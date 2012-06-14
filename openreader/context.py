from django.conf import settings

def constants(request):
    """
    Adds general OpenReader constants
    """

    return {
        'settings': settings,
        'MAX_PUBLICATION_FILE_SIZE':settings.MAX_PUBLICATION_FILE_SIZE,
        'MAX_PUBLICATION_FILE_SIZE_TEXT':settings.MAX_PUBLICATION_FILE_SIZE_TEXT,
    }