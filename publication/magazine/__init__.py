# -*- encoding: utf-8 -*-

MODULE_NAME = 'นิตยสาร'
MODULE_CODE = 'magazine'
MODULE_NUMBER = 102

FRONT_PAGE_URL_NAME = 'view_magazines'

def get_publication_title(publication):
    return '%s - %s' % (publication.magazineissue.magazine.title, publication.title)
