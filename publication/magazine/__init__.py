MODULE_NAME = 'Magazines'
MODULE_CODE = 'magazine'
MODULE_NUMBER = 102

FRONT_PAGE_URL_NAME = 'view_publisher_magazines'

def get_publication_title(publication):
    return '%s - %s' % (publication.magazineissue.magazine.title, publication.title)
