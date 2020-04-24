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


SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'ALPR_VictorES'

DATABASE_REMOTE='My Drive/ALPR/ALPR_Data/database'
RESOURCES_REMOTE='My Drive/ALPR/ALPR_Data/resources'

os.chdir(os.getcwd()+"/setup")
#Oauth2 client:
authInst = auth.auth(SCOPES,CLIENT_SECRET_FILE,APPLICATION_NAME)
    
credentials = authInst.getCredentials()

httpInst = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=httpInst)

# auth.listFiles(drive_service, 20)
# auth.download_folder(drive_service,'1RwoZfh5MzePh11uQnMv-L-7GIO02N6S9', "","database" )
# folder_name = 'database'

# folders = drive_service.files().list(
#             q=f"name contains '{folder_name}' and mimeType='application/vnd.google-apps.folder'",
#             fields='files(id, name, parents)').execute()

# print(folders)
# for i in range(0,len(folders['files'])):
#     path = auth.get_full_path(drive_service, folders['files'][i])
#     print(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("database_dir")
    parser.add_argument("resources_dir")
    args = parser.parse_args()

    database_dir = args.database_dir
    resources_dir = args.resources_dir
    database_name = DATABASE_REMOTE.split('/')[-1]
    resources_name = RESOURCES_REMOTE.split('/')[-1]
    #Download database:
    print("Download database...")
    databaseList = drive_service.files().list(
            q=f"name contains '{database_name}' and mimeType='application/vnd.google-apps.folder'",
            fields='files(id, name, parents)').execute()
    downloadItem = None
    for folder in databaseList['files']:
        path = auth.get_full_path(drive_service, folder)
        print(path)
        if path == DATABASE_REMOTE:
            downloadItem = folder
            break
    os.chdir(database_dir)
    if downloadItem !=  None:
        auth.download_folder(drive_service, downloadItem['id'], folder_name=database_name)
    else:
        print("Error: Cannot find database!")
    #Download resources:
    resourcesList = drive_service.files().list(
            q=f"name contains '{resources_name}' and mimeType='application/vnd.google-apps.folder'",
            fields='files(id, name, parents)').execute()
    downloadItem = None
    for folder in resourcesList['files']:
        print(path)
        path = auth.get_full_path(drive_service, folder)
        if path == RESOURCES_REMOTE:
            downloadItem = folder
            break
    os.chdir(resources_dir)
    if downloadItem !=  None:
        auth.download_folder(drive_service,downloadItem['id'], folder_name=resources_name)
    else:
        print("Error: Cannot find resources!")

if __name__ == '__main__':
    main()