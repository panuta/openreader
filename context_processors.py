from django.conf import settings

from publication.models import Publication

def constants(request):
    """
    Adds general OpenReader constants

    """

    dict = {}
    for key in Publication.STATUS.keys():
        dict['PUBLICATION_STATUS_%s' % key] = Publication.STATUS[key]
    
    dict['SITE_TYPE'] = settings.SITE_TYPE

    return dict