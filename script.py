import os
import time
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings

DIST_DIR = './dist'
CONTAINER_NAME = '$web'

def generate_files():
    # read the files in /dist
    dist_files = []
    for (dirpath, dirname, filenames) in os.walk(DIST_DIR):
        dist_files.extend([dirpath.replace('\\', '/') + '/' + filename for filename in filenames])

    # include index.html
    upload_files = ['./index.html']
    upload_files.extend(dist_files)
    print('These are the files that will be uploaded to blob:')
    upload_files = [name.replace('./', '') for name in upload_files]
    for file in upload_files:
        print(file)
    return upload_files

def update_content_type(container_client, upload_name, content_type):
    print(f'Updating content type for {upload_name} with content_type = {content_type}')
    blob_client = container_client.get_blob_client(upload_name)
    blob_client.set_http_headers(content_settings=ContentSettings(content_type=content_type))

def upload_files(container_client, files):
    for file in files:
        with open(file, "rb") as data:
            upload_name = file.replace('./', '')
            container_client.upload_blob(name=upload_name, data=data)
            if '.png' in upload_name:
                update_content_type(container_client, upload_name, 'image/png')
            elif '.mp4' in upload_name:
                update_content_type(container_client, upload_name, 'video/mp4')
            elif '.html' in upload_name:
                update_content_type(container_client, upload_name, 'text/html')
    print('done uploading')

# algo:
# 1) find container, true: tear down
# 2) wait 60 secs 
# 3) create container
# 4) upload files

if __name__ ==  "__main__":
    connection_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_str:
        print('AZURE_STORAGE_CONNECTION_STRING is not set!')
        exit()
    blob_service_client = BlobServiceClient.from_connection_string(connection_str)
    try:
        container = blob_service_client.get_container_client(CONTAINER_NAME)
        if container == None:
            print(f'container {CONTAINER_NAME} does not exist!')
        else:
            # delete_container
            container.delete_container()
            print('deleting container...')
            print('Sleeping for 60 secs...')
            time.sleep(60)
    finally:
        print('Creating new container...')
        new_container = blob_service_client.create_container(CONTAINER_NAME)
        print('sleeping for 60 sec')
        time.sleep(60)
        files = generate_files()
        upload_files(new_container, files)