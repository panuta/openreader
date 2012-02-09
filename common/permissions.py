ROLE_CHOICES = (('organization_admin', 'Organization Admin'), ('organization_staff', 'Organization Staff'), ('organization_user', 'Organization User'))

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