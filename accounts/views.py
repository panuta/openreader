from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import UserPublisher

@login_required
def view_user_welcome(request):
    return render(request, 'user_welcome.html', {})