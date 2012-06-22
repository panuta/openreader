from domain.models import UserOrganization, OrganizationAdminPermission, OrganizationShelf, GroupShelfPermission, UserGroup, UserShelfPermission, OrganizationShelfPermission

ROLE_CHOICES = (('organization_admin', 'Organization Admin'), ('organization_staff', 'Organization Staff'), ('organization_user', 'Organization User'))

def get_backend(request):
    cached_backend = request.session.get('perm_backend', None)

    if not cached_backend:
        perm_backend = DefaultUserPermissionBackend()
        request.session['perm_backend'] = cached_backend = perm_backend

    return cached_backend


class DefaultUserPermissionBackend(object):

    @staticmethod
    def can_view_organization(user, organization, parameters={}):
        if user.is_superuser:
            return True

        try:
            UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return False

        return True

    # User Admin Permissions

    @staticmethod
    def can_manage_user(user, organization, parameters={}):
        if user.is_superuser:
            return True
            
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
            user_groups = UserGroup.objects.filter(user_organization=user_organization)
            group_permissions = []
            for group in user_groups:
                group_permissions.extend(group.group.admin_permissions.all())

        except UserOrganization.DoesNotExist:
            return False

        if user_organization.is_admin:
            return True

        return OrganizationAdminPermission.objects.get(code_name='manage_user') in group_permissions

    @staticmethod
    def can_manage_group(user, organization, parameters={}):
        if user.is_superuser:
            return True
            
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
            user_groups = UserGroup.objects.filter(user_organization=user_organization)
            group_permissions = []
            for group in user_groups:
                group_permissions.extend(group.group.admin_permissions.all())
        except UserOrganization.DoesNotExist:
            return False

        if user_organization.is_admin:
            return True

        return OrganizationAdminPermission.objects.get(code_name='manage_group') in group_permissions

    @staticmethod
    def can_manage_shelf(user, organization, parameters={}):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
            user_groups = UserGroup.objects.filter(user_organization=user_organization)
            group_permissions = []
            for group in user_groups:
                group_permissions.extend(group.group.admin_permissions.all())
        except UserOrganization.DoesNotExist:
            return False

        if user_organization.is_admin:
            return True

        return OrganizationAdminPermission.objects.get(code_name='manage_shelf') in group_permissions

    # Publication Permissions

    @staticmethod
    def can_view_publication(user, organization, parameters={}):
        return DefaultUserPermissionBackend.get_publication_access(user, parameters['publication']) >= OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS']

    @staticmethod
    def can_edit_publication(user, organization, parameters={}):
        return DefaultUserPermissionBackend.get_publication_access(user, parameters['publication']) >= OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS']

    @staticmethod
    def can_view_shelf(user, organization, parameters={}):
        return DefaultUserPermissionBackend.get_shelf_access(user, parameters['shelf']) >= OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS']

    @staticmethod
    def can_upload_shelf(user, organization, parameters={}):
        return DefaultUserPermissionBackend.get_shelf_access(user, parameters['shelf']) == OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS']

    # Publication

    @staticmethod
    def get_publication_access(user, publication):
        max_access_level = OrganizationShelf.SHELF_ACCESS['NO_ACCESS']
        for shelf in publication.shelves.all():
            access_level = DefaultUserPermissionBackend.get_shelf_access(user, shelf)
            if access_level > max_access_level: max_access_level = access_level

        return max_access_level

    # Shelf

    @staticmethod
    def get_viewable_shelves(user, organization):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return []

        if user_organization.is_admin:
            return OrganizationShelf.objects.filter(organization=organization).order_by('name')

        shelves = []
        for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
            if DefaultUserPermissionBackend.get_shelf_access(user, shelf) >= OrganizationShelf.SHELF_ACCESS['VIEW_ACCESS']:
                shelves.append(shelf)

        return shelves

    @staticmethod
    def get_uploadable_shelves(user, organization):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return []

        if user_organization.is_admin:
            return OrganizationShelf.objects.filter(organization=organization).order_by('name')

        shelves = []
        for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
            if DefaultUserPermissionBackend.get_shelf_access(user, shelf) >= OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS']:
                shelves.append(shelf)

        return shelves

    @staticmethod
    def get_shelf_access(user, shelf):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=shelf.organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return OrganizationShelf.SHELF_ACCESS['NO_ACCESS']

        if user_organization.is_admin:
            return OrganizationShelf.SHELF_ACCESS['PUBLISH_ACCESS']

        # User Access Level
        try:
            return UserShelfPermission.objects.get(shelf=shelf, user=user).access_level
        except UserShelfPermission.DoesNotExist:
            pass

        # Group Access Level
        found_group_access = False
        max_group_access_level = OrganizationShelf.SHELF_ACCESS['NO_ACCESS']
        for group in user_organization.groups.all():
            try:
                access_level = GroupShelfPermission.objects.get(shelf=shelf, group=group).access_level
                max_group_access_level = access_level if max_group_access_level < access_level else max_group_access_level
                found_group_access = True
            except GroupShelfPermission.DoesNotExist:
                pass

        if found_group_access:
            return max_group_access_level

        # Organization Access Level
        try:
            return OrganizationShelfPermission.objects.get(shelf=shelf).access_level
            max_access_level = access_level if max_access_level < access_level else max_access_level
        except OrganizationShelfPermission.DoesNotExist:
            pass

        return OrganizationShelf.SHELF_ACCESS['NO_ACCESS']
