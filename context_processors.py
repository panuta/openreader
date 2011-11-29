
from publisher.models import Publication

def constants(request):
    """
    Adds general OpenReader constants

    """

    dict = {}
    for key in Publication.STATUS.keys():
        dict['PUBLICATION_STATUS_%s' % key] = Publication.STATUS[key]

    return dict