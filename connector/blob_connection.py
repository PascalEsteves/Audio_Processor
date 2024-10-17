import os
from datetime import datetime
from azure.storage.blob import BlobServiceClient,generate_blob_sas,BlobSasPermissions,ContentSettings
from dateutil.relativedelta import relativedelta
import pandas as pd
from environments.environments import Environments
import io

class BlobStorageConnector:

    __connector_name__ = "Blob Storage"

    def __init__(self) -> None:

        self.container :str =  Environments.get_blob_container()
        self.client : object = self._build_client()

    def _build_client(self):
        """
        Create a connection to Blob Client
        """
        self.user :str = Environments.get_blob_user()
        self.key :str = Environments.get_blob_key()
        return BlobServiceClient(account_url=f"https://{self.user}.blob.core.windows.net",
                                 credential=self.key)

    def upload_file(self,
                    file_path: str,
                    blob_name: str,
                    container: str=None):

        """
        FUNCTION TO UPLOAD FILE TO CONTAINER
        :params file_path : path to file to be uploaded
        :params blob_name : path of file in blob
        :container : container to upload file
        """

        blob : object = self.client.get_blob_client(container=container if container else self.container, blob=blob_name)

        with open(file_path, "rb") as data:
            blob.upload_blob(
                data, overwrite=True, max_concurrency=4
            )

    def delete_file(self,
                    blob_name:str,
                    container=None):

        """
        FUNCTION TO DELETE FILE FROM STORAGE
        :params blob_name : path of file inside blob
        :params container : if specific container in signature
        """

        file :object = self.client.get_blob_client(container=container if container else self.container, blob=blob_name)
        try:
            file.delete_blob()
        except Exception as e:
            print(f"Error occurred while deleting the blob: {e}")

    def download_file(self,
                      blob_name:str ,
                      filepath:str,
                      container:str=None):

        blob = self.client.get_blob_client(container= container if container else self.container, blob= blob_name)

        with open(filepath, "wb") as f:
            blob_data = blob.download_blob()
            f.write(blob_data.readall())


    def get_public_link(self,
                     blob_name:str,
                     container:str=None)->str:

        """
        FUNCTION TO GENERATE SAS LINK FROM FILE
        :params blob_name : path of file inside blob
        :params container : if specific container in signature
        """

        file :object =  self.client.get_blob_client(container=container if container else self.container , blob=blob_name)

        token :str = generate_blob_sas(account_name=self.user,
                                    account_key = self.key,
                                    container_name = container if container else self.container,
                                    blob_name= blob_name,
                                    permission=BlobSasPermissions(read=True, tag=False),
                                    expiry=datetime.utcnow() + relativedelta(months=3)
                                    )

        return file.url + "?" + token

    def get_list_files(self,
                        container:str = None,
                        folder:str =None)->list:

        """
        FUNCTION TO LIST ALL FILES INSIDE A CONTAINER
        :params container : container where files are
        :params folder : To returns only the files present in a specific folder
        """

        client_container :object = self.client.get_container_client(container= container if container else self.container)

        if folder:
            files = [x.name for x in client_container.list_blobs(name_starts_with=folder)]
        else:
            files = [x.name for x in client_container.list_blobs()]

        return files