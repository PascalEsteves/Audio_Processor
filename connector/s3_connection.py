import boto3
from dateutil.relativedelta import relativedelta
from environments.environments import Environments
import datetime
from typing import List

class S3_Connector:

    __connector_name__ = "S3 Storage"

    def __init__(self) -> None:

        self.bucket :str = Environments.get_s3_bucket_name()
        self.client = self._build_client()

    def _build_client(self):
        """
        Create a connection to client S3 storage
        """
        aws_access_key_id :str = Environments.get_s3_access_key()
        aws_access_secret_id :str = Environments.get_s3_secret_key()
        url_endpoint : str = Environments.get_s3_url()

        return boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_access_secret_id,
            endpoint_url=url_endpoint,
        )

    def upload_file(
            self,
            filepath: str,
            filename: str = None,
            bucket_name: str =None,
        ) -> str:

        """
        FUNCTION TO UPLOAD FILE TO BUCKET

        :params filepath : filepath to file to be uploaded
        :params bucket_name : Bucket to upload file
        :params filename : filename/filepath for file inside the bucket

        """

        try:
            self.client.upload_file(
                Filename=filepath,
                Bucket=bucket_name if bucket_name else self.bucket,
                Key=filename if filename else filepath
            )
        except FileNotFoundError:
            print("The file was not found")

        except Exception as e:
            print("Credentials not available")

    def delete_file(self,
                       filename:str ,
                       bucket_name:str = None):
        """
        Delete a file from an S3 bucket.

        :param bucket_name: The S3 bucket name
        :param filename: The name of the file (object) to delete
        """
        try:
            self.client.delete_object(Bucket=bucket_name if bucket_name else self.bucket, Key=filename)
        except Exception as e:
            print(f"Error: {str(e)}")

    def download_file(
        self,
        object_name: str,
        filepath: str,
        bucket: str = None
        ) -> None:

        """
        Function to download a file from an S3 bucket.

        :param object_name: Name of the file (object) in S3
        :param bucket_name: Name of the S3 bucket
        :param file_name: The file name to save the downloaded content locally
        """
        try:
            self.client.download_file(
                Bucket=bucket if bucket else self.bucket,
                Key=object_name,
                Filename=filepath
            )
        except Exception as e:
            print(f"Error: {str(e)}")

    def get_list_of_files(self, bucket_name:str=None, folder:str=None)->List:
        """
        Function to list files in a specific S3 bucket.

        :param bucket_name: Name of the S3 bucket
        :param folder_name: Folder (prefix) to list files from
        :return: List of files (keys) in the folder
        """
        try:
            s3_result = self.client.list_objects_v2(Bucket=bucket_name if bucket_name else self.bucket, Prefix=folder)

            file_list = []
            for key in s3_result['Contents']:
                if key["Size"]!=0:
                    file_list.append(key['Key'])

            while s3_result['IsTruncated']:
                continuation_key = s3_result['NextContinuationToken']

                s3_result = self.client.list_objects_v2(Bucket=bucket_name if bucket_name else self.bucket,
                                                        Prefix=folder,
                                                        ContinuationToken=continuation_key)
                for key in s3_result['Contents']:
                    if key["Size"] != 0:
                        file_list.append(key['Key'])

            return file_list

        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    def generate_public_link(
        self,
        filepath: str,
        bucket: str = None,
        duration: relativedelta = relativedelta(months=1)
    ) -> str:

        """
        Function to generate a pre-signed URL to share an S3 object.

        :param bucket: Name of the S3 bucket
        :param filename: Name of the file in S3
        :param expiration: Time in seconds for the presigned URL to remain valid (default is 3600 seconds or 1 hour)
        :return: Presigned URL as a string. If error, returns None.
        """


        now : datetime = datetime.now()
        expiration_datetime :datetime = now + duration
        duration_timedelta = expiration_datetime - now
        duration_seconds = duration_timedelta.days * 24 * 3600 + duration_timedelta.seconds

        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket if bucket else self.bucket, "Key": filepath},
            ExpiresIn=duration_seconds,
        )

