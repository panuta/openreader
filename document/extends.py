
class UserInvitationExtension():
    TEMPLATE_NAME = {
        'user_invite':'document/extends/organization_user_invite.html'
    }
    
    def after_user_invited():
        pass