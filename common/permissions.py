
from publication.models import *

def can(user, action, object):
    return _dispatch(user, action, object)

def _dispatch(user, action, object):
    is_permit = True
    
    for action_name in action.split('+'):
        try:
            is_permit = is_permit & getattr(object, 'can_%s' % action_name)(user)
        except AttributeError:
            return False
    return is_permit