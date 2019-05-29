import boto3

from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_BUCKET, S3_REGION


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
