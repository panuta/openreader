from models import *

class UserPermission(object):

    @staticmethod
    def view_publication(user, organization, parameters):
        return get_publication_access(user, parameters['publication']) >= SHELF_ACCESS['VIEW_ACCESS']
    
    @staticmethod
    def edit_publication(user, organization, parameters):
        return get_publication_access(user, parameters['publication']) >= SHELF_ACCESS['PUBLISH_ACCESS']

    @staticmethod
    def view_shelf(user, organization, parameters):
        return get_shelf_access(user, parameters['shelf']) >= SHELF_ACCESS['VIEW_ACCESS']
    
    @staticmethod
    def upload_shelf(user, organization, parameters):
        return get_shelf_access(user, parameters['shelf']) == SHELF_ACCESS['PUBLISH_ACCESS']


# Publication
############################################################################################

def get_publication_access(user, publication):
    max_access_level = SHELF_ACCESS['NO_ACCESS']
    for shelf in publication.shelves.all():
        access_level = get_shelf_access(user, shelf)
        if access_level > max_access_level: max_access_level = access_level
    
    return max_access_level

# Organization Shelf
############################################################################################

def get_viewable_shelves(user, organization):
    try:
        user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
    except UserOrganization.DoesNotExist:
        return []

    if user_organization.is_admin:
        return OrganizationShelf.objects.filter(organization=organization).order_by('name')

    shelves = []
    for shelf in OrganizationShelf.objects.filter(organization=organization).order_by('name'):
        if get_shelf_access(user, shelf) >= SHELF_ACCESS['VIEW_ACCESS']:
            shelves.append(shelf)

    return shelves

def get_shelf_access(user, shelf):
    try:
        user_organization = UserOrganization.objects.get(user=user, organization=shelf.organization, is_active=True)
    except UserOrganization.DoesNotExist:
        return SHELF_ACCESS['NO_ACCESS']

    if not user_organization:
        return SHELF_ACCESS['NO_ACCESS']

    if user_organization.is_admin:
        return SHELF_ACCESS['PUBLISH_ACCESS']

    max_access_level = SHELF_ACCESS['NO_ACCESS']

    try:
        access_level = OrganizationShelfPermission.objects.get(shelf=shelf).access_level
        max_access_level = access_level if max_access_level < access_level else max_access_level
    except OrganizationShelfPermission.DoesNotExist:
        pass
    
    if max_access_level == SHELF_ACCESS['PUBLISH_ACCESS']: return SHELF_ACCESS['PUBLISH_ACCESS'] # No need to query further

    for user_group in UserGroup.objects.filter(user_organization=user_organization):
        try:
            access_level = GroupShelfPermission.objects.get(shelf=shelf, group=user_group.group).access_level
            max_access_level = access_level if max_access_level < access_level else max_access_level
        except GroupShelfPermission.DoesNotExist:
            pass
    
    if max_access_level == SHELF_ACCESS['PUBLISH_ACCESS']: return SHELF_ACCESS['PUBLISH_ACCESS'] # No need to query further

    try:
        access_level = UserShelfPermission.objects.get(shelf=shelf, user=user).access_level
        max_access_level = access_level if max_access_level < access_level else max_access_level
    except UserShelfPermission.DoesNotExist:
        pass
    
    return max_access_level