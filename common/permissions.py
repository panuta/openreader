ROLE_CHOICES = (('publisher_admin', 'Publisher Admin'), ('publisher_staff', 'Publisher Staff'), ('publisher_user', 'Publisher User'))

def can(user, action, object):
    return _dispatch(user, action, object)

def _dispatch(user, action, object):
    action_permits = []

    if ',' in action:
        actions = action.split(',')
    elif '+' in action:
        actions = action.split('+')
    else:
        actions = (action, )
    
    for action_name in actions:
        try:
            action_permits.append(getattr(object, 'can_%s' % action_name)(user))
        except AttributeError:
            action_permits.append(False)
    
    result = action_permits[0]

    for action_permit in action_permits[1:]:
        if ',' in action:
            result = result or action_permit
        elif '+' in action:
            result = result or action_permit
    
    return result
