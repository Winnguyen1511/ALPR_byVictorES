from __future__ import print_function
import httplib2
import os, io

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import argparse

import auth

platePb = 'yolo-plate.pb'
plateMeta = 'yolo-plate.meta'
charPb = 'yolo-character.pb'
charMeta = 'yolo-character.meta'
charCnn = 'character_recognition.h5'

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None
SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ALPR_VictorES'

os.chdir(os.getcwd()+"/setup")
#Oauth2 client:
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
    
credentials = authInst.getCredentials()

httpInst = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=httpInst)



def downloadFile(file_id,filepath):
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath,'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def searchFile(query):
    results = drive_service.files().list(
    fields="nextPageToken, files(id, name)",q=query).execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        # print('Files:')
        # for item in items:
        #     print(item)
        #     print('{0} ({1})'.format(item['name'], item['id'], item['mimeType']))
        return items[0]
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("platePb")
    parser.add_argument("plateMeta")
    parser.add_argument("charPb")
    parser.add_argument("charMeta")
    parser.add_argument("charCnn")

    args = parser.parse_args()
    platePbDir = args.platePb
    plateMetaDir = args.plateMeta
    charPbDir = args.charPb
    charMetaDir = args.charMeta
    charCnnDir = args.charCnn
    #Search all needed file:
    print("> Collecting resources...")
    platePbObj = searchFile("name contains '"+platePb+"'")
    plateMetaObj = searchFile("name contains '"+plateMeta+"'")
    charPbObj = searchFile("name contains '"+charPb+"'")
    charMetaObj = searchFile("name contains '"+charMeta+"'")
    charCnnObj = searchFile("name contains '"+charCnn+"'")
    print("> Collecting completed!")
    #Start to download:
    print("> Start to download...")
    if(os.path.exists(platePbDir) == False):
        print("> Download ",platePbDir)
        downloadFile(platePbObj['id'], platePbDir)
    else:
        print(platePbDir," exist!")
    if(os.path.exists(plateMetaDir) == False):
        print("> Download ",plateMetaDir)
        downloadFile(plateMetaObj['id'], plateMetaDir)
    else:
        print(plateMetaDir, " exist!")
    if(os.path.exists(charPbDir) == False):
        print("> Download ",charPbDir)
        downloadFile(charPbObj['id'], charPbDir)
    else:
        print(charPbDir, " exist!")
    if(os.path.exists(charMetaDir) == False):
        print("> Download ",charMetaDir)
        downloadFile(charMetaObj['id'], charMetaDir)
    else:
        print(charMetaDir, " exists!")
    if(os.path.exists(charCnnDir) == False):
        print("> Download ",charCnnDir)
        downloadFile(charCnnObj['id'], charCnnDir)
    else:
        print(charCnnDir, " exists!")
    print("> Download completed!")
main()
