from PIL import Image
import boto3
from shutil import copyfile


def image_thumbnail_resizer(file_name, hash_version, file_format):
    file_name_thumbnail = '{hash_version}_w_25.{file_format}'.format(hash_version=hash_version,
                                                                     file_format=file_format)
    copyfile(src='/tmp/{file_name}'.format(file_name=file_name),
             dst='/tmp/{file_name_thumbnail}'.format(file_name_thumbnail=file_name_thumbnail))

    img = Image.open('/tmp/{file_name_thumbnail}'.format(file_name_thumbnail=file_name_thumbnail))
    thumbnail_size = 25, 25
    img.thumbnail(thumbnail_size, Image.ANTIALIAS)
    img.save('/tmp/{file_name_thumbnail}'.format(file_name_thumbnail=file_name_thumbnail))

    return file_name_thumbnail


def image_profile_pic_resizer(file_name, hash_version, file_format):
    file_name_profile_pic = '{hash_version}_w_250.{file_format}'.format(hash_version=hash_version,
                                                                        file_format=file_format)

    copyfile(src='/tmp/{file_name}'.format(file_name=file_name),
             dst='/tmp/{file_name_profile_pic}'.format(file_name_profile_pic=file_name_profile_pic))

    img = Image.open('/tmp/{file_name_profile_pic}'.format(file_name_profile_pic=file_name_profile_pic))
    thumbnail_size = 250, 250
    img.thumbnail(thumbnail_size, Image.ANTIALIAS)
    img.save('/tmp/{file_name_profile_pic}'.format(file_name_profile_pic=file_name_profile_pic))

    return file_name_profile_pic


def image_raw_reformat_rename(file_name, hash_version, file_format):
    img = Image.open('/tmp/{file_name}'.format(file_name=file_name))
    image_name = '{hash_version}_raw.{file_format}'.format(hash_version=hash_version,
                                                           file_format=file_format)
    img.save('/tmp/{image_name}'.format(image_name=image_name))
    return image_name


def profile_picture_resizing_wrapper(file_name, hash_version, file_format):
    thumbnail = image_thumbnail_resizer(file_name, hash_version, file_format)
    profile_pic = image_profile_pic_resizer(file_name, hash_version, file_format)
    raw_pic = image_raw_reformat_rename(file_name, hash_version, file_format)
    return [thumbnail, profile_pic, raw_pic]


def download_to_tmp_from_s3(file_name, bucket):
    s3 = boto3.resource('s3')
    download_path = '/tmp/{}'.format(file_name)
    s3.Bucket(bucket).download_file(file_name, download_path)
    return download_path


def upload_to_s3_from_tmp(bucket, files: list, user_id):
    s3_client = boto3.client('s3')
    for file_name in files:
        file_path = '/tmp/{file_name}'.format(file_name=file_name)
        s3_client.upload_file(file_path,
                              bucket,
                              'images/user/{user_id}/{file_name}'.format(user_id=user_id,
                                                                         file_name=file_name),
                              ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/png'})
