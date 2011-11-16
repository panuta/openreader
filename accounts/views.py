from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import *
from accounts.models import *

def login(request):
    from django.contrib.auth.views import login
    return login(request, authentication_form=EmailAuthenticationForm)

def view_user_welcome(request):
    welcome_contact_email = settings.WELCOME_CONTACT_EMAIL
    return render(request, 'accounts/user_welcome.html', {'welcome_contact_email':welcome_contact_email})

@login_required
def view_my_profile(request):
    return render(request, 'accounts/my_profile.html', {})

@login_required
def view_my_account(request):
    return render(request, 'accounts/my_account.html', {})