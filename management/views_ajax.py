# -*- encoding: utf-8 -*-
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from common.shortcuts import response_json_success, response_json_error

from accounts.permissions import get_backend as get_permission_backend
from domain.models import OrganizationInvitation

@require_POST
@login_required
def ajax_resend_organization_invitation(request, invitation_id):
    if not request.user.is_superuser:
        raise Http404

    if request.is_ajax():
        invitation = get_object_or_404(OrganizationInvitation, pk=invitation_id)

        if invitation.send_invitation_email():
            invitation.created = datetime.now()
            invitation.save()
            return response_json_success()
        else:
            return response_json_error('send-invitation-failed')
    else:
        raise Http404


@require_POST
@login_required
def ajax_cancel_organization_invitation(request, invitation_id):
    if not request.user.is_superuser:
        raise Http404

    if request.is_ajax():
        invitation = get_object_or_404(OrganizationInvitation, pk=invitation_id)
        invitation.delete()

        messages.success(request, u'เพิกถอนคำขอบริษัทเรียบร้อย')
        return response_json_success({'redirect_url':reverse('view_organizations_invited')})
    else:
        raise Http404
