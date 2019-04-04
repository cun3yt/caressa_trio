import boto3

from caressa.settings import S3_RAW_UPLOAD_BUCKET, S3_PRODUCTION_BUCKET, S3_REGION


def aws_url_creator(bucket, file_key):
    return '{region}/{bucket}/{file_key}'.format(region=S3_REGION,
                                                 bucket=bucket,
                                                 file_key=file_key)


def move_file_from_upload_to_prod_bucket(file_key):
    s3 = boto3.resource('s3')
    copy_source = {
        'Bucket': S3_RAW_UPLOAD_BUCKET,
        'Key': file_key
    }
    prod_bucket = s3.Bucket(S3_PRODUCTION_BUCKET)
    prod_bucket.copy(copy_source, file_key)
    return aws_url_creator(prod_bucket, file_key)