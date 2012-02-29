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
    parameters = extract_parameters(server.parameters)

    path = parameters.get('prefix') + publication.get_download_rel_path()
    expire_timestamp = int(time()) + settings.DOWNLOAD_LINK_EXPIRE_IN * 60

    import hashlib, base64
    m = hashlib.md5()
    m.update('%s%s%s' % (parameters.get('secret'), path, expire_timestamp))
    hash = base64.urlsafe_b64encode(m.digest())
    hash = hash.replace('=', '')
    hash = hash.replace('+', '-')
    hash = hash.replace('/', '_')
    return 'http://%s%s?st=%s&e=%s' % (server.server_address, path, hash, expire_timestamp)

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

    if server.server_type == 'sftp':
        return _upload_to_sftp_server(server, publication)

    elif server.server_type == 's3':
        return _upload_to_s3_server(server, publication)

    return False

def _upload_to_sftp_server(server, publication):
    parameters = extract_parameters(server.parameters)
    
    from storages.backends.sftpstorage import SFTPStorage
    root_path = '%s%s' % (parameters.pop('root_path'), publication.get_parent_folder())
    SFTPStorage(server.server_address, root_path, parameters).save('%s.%s' % (publication.uid, publication.file_ext), publication.uploaded_file)

    return True

def _upload_to_s3_server(server, publication):
    pass
