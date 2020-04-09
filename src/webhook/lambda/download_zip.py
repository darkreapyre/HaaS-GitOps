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
    # # temp_archive = '/tmp/archive.zip'
    # # Identify git host flavour
    # hostflavour = 'generic'
    # if 'X-Hub-Signature' in event['params']['header'].keys():
    #     hostflavour = 'githubent'
    # elif 'X-Gitlab-Event' in event['params']['header'].keys():
    #     hostflavour = 'gitlab'
    # elif 'User-Agent' in event['params']['header'].keys():
    #     if event['params']['header']['User-Agent'].startswith('Bitbucket-Webhooks'):
    #         hostflavour = 'bitbucket'
    #     elif event['params']['header']['User-Agent'].startswith('GitHub-Hookshot'):
    #         hostflavour = 'github'
    #     elif 'Bitbucket-' in event['params']['header']['User-Agent']:
    #         hostflavour = 'bitbucket-server'
    # elif event['body-json']['publisherId'] == 'tfs':
    #     hostflavour='tfs'

    # headers = {}
    headers = {'Authorization': 'token '+OAUTH_token}
    branch = 'master'
    # if hostflavour == 'githubent':
    #     archive_url = event['body-json']['repository']['archive_url']
    #     owner = event['body-json']['repository']['owner']['name']
    #     name = event['body-json']['repository']['name']
    #     # replace the code archive download and branch reference placeholders
    #     archive_url = archive_url.replace('{archive_format}', 'zipball').replace('{/ref}', '/master')
    #     # add access token information to archive url
    #     archive_url = archive_url+'?access_token='+OAUTH_token
    # elif hostflavour == 'github':
    #     archive_url = event['body-json']['repository']['archive_url']
    #     owner = event['body-json']['repository']['owner']['login']
    #     name = event['body-json']['repository']['name']
    #     # replace the code archive download and branch reference placeholders
    #     branch_name = event['body-json']['ref'].replace('refs/heads/', '')
    #     archive_url = archive_url.replace('{archive_format}', 'zipball').replace('{/ref}', '/' + branch_name)
    #     # add access token information to archive url
    #     archive_url = archive_url+'?access_token='+OAUTH_token
    # elif hostflavour == 'gitlab':
    #     #https://gitlab.com/jaymcconnell/gitlab-test-30/repository/archive.zip?ref=master
    #     archive_root = event['body-json']['project']['http_url'].strip('.git')
    #     project_id = event['body-json']['project_id']
    #     branch = event['body-json']['ref'].replace('refs/heads/', '')
    #     archive_url = "https://gitlab.com/api/v4/projects/{}/repository/archive.zip".format(project_id)
    #     params = {'private_token': OAUTH_token, 'sha': branch}

    #     owner = event['body-json']['project']['namespace']
    #     name = event['body-json']['project']['name']

    # elif hostflavour == 'bitbucket':
    #     branch = event['body-json']['push']['changes'][0]['new']['name']
    #     archive_url = event['body-json']['repository']['links']['html']['href']+'/get/' + branch + '.zip'
    #     owner = event['body-json']['repository']['owner']['username']
    #     name = event['body-json']['repository']['name']
    #     r = requests.post('https://bitbucket.org/site/oauth2/access_token', data={'grant_type': 'client_credentials'}, auth=(event['context']['oauth-key'], event['context']['oauth-secret']))
    #     if 'error' in r.json().keys():
    #         logger.error('Could not get OAuth token. %s: %s' % (r.json()['error'], r.json()['error_description']))
    #         raise Exception('Failed to get OAuth token')
    #     headers['Authorization'] = 'Bearer ' + r.json()['access_token']
    # elif hostflavour == 'tfs':
    #     archive_url = event['body-json']['resourceContainers']['account']['baseUrl'] + 'DefaultCollection/' + event['body-json']['resourceContainers']['project']['id'] + '/_apis/git/repositories/' + event['body-json']['resource']['repository']['id'] + '/items'
    #     owner = event['body-json']['resource']['pushedBy']['displayName']
    #     name = event['body-json']['resource']['repository']['name']
    #     pat_in_base64 = base64.encodestring(':%s' % event['context']['git-token'])
    #     headers['Authorization'] = 'Basic %s' % pat_in_base64
    #     headers['Authorization'] = headers['Authorization'].replace('\n','')
    #     headers['Accept'] = 'application/zip'
    # elif hostflavour == 'bitbucket-server':
    #     clone_urls = event['body-json']['repository']['links']['clone']
    #     http_clone_url = None
    #     for clone_url in clone_urls:
    #         if clone_url.get('name') == "http":
    #             http_clone_url = clone_url.get('href')
    #     if http_clone_url is None:
    #         raise Exception("Could not find http clone url from the webhook payload")

    #     if len(event['body-json']['changes']) != 1:
    #         raise Exception("Could not handle the number of changes")
    #     change = event['body-json']['changes'][0]
    #     url_parts = urlparse(http_clone_url)
    #     owner = event['body-json']['repository']['project']['name']
    #     name = event['body-json']['repository']['name']
    #     archive_url = "{scheme}://{netloc}/rest/api/latest/projects/{project}/repos/{repo}/archive?at={hash}&format=zip".format(
    #         scheme=url_parts.scheme,
    #         netloc=url_parts.netloc if os.environ.get("SCM_HOSTNAME_OVERRIDE", '') == '' else  os.environ.get("SCM_HOSTNAME_OVERRIDE"),
    #         project=owner,
    #         repo=name,
    #         hash=change['toHash'],
    #     )
    #     branch = change['refId'].replace('refs/heads/', '')
    #     secret = base64.b64encode(
    #         ":".join([event['context']['oauth-key'], event['context']['oauth-secret']])
    #     )
    #     headers['Authorization'] = 'Basic ' + secret
    
    ##########################################################################################################
    # GitHub specific hostflavor
    archive_url = event['body-json']['repository']['archive_url']
    owner = event['body-json']['repository']['owner']['login']
    name = event['body-json']['repository']['name']
    # replace the code archive download and branch reference placeholders
    branch_name = event['body-json']['ref'].replace('refs/heads/', '')
    archive_url = archive_url.replace('{archive_format}', 'zipball').replace('{/ref}', '/' + branch_name)
    # add access token information to archive url
    #archive_url = archive_url+'?access_token='+OAUTH_token
    ##########################################################################################################

    # download the code archive via archive url
    logger.info('Downloading archive from %s' % archive_url)
    r = requests.get(archive_url, verify=verify, headers=headers, params=params)
    # f = StringIO(r.content) #Python2
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
