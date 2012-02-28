from time import time

from django.conf import settings

from common.utilities import extract_parameters

# Generate download URL
# ############################################################################################################################################

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

# Upload to server
# ############################################################################################################################################

def upload_to_server(server, publication):

    if server.server_type == 'nginx':
        return _upload_to_nginx_server(server, publication)

    elif server.server_type == 's3':
        return _upload_to_s3_server(server, publication)

    elif server.server_type == 'intranet':
        return _upload_to_intranet_server(server, publication)

    elif server.server_type == 'xsendfile':
        return _upload_to_xsendfile_server(server, publication)
    
    return None

from django.db import models
class PublicationOnSFTP(models.Model):
    upload_file = models.FileField(storage=sftp_storage, upload_to='/web/openreader/www/')


def _upload_to_nginx_server(server, publication):
    parameters = extract_parameters(server.parameters)

    if parameter.get('location') == 'remote':
        # Upload via SFTP

        from storages.backends.sftpstorage import SFTPStorage

        model = PublicationOnSFTP()
        model.upload_to = publication.uploaded_file
        model.upload_to.save()

    elif parameter.get('location') == 'remote':
        pass

def _upload_to_s3_server(server, publication):
    pass

def _upload_to_intranet_server(server, publication):
    pass

def _upload_to_xsendfile_server(server, publication):
    pass
