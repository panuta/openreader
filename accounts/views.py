from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from forms import *
from models import *

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

@login_required
def view_user_home(request):
    if request.user.is_superuser:
        return redirect('/management/')
    
    try:
        user_organization = UserOrganization.objects.get(user=request.user, is_default=True)
    except UserOrganization.DoesNotExist:
        if UserOrganization.objects.filter(user=request.user).count() == 0:
            return redirect('view_user_welcome')
        else:
            # If a user does not set any default publisher, pick the first one
            user_organization = UserOrganization.objects.filter(user=request.user).order_by('created')[0]
    
    if settings.SITE_TYPE == 'document':
        return redirect('view_document_front', organization_id=user_organization.organization.id)
    
    if settings.SITE_TYPE == 'publisher':
        return redirect('view_publisher_front', organization_id=user_organization.organization.id)

def view_user_welcome(request):
    if UserOrganization.objects.filter(user=request.user).count() != 0:
        raise Http404
    
    welcome_contact_email = settings.WELCOME_CONTACT_EMAIL
    return render(request, 'accounts/user_welcome.html', {'welcome_contact_email':welcome_contact_email})

@login_required
def view_my_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            user_profile = request.user.get_profile()
            user_profile.first_name = form.cleaned_data['first_name']
            user_profile.last_name = form.cleaned_data['last_name']
            user_profile.save()

            return redirect('view_my_profile')
    else:
        form = UserProfileForm(initial=request.user.get_profile().__dict__)

    return render(request, 'accounts/my_profile.html', {'form':form})

@login_required
def view_my_account(request):
    return render(request, 'accounts/my_account.html', {})

@login_required
def change_my_account_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_my_account')

    else:
        form = PasswordChangeForm(user=request.user)
    
    return render(request, 'accounts/my_account_change_password.html', {'form':form})