ROLE_CHOICES = (('organization_admin', 'Organization Admin'), ('organization_staff', 'Organization Staff'), ('organization_user', 'Organization User'))

"""
def can(user, action, organization, parameters={}):
    if ',' in action:
        actions = action.split(',')
        use_AND = True

    elif '+' in action:
        actions = action.split('+')
        use_AND = False

    else:
        actions = (action, )

    permission_list = []
    for action_name in actions:
        permission_list.append(user.get_profile().check_permission(action_name, organization, parameters))
    
    result = permission_list[0]

    for permission in permission_list[1:]:
        if use_AND:
            result = result and permission
        else:
            result = result or permission
    
    return result
"""

from django.utils.importlib import import_module

PERM_APPS = ('accounts', 'document')

def can(user, perm_name, organization, parameters={}):
    for app_name in PERM_APPS:
        try:
            mod = import_module('%s.permissions' % app_name)
        except ImportError, e:
            pass
        except ValueError, e:
            pass
        else:
            try:
                cls = getattr(mod, 'UserPermission')
                return getattr(cls, perm_name)(user, organization, parameters)
            except AttributeError:
                pass
    
    return False