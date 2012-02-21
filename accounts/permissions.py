from models import *

class UserPermission(object):

    @staticmethod
    def view_organization(user, organization, parameters):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return False

        return True
    
    @staticmethod
    def manage_user(user, organization, parameters):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return False
        
        if user_organization.is_admin:
            return True
        
        return OrganizationAdminPermission.objects.get(code_name='manage_user') in user_organization.admin_permissions.all()
    
    @staticmethod
    def manage_group(user, organization, parameters):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return False
        
        if user_organization.is_admin:
            return True
        
        return OrganizationAdminPermission.objects.get(code_name='manage_group') in user_organization.admin_permissions.all()
    
    @staticmethod
    def manage_shelf(user, organization, parameters):
        try:
            user_organization = UserOrganization.objects.get(user=user, organization=organization, is_active=True)
        except UserOrganization.DoesNotExist:
            return False
        
        if user_organization.is_admin:
            return True
        
        return OrganizationAdminPermission.objects.get(code_name='manage_shelf') in user_organization.admin_permissions.all()
