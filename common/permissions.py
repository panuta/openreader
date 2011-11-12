
from publication.models import *

def can(user, action, object):
    return _dispatch(user, action, object)

def _dispatch(user, action, object):
    try:
        if isinstance(object, Publisher):
            return getattr(object, 'can_%s' % action)(user)
    except AttributeError:
        return False
    return False