
from publisher.models import Publication

def constants(request):
    """
    Adds general OpenReader constants

    """

    dict = {}
    for key in Publication.PUBLISH_STATUS.keys():
        dict['PUBLISH_STATUS_%s' % key] = Publication.PUBLISH_STATUS[key]

    return dict