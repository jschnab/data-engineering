import logging
import os
import urllib.request

from datetime import datetime
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import boto3
import pandas as pd

S3_BUCKET = "put your bucket name here"
DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/"
    "00462/drugsCom_raw.zip"
)
KEY_PREFIX = "extract-ex9"
CSV_SEP = "\t"
CSV_ENCODING = "latin-1"

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)


def upload_to_s3(bucket, key, filename):
    client = boto3.client("s3")
    client.upload_file(Bucket=bucket, Key=key, Filename=filename)


def download_from_s3(bucket, key, filename):
    client = boto3.client("s3")
    client.download_file(Bucket=bucket, Key=key, Filename=filename)


def list_s3_objects(bucket, prefix):
    client = boto3.client("s3")
    kwargs = {"Bucket": bucket, "Prefix": prefix}
    token = ""  # continuation token that allows to fetch next page of results
    keys = []  # list of object names

    while token is not None:
        if token != "":
            kwargs["ContinuationToken"] = token
        response = client.list_objects_v2(**kwargs)
        contents = response.get("Contents")
        for obj in contents:
            key = obj.get("Key")
            if key[-1] != "/":  # ignore directories
                keys.append(key)
        token = response.get("NextContinuationToken")

    return keys


def transform_csv(original, transformed, sep=CSV_SEP, encoding=CSV_ENCODING):
    df = pd.read_csv(original, sep=sep, encoding=encoding)
    filtered_df = df[(df["rating"] == 9) | (df["rating"] == 10)]
    filtered_df.to_csv(transformed, index=False, sep=sep, encoding=encoding)


def extract(url=DATA_URL, bucket=S3_BUCKET, key_prefix=KEY_PREFIX, date=None):
    logging.info("start data extract task")
    with TemporaryDirectory() as temp_dir:

        logging.info(f"downloading {url}")
        with urllib.request.urlopen(url) as response:
            filename = url.split("/")[-1]
            local_filename = os.path.join(temp_dir, filename)
            with open(local_filename, "wb") as f:
                f.write(response.read())

            # upload zip archive
            if not date:
                date = datetime.now().strftime("%Y/%m/%d")
            key = f"{key_prefix}/{date}/{filename}"
            logging.info(f"uploading to s3://{bucket}/{key}")
            upload_to_s3(bucket=bucket, key=key, filename=local_filename)

            # upload unzipped archive contents
            with ZipFile(local_filename, "r") as f:
                for fi in f.namelist():
                    f.extract(fi, path=temp_dir)
                    logging.info(f"unzipping {fi} to {temp_dir}")
                    local_filename = os.path.join(temp_dir, fi)
                    key = f"{key_prefix}/{date}/extracted/{fi}"
                    logging.info(f"uploading to s3://{bucket}/{key}")
                    upload_to_s3(
                        bucket=bucket,
                        key=key,
                        filename=local_filename
                    )
    logging.info("finished data extract task")


def transform(bucket=S3_BUCKET, key_prefix=KEY_PREFIX, date=None):
    logging.info("start data transformation task")
    if not date:
        date = datetime.now().strftime("%Y/%m/%d")

    unzipped_prefix = f"{key_prefix}/{date}/extracted"
    transformed_prefix = f"{key_prefix}/{date}/transformed"

    with TemporaryDirectory() as temp_dir:

        for key in list_s3_objects(bucket, unzipped_prefix):
            basename = key.split("/")[-1]
            no_ext, ext = os.path.splitext(basename)

            # full path of file before and after transformation
            raw_filename = os.path.join(temp_dir, basename)
            trans_basename = f"{no_ext}_trans{ext}"
            trans_filename = os.path.join(temp_dir, trans_basename)

            logging.info(f"downloading s3://{bucket}/{key} to {raw_filename}")
            download_from_s3(bucket=bucket, key=key, filename=raw_filename)

            logging.info(f"transforming {raw_filename}")
            transform_csv(raw_filename, trans_filename)

            transformed_key = f"{transformed_prefix}/{trans_basename}"
            logging.info(
                f"uploading {trans_basename} to s3://{bucket}/"
                f"{transformed_key}"
            )
            upload_to_s3(
                bucket=bucket,
                key=transformed_key,
                filename=trans_filename
            )
    logging.info("finished data transformation task")


def main():
    extract()
    transform()


if __name__ == "__main__":
    main()
