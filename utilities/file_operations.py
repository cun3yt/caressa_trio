from PIL import Image
import boto3
from shutil import copyfile
from uuid import uuid4


def image_resizer(file_name, hash_version, file_format, size):
    resize_file_name = '{hash_version}_w_{size}.{file_format}'.format(hash_version=hash_version,
                                                                      size=size,
                                                                      file_format=file_format)
    copyfile(src='/tmp/{file_name}'.format(file_name=file_name),
             dst='/tmp/{resize_file_name}'.format(resize_file_name=resize_file_name))

    img = Image.open('/tmp/{resize_file_name}'.format(resize_file_name=resize_file_name))
    img = img.convert("RGB")
    thumbnail_size = size, size
    img.thumbnail(thumbnail_size, Image.ANTIALIAS)
    img.save('/tmp/{resize_file_name}'.format(resize_file_name=resize_file_name))
    return resize_file_name


def _image_thumbnail_resizer(file_name, hash_version, file_format):
    return image_resizer(file_name, hash_version, file_format, 25)


def _image_profile_pic_resizer(file_name, hash_version, file_format):
    return image_resizer(file_name, hash_version, file_format, 250)


def _image_raw_reformat_rename(file_name, hash_version):
    file_format = 'png'
    img = Image.open('/tmp/{file_name}'.format(file_name=file_name))
    image_name = '{hash_version}_raw.{file_format}'.format(hash_version=hash_version,
                                                           file_format=file_format)
    img.save('/tmp/{image_name}'.format(image_name=image_name))
    return image_name


def profile_picture_resizing_wrapper(file_name, hash_version, file_format):
    thumbnail = _image_thumbnail_resizer(file_name, hash_version, file_format)
    profile_pic = _image_profile_pic_resizer(file_name, hash_version, file_format)
    raw_pic = _image_raw_reformat_rename(file_name, hash_version)
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


def generate_versioned_picture_name(current_picture_name=''):
    uuid = str(uuid4())[:8]
    if not current_picture_name:
        return '{hash}_v0'.format(hash=uuid)

    current_picture_version = current_picture_name.rsplit('_')[1]
    increment_version = int(current_picture_version[1:]) + 1
    return '{hash}_v{version}'.format(hash=str(uuid4())[:8],
                                      version=increment_version,)
