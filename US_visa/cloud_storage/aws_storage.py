import os
import sys
import pickle
from io import StringIO
from typing import Union, List

import boto3
from botocore.exceptions import ClientError
from pandas import DataFrame, read_csv

from us_visa.exception import USvisaException
from us_visa.logger import logging
from us_visa.configuration.aws_connection import S3Client


class SimpleStorageService:
    """
    Wrapper around S3. Used by USvisaEstimator.
    """

    def __init__(self):
        try:
            s3_client = S3Client()
            self.s3_resource = s3_client.s3_resource
            self.s3_client = s3_client.s3_client
        except Exception as e:
            raise USvisaException(e, sys) from e

    # ---------- helpers ----------

    def get_bucket(self, bucket_name: str):
        try:
            return self.s3_resource.Bucket(bucket_name)
        except Exception as e:
            raise USvisaException(e, sys) from e

    def s3_key_path_available(self, bucket_name: str, s3_key: str) -> bool:
        """
        Check if any object exists with this prefix in the bucket.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [obj for obj in bucket.objects.filter(Prefix=s3_key)]
            return len(file_objects) > 0
        except Exception as e:
            raise USvisaException(e, sys) from e

    @staticmethod
    def _read_object_body(s3_object, decode: bool = True, make_readable: bool = False) -> Union[StringIO, str, bytes]:
        """
        Internal helper to read raw S3 object content.
        """
        try:
            body = s3_object.get()["Body"].read()
            if decode:
                body = body.decode()
            if make_readable:
                return StringIO(body)
            return body
        except Exception as e:
            raise USvisaException(e, sys) from e

    def get_file_object(self, filename: str, bucket_name: str):
        """
        Get S3 object(s) matching the given key prefix.
        """
        try:
            bucket = self.get_bucket(bucket_name)
            file_objects = [obj for obj in bucket.objects.filter(Prefix=filename)]
            if not file_objects:
                raise USvisaException(f"No object found with prefix {filename} in bucket {bucket_name}", sys)
            # if exactly one -> return single, else list
            return file_objects[0] if len(file_objects) == 1 else file_objects
        except Exception as e:
            raise USvisaException(e, sys) from e

    # ---------- model related ----------

    def load_model(self, model_name: str, bucket_name: str, model_dir: str = None) -> object:
        """
        Load a pickle model stored in S3.
        """
        try:
            key = f"{model_dir}/{model_name}" if model_dir else model_name
            file_object = self.get_file_object(key, bucket_name)
            model_bytes = self._read_object_body(file_object, decode=False)
            model = pickle.loads(model_bytes)
            logging.info(f"Loaded model from s3://{bucket_name}/{key}")
            return model
        except Exception as e:
            raise USvisaException(e, sys) from e

    def upload_file(self, from_filename: str, to_filename: str, bucket_name: str, remove: bool = True):
        """
        Upload a local file to S3.
        """
        try:
            logging.info(f"Uploading {from_filename} to s3://{bucket_name}/{to_filename}")
            self.s3_resource.meta.client.upload_file(from_filename, bucket_name, to_filename)
            if remove and os.path.exists(from_filename):
                os.remove(from_filename)
                logging.info(f"Removed local file {from_filename}")
        except Exception as e:
            raise USvisaException(e, sys) from e

    # ---------- DataFrame helpers (optional but used elsewhere) ----------

    def upload_df_as_csv(self, data_frame: DataFrame, local_filename: str, bucket_filename: str, bucket_name: str):
        """
        Save DataFrame as CSV and upload to S3.
        """
        try:
            data_frame.to_csv(local_filename, index=False)
            self.upload_file(local_filename, bucket_filename, bucket_name)
        except Exception as e:
            raise USvisaException(e, sys) from e

    def get_df_from_object(self, s3_object) -> DataFrame:
        """
        Read CSV data from S3 object into pandas DataFrame.
        """
        try:
            content = self._read_object_body(s3_object, decode=True, make_readable=True)
            df = read_csv(content, na_values="na")
            return df
        except Exception as e:
            raise USvisaException(e, sys) from e

    def read_csv(self, filename: str, bucket_name: str) -> DataFrame:
        """
        Read CSV stored in S3 into DataFrame.
        """
        try:
            s3_object = self.get_file_object(filename, bucket_name)
            return self.get_df_from_object(s3_object)
        except Exception as e:
            raise USvisaException(e, sys) from e
