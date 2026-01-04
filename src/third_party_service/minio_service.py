import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from loguru import logger


class MinioService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url='http://114.67.220.218:9000',
            aws_access_key_id='admin',
            aws_secret_access_key='password123',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )

    def upload_single_file(self, filename, bucket_name, object_name: str = "images"):
        try:
            self.s3.upload_file(filename=filename, bucket=bucket_name, key=object_name)
            return True
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return False

    def delete_single_file(self, bucket_name, object_name):
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_name)
            print(f"文件 {object_name} 删除成功")
            return True
        except ClientError as e:
            print(f"删除失败: {e}")
            return False

    def get_presigned_url(self, bucket_name, object_name, expiration=3600 * 24 * 36):
        """
        生成带签名的临时访问 URL
        :param expiration: URL 有效期（秒），默认 1 小时
        """
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"生成 URL 失败: {e}")
            return None

