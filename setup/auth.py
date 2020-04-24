from __future__ import print_function
import httplib2
import os
import io
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
class auth:
    def __init__(self,SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME):
        self.SCOPES = SCOPES
        self.CLIENT_SECRET_FILE = CLIENT_SECRET_FILE
        self.APPLICATION_NAME = APPLICATION_NAME
    def getCredentials(self):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        cwd_dir = os.getcwd()
        credential_dir = os.path.join(cwd_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'google-drive-credentials.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            #To intensitive ignore all the argparser 
            flags = tools.argparser.parse_args(args=[])
            credentials = tools.run_flow(flow, store, flags)
            print('Storing credentials to ' + credential_path)
        return credentials

def download_folder(service, folder_id, location="", folder_name="tmp"):
    if not os.path.exists(location + folder_name):
        os.makedirs(location + folder_name)
    location += folder_name + '/'

    result = []
    page_token = None

    while True:
        size = 100
        #Find all folder and files in folder id:
        query = f"'{folder_id}' in parents"
        fields='nextPageToken, files(id, name, mimeType)'
        files = service.files().list(q=query, fields=fields,
                                     pageToken=page_token, pageSize=size).execute()
        result.extend(files['files'])
        pageToken = files.get('nextPageToken')
        if not pageToken:
            break
    result = sorted(result, key=lambda x:x['name'])

    total = len(result)
    current = 1
    for item in result:
        file_id = item['id']
        file_name = item['name']
        mime_type = item['mimeType']
        print(f'{file_name} {mime_type} ({current}/{total})')
        if mime_type == 'application/vnd.google-apps.folder':
            #download the child folder
            download_folder(service, file_id, location, file_name)
        elif not os.path.isfile(location + file_name):
            download_file(service, file_id, location, file_name)
        current += 1
    
    # print(result)


def download_file(service, file_id, location, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False

    #download io stream:
    while done is False:
        try:
            status, done = downloader.next_chunk()
        except:
            fh.close()
            os.remove(location+file_name)
            return False
        print(f'\rDownload {int(status.progress() * 100)}%.')
    #write file from io stream:
    with io.open(location+file_name,'wb') as f:
        fh.seek(0)
        f.write(fh.read())
    

def get_full_path(service, folder):
    if not 'parents' in folder:
        return folder['name']
    
    files = service.files().get(fileId=folder['parents'][0],
                                fields='id, name, parents').execute()
    path = files['name'] + '/'+folder['name']
    while 'parents' in files:
        files = service.files().get(fileId=files['parents'][0], fields='id, name, parents').execute()
        path = files['name'] + '/' + path
    return path

def listFiles(service, size):
    results = service.files().list(
        pageSize=size,fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            print('{0} ({1})'.format(item['name'], item['id']))