"""
Module structure
- 'module_name' folder in publication app
- 'module_name' folder in templates
"""

def get_publication_module(module_name, sub_module=''):
    if sub_module: sub_module = '.' + sub_module
    try:
        return __import__('publication.%s%s' % (module_name, sub_module), fromlist=['publication'])
    except:
        import sys
        print sys.exc_info()
        return None

