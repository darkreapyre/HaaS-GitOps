import boto3
try:
    import requests #Python3
except ImportError:
    from botocore.vendored import requests #Python2
import logging
import base64
import os
import shutil
from zipfile import ZipFile
try:
    from cStringIO import StringIO #Python2
except ImportError:
    from io import BytesIO #Python3
try:
    from urlparse import urlparse #Python2
except ImportError:
    import urllib.parse as urlparse #Python3
import base64

# Set to False to allow self-signed/invalid ssl certificates
verify = False

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers[0].setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)
params = None
s3_client = boto3.client('s3')


def get_members(zip):
    parts = []
    # get all the path prefixes
    for name in zip.namelist():
        # only check files (not directories)
        if not name.endswith('/'):
            # keep list of path elements (minus filename)
            parts.append(name.split('/')[:-1])
    # now find the common path prefix (if any)
    prefix = os.path.commonprefix(parts)
    if prefix:
        # re-join the path elements
        prefix = '/'.join(prefix) + '/'
    # get the length of the common prefix
    offset = len(prefix)
    # now re-set the filenames
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        # only check files (not directories)
        if len(name) > offset:
            # remove the common prefix
            zipinfo.filename = name[offset:]
            yield zipinfo


def lambda_handler(event, context):
    params = None
    logger.info('Event %s', event)
    OAUTH_token = event['context']['git-token']
    OutputBucket = event['context']['output-bucket']
    headers = {'Authorization': 'token '+OAUTH_token}
    branch = 'master'

    # GitHub specific hostflavor
    archive_url = event['body-json']['repository']['archive_url']
    owner = event['body-json']['repository']['owner']['login']
    name = event['body-json']['repository']['name']

    # replace the code archive download and branch reference placeholders
    branch_name = event['body-json']['ref'].replace('refs/heads/', '')
    archive_url = archive_url.replace('{archive_format}', 'zipball').replace('{/ref}', '/' + branch_name)

    # download the code archive via archive url
    logger.info('Downloading archive from %s' % archive_url)
    r = requests.get(archive_url, verify=verify, headers=headers, params=params)
    f = BytesIO(r.content)
    zip = ZipFile(f)
    path = '/tmp/code'
    zipped_code = '/tmp/zipped_code'
    try:
        shutil.rmtree(path)
        os.remove(zipped_code + '.zip')
    except:
        pass
    finally:
        os.makedirs(path)
    # Write to /tmp dir without any common preffixes
    zip.extractall(path, get_members(zip))

    # Create zip from /tmp dir without any common preffixes
    s3_archive_file = "%s/%s/%s/%s.zip" % (owner, name, branch, name)
    shutil.make_archive(zipped_code, 'zip', path)
    logger.info("Uploading zip to S3://%s/%s" % (OutputBucket, s3_archive_file))
    s3_client.upload_file(zipped_code + '.zip', OutputBucket, s3_archive_file)
    logger.info('Upload Complete')
