# Create your views here.

from django.shortcuts import get_object_or_404, redirect, render

def view_homepage(request):
	if request.user.is_authenticated():
		return redirect('view_dashboard')

	return render(request, 'homepage.html', {})