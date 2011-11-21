
def get_publication_title(publication):
    return '%s - %s' % (publication.magazineissue.magazine.title, publication.title)