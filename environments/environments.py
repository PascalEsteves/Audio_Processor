from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

class Environments:

    blob_credentials : Dict = {
                               "blob_user": os.getenv("BLOB_USER"),
                               "blob_key": os.getenv("BLOB_KEY"),
                               "container": os.getenv("CONTAINER")
                               }

    s3_credentials : Dict = {
                               "s3_access_key": os.getenv("S3_ACCESS_KEY"),
                               "s3_secret_key": os.getenv("S3_SECRET_KEY"),
                               "s3_bucket_name": os.getenv("S3_BUCKET_NAME"),
                               "s3_url": os.getenv("S3_URL")
                               }

    box_credentials : Dict = {
                               "JWTAuth": os.getenv("BOX_TOKEN")
                               }

    local_paramets : Dict = {
        "local_path": os.getenv("LOCAL_PATH")
    }

    db_parameters : Dict = {
        "db_engine": os.getenv("DB_ENGINE"),
        "username" : os.getenv("DB_USERNAME"),
        "password" : os.getenv("DB_PASSWORD"),
        "host" : os.getenv("DB_HOST"),
        "db_name" : os.getenv("DB_NAME")
    }

    HYPER_PARAMETERS_PYANNOTATE: Dict= {
                "min_duration_on": 0.0,
                "min_duration_off": 0.0
    }

    hugging_face_token : Dict = {"token": os.getenv("HUGGING_FACE_TOKEN")}

    Api_endpoints: Dict = {"PYANNOTATE": "http://127.0.0.1:8000",
                           "WHISPER": "http://127.0.0.1:5000"}

    @classmethod
    def get_box_token(cls)->str:
        return cls.box_credentials.get("blob_user")

    @classmethod
    def get_blob_user(cls)->str:
        return cls.blob_credentials.get("blob_user")

    @classmethod
    def get_blob_key(cls)->str:
        return cls.blob_credentials.get("blob_key")

    @classmethod
    def get_blob_container(cls)->str:
        return cls.blob_credentials.get("container")

    @classmethod
    def get_s3_access_key(cls)->str:
        return cls.s3_credentials.get("s3_access_key")

    @classmethod
    def get_s3_secret_key(cls)->str:
        return cls.s3_credentials.get("s3_secret_key")

    @classmethod
    def get_s3_bucket_name(cls)->str:
        return cls.s3_credentials.get("s3_bucket_name")

    @classmethod
    def get_s3_url(cls)->str:
        return cls.s3_credentials.get("s3_url")

    @classmethod
    def get_db_engine(cls)->str:
        return cls.db_parameters.get("db_engine")

    @classmethod
    def get_db_username(cls)->str:
        return cls.db_parameters.get("username")

    @classmethod
    def get_db_password(cls)->str:
        return cls.db_parameters.get("password")

    @classmethod
    def get_db_host(cls)->str:
        return cls.db_parameters.get("host")

    @classmethod
    def get_db_name(cls)-> str:
        return cls.db_parameters.get("db_name")

    @classmethod
    def get_hugging_face_token(cls)->str:
        return cls.hugging_face_token.get("token")

    @classmethod
    def get_api_endpoint(cls, endpoint:str)->str:
        return cls.Api_endpoints.get(endpoint,"None")
