MODULE_NAME = 'Books'
MODULE_CODE = 'book'
MODULE_NUMBER = 101

FRONT_PAGE_URL_NAME = 'view_publisher_books' # Combine with publisher url -> /publisher/1/books

def get_publication_title(publication):
    return '%s' % (publication.title)