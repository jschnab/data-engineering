import boto3
from hashlib import md5


def check_md5(stream, md5):
    """
    Checks the MD5 sum of a bytesIO object.

    Parameters
      stream (bytesIO): data to check
      md5 (str): reference MD5 checksum

    Returns
      bool: True if stream checkum matches reference else False
    """

    md5_sum = md5(stream.getbuffer())

    if md5_sum == md5:
        return True

    return False


def stream_to_S3(profile, region, stream, bucket, path, md5):
    """
    Copies a bytesIO object to AWS S3.

    Parameters
      profile (str): AWS profile name
      region (str): AWS region name
      stream (bytesIO): data to copy
      bucket (str): bucket name
      path (str): destination file path
      md5 (str): MD5 checksum of the data

    Returns
      dict: response of AWS S3 to the transfer
    """

    _client = boto3.Session(
            profile_name=profile,
            region_name=region,
            ).client('s3')

    try:
        response = _client.put_object(
                Body=stream,
                Bucket=bucket,
                Key=path,
                ContentMD5=md5
                )

        return response

    except:
        # catch any error
        raise
