import datetime
import logging, sys, traceback

from celery.task import task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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
        html_email_body = render_to_string('organization/emails/decide_on_first_month.html', {
            'organization': organization, 
            'settings': settings,
        })
        text_email_body = strip_tags(html_email_body)
        subject = 'Dicision for %s on Openreader' % organization.name
        send_to_emails = UserOrganization.objects.filter(organization=organization, is_admin=True).values_list('user__email', flat=True)
        
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
