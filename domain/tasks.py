import datetime
import logging, sys, traceback

from celery.task import task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from common.utilities import format_abbr_date


logger = logging.getLogger(settings.OPENREADER_LOGGER)


@task(name='tasks.generate_thumbnails')
def generate_thumbnails(publication_uid):
    from common.thumbnails import generate_thumbnails, delete_thumbnails
    from domain.models import Publication

    try:
        publication = Publication.objects.get(uid=publication_uid)
    except Publication.DoesNotExist:
        logger.critical(traceback.format_exc(sys.exc_info()[2]))
        return None

    try:
        if publication.has_thumbnail:
            delete_thumbnails(publication)

        publication.has_thumbnail = generate_thumbnails(publication)
    except:
        publication.has_thumbnail = False
        logger.error(traceback.format_exc(sys.exc_info()[2]))

    publication.is_processing = False
    publication.save()

    return publication_uid


@task(name='tasks.prepare_publication')
def prepare_publication(publication_uid):

    from common.thumbnails import generate_thumbnails, delete_thumbnails
    from domain.models import Publication

    try:
        publication = Publication.objects.get(uid=publication_uid)
    except:
        logger.critical(traceback.format_exc(sys.exc_info()[2]))
        return None

    # Generate thumbnails

    try:
        if publication.has_thumbnail:
            delete_thumbnails(publication)

        publication.has_thumbnail = generate_thumbnails(publication)
    except:
        publication.has_thumbnail = False
        logger.error(traceback.format_exc(sys.exc_info()[2]))
    
    # Upload publication
    
    from common.fileservers import upload_to_server
    from domain.models import OrganizationUploadServer

    for server in OrganizationUploadServer.objects.filter(organization=publication.organization):
        try:
            upload_to_server(server, publication)
        except:
            logger.error(traceback.format_exc(sys.exc_info()[2]))

    publication.is_processing = False
    publication.save()

    return publication_uid


@task(name='tasks.send_notification_email_to_decide_on_first_month')
def send_notification_email_to_decide_on_first_month():
    from domain.models import Organization, UserOrganization
    notify_day = datetime.date.today()-datetime.timedelta(days=21)
    organizations = Organization.objects.filter(created__year=notify_day.year, created__month=notify_day.month, created__day=notify_day.day)

    for organization in organizations:
        invoice = organization.get_latest_invoice()

        html_email_body = render_to_string('organization/emails/decide_on_first_month.html', {
            'organization': organization, 
            'settings': settings,
            'expire_date': invoice.end_date + datetime.timedelta(days=1),
        })
        text_email_body = strip_tags(html_email_body)
        subject = 'Decision for %s on Openreader' % organization.name
        send_to_emails = list(UserOrganization.objects.filter(organization=organization, is_admin=True).values_list('user__email', flat=True))
        
        if organization.email not in send_to_emails:
            send_to_emails.append(organization.email)

        msg = EmailMultiAlternatives(
            subject, 
            text_email_body, 
            settings.EMAIL_ADDRESS_NO_REPLY, 
            send_to_emails
        )
        msg.attach_alternative(html_email_body, "text/html")

        try:
            msg.send()
            print True
        except:
            import sys
            print sys.exc_info()


@task(name='tasks.send_notification_email_to_pay_service')
def send_notification_email_to_pay_service():
    from domain.models import Organization, UserOrganization
    organizations = Organization.objects.all()

    for organization in organizations:
        invoice = organization.get_latest_invoice()

        if settings.TEST_PAYMENT_REMIND_EVERY_HOUR:
            diff_date_days = datetime.datetime.now().hour - invoice.attempt
        else:
            diff_date_days = (datetime.date.today() - invoice.end_date).days
        if diff_date_days in [1, 4, 7, 10, 13, 16]:
            html_email_body = render_to_string('organization/emails/notify_payment.html', {
                'organization': organization,
                'settings': settings,
                'invoice': invoice,
            })
            text_email_body = strip_tags(html_email_body)
            subject = 'Invoice for %s on Openreader from %s to %s' % (organization.name, format_abbr_date(invoice.start_date), format_abbr_date(invoice.end_date))
            send_to_emails = list(UserOrganization.objects.filter(organization=organization, is_admin=True).values_list('user__email', flat=True))

            if organization.email not in send_to_emails:
                send_to_emails.append(organization.email)

            msg = EmailMultiAlternatives(
                subject,
                text_email_body,
                settings.EMAIL_ADDRESS_NO_REPLY,
                send_to_emails
            )
            msg.attach_alternative(html_email_body, "text/html")

            try:
                msg.send()
                print True
            except:
                import sys
                print sys.exc_info()
        elif diff_date_days == 17:
            from domain import functions as domain_functions
            domain_functions.remove_organization(organization)