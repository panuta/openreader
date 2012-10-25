# -*- encoding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET

from accounts.forms import EmailAuthenticationForm

from domain.models import UserOrganization

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)


@require_GET
def view_user_home(request):
    if not request.user.is_authenticated():
        return render(request, 'index.html')

    if request.user.is_superuser:
        return redirect('/management/')

    user_organizations = UserOrganization.objects.filter(user=request.user, is_active=True).order_by('-is_default', 'created')
    if user_organizations:
        user_organization = user_organizations[0]
    else:
        return redirect('view_user_welcome')
    
    return redirect('view_organization_front', organization_slug=user_organization.organization.slug)


@require_GET
@login_required
def view_user_welcome(request):
    if UserOrganization.objects.filter(user=request.user, is_active=True).count():
        return redirect('view_user_home')
    
    return render(request, 'accounts/user_welcome.html', {})
