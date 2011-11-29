from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import ugettext_lazy as _

from accounts.forms import *
from accounts.models import *

from publisher.models import UserPublisher

def auth_login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

def view_user_welcome(request):
    if UserPublisher.objects.filter(user=request.user).count() != 0:
        raise Http404
    
    if request.user.is_superuser:
        return redirect('/management/')
    
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