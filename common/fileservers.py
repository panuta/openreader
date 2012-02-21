from time import time

from django.conf import settings

def generate_download_url(server, publication):

    if server.server_type == 'nginx':
        return _generate_nginx_download_url(server, publication)

    elif server.server_type == 's3':
        return _generate_s3_download_url(server, publication)

    elif server.server_type == 'intranet':
        return _generate_intranet_download_url(server, publication)

    elif server.server_type == 'xsendfile':
        return _generate_xsendfile_download_url(server, publication)
    
    return None

def _generate_nginx_download_url(server, publication):
    """
    Serve file using nginx's HttpSecureLinkModule
    """
    path = publication.get_download_rel_path()
    expire_timestamp = int(time()) + settings.DOWNLOAD_LINK_EXPIRE_IN * 60

    import md5, base64
    m = md5.new()
    m.update('%s/%s%s' % (server.key, path, expire_timestamp))
    hash = base64.urlsafe_b64encode(m.digest())
    hash = hash.replace('=', '')
    hash = hash.replace('+', '-')
    hash = hash.replace('/', '_')
    return 'http://%s%s%s?st=%s&e=%s' % (server.server_address, server.prefix, path, hash, expire_timestamp)

def _generate_s3_download_url(server, publication):
    """
    Serve file using Amazon S3 and Amazon CloudFront
    """

    # TODO

    return ''

def _generate_intranet_download_url(server, publication):
    """
    Serve file using an unprotected file server (Should be used in a closed environment)
    """

    path = publication.get_download_rel_path()
    return 'http://%s%s%s' % (server.server_address, server.prefix, path)

def _generate_xsendfile_download_url(server, publication):
    """
    Serve file using Apache's xsendfile module
    """

    # TODO

    return ''
