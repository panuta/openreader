import base64
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from api.models import *
from accounts.models import *

from httpauth import *

from datetime import datetime, timedelta
import md5

def token_expired(token):
    try:
        data = Token.objects.get(token=token)
    except (Token.DoesNotExist):
        return False
    
    expired = data.expired > datetime.now()
    if expired:
        data.delete()
    
    return expired
 
#############################################################################
#
def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
This is a helper function used by both 'logged_in_or_basicauth' and
'has_perm_or_basicauth' that does the nitty of determining if they
are already logged in or if they have provided proper http-authorization
and returning the view if all goes well, otherwise responding with a 401.
"""
    # token = request.GET.get('token')
    # if (token):
    #     if token_expired(token):
    #         return HttpResponse(simplejson.dumps({'error': 'token expired'}))
    
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)
 
    # They are not logged in. See if they provided login credentials
    #
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        print auth
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                email_user = User.objects.filter(email=uname)
                if not email_user:
                    username = uname
                else:
                    username = email_user[0].email

                user = authenticate(email=username, password=passwd)
                if user is not None:
                    if user.is_active:
                        #login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)
 
    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response

import re

def determine_device(request):

    device = {}

    ua = request.META.get('HTTP_USER_AGENT', '').lower()
    
    if ua.find("iphone") > 0:
        device['type'] = "iphone" + re.search("iphone os (\d)", ua).groups(0)[0]
        
    if ua.find("ipad") > 0:
        device['type'] = "ipad"
        
    if ua.find("android") > 0:
        device['type'] = "android" + re.search("android (\d\.\d)", ua).groups(0)[0].translate(None, '.')
        
    if ua.find("blackberry") > 0:
        device['type'] = "blackberry"
        
    if ua.find("windows phone os 7") > 0:
        device['type'] = "winphone7"
        
    if ua.find("iemobile") > 0:
        device['type'] = "winmo"
        
    if not device:          # either desktop, or something we don't care about.
        device['type'] = "baseline"
    
    # spits out device names for CSS targeting, to be applied to <html> or <body>.
    device['classes'] = " ".join(v for (k,v) in device.items())
    
    return {'device': device }

#############################################################################
#
def logged_in_or_basicauth(realm = ""):
    """
A simple decorator that requires a user to be logged in. If they are not
logged in the request is examined for a 'authorization' header.
If the header is present it is tested for basic authentication and
the user is logged in with the provided credentials.
If the header is not present a http 401 is sent back to the
requestor to provide credentials.
The purpose of this is that in several django projects I have needed
several specific views that need to support basic authentication, yet the
web site as a whole used django's provided authentication.
The uses for this are for urls that are access programmatically such as
by rss feed readers, yet the view requires a user to be logged in. Many rss
readers support supplying the authentication credentials via http basic
auth (and they do NOT support a redirect to a form where they post a
username/password.)
Use is simple:
@logged_in_or_basicauth
def your_view:
...
You can provide the name of the realm to ask for authentication within.
"""
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator
 
#############################################################################
#
def has_perm_or_basicauth(perm, realm = ""):
    """
This is similar to the above decorator 'logged_in_or_basicauth'
except that it requires the logged in user to have a specific
permission.
Use:
@logged_in_or_basicauth('asforums.view_forumcollection')
def your_view:
...
"""
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.has_perm(perm),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator