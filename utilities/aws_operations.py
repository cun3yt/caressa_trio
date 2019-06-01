import os

import boto3
from PIL import Image

from caressa import settings
from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_BUCKET, S3_REGION

from utilities import file_operations as file_ops


def aws_url_creator(bucket, file_key):
    return '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                 bucket=bucket,
                                                 file_key=file_key)


def move_file_from_upload_to_prod_bucket(source_file_key, dest_file_key) -> str:
    """

    :param source_file_key:
    :param dest_file_key:
    :return: public url of the object
    """
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': S3_RAW_UPLOAD_BUCKET,
        'Key': source_file_key
    }
    prod_bucket = s3.Bucket(S3_BUCKET)
    prod_bucket.copy(copy_source, dest_file_key, ExtraArgs={'ACL': 'public-read'})
    return aws_url_creator(S3_BUCKET, dest_file_key)


def resize_photo_from_aws_and_upload_to_prod_bucket(source_file_key, dest_file_key):
    file_ops.download_to_tmp_from_s3(source_file_key, settings.S3_RAW_UPLOAD_BUCKET)

    file_path = '/tmp/{file_name}'.format(file_name=source_file_key)
    file_path_to_resize = '{file_path}.resize'.format(file_path=file_path)
    os.rename(file_path, file_path_to_resize)

    size = 1024, 1024
    im = Image.open(file_path_to_resize)
    rgb_im = im.convert("RGB")
    rgb_im.thumbnail(size, Image.ANTIALIAS)
    rgb_im.save(file_path, "JPEG")

    s3_client = boto3.client('s3')

    s3_client.upload_file(file_path,
                          S3_BUCKET,
                          dest_file_key,
                          ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})

    return aws_url_creator(S3_BUCKET, dest_file_key)


def upload_mp3_to_s3(file_key, local_file_path, return_format: str) -> str:
    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path,
                          S3_BUCKET,
                          file_key,
                          ExtraArgs={'ACL': 'public-read', 'ContentType': 'audio/mp3'})

    if return_format == 'key':
        return file_key

    url = aws_url_creator(bucket=S3_BUCKET, file_key=file_key)
    return url
