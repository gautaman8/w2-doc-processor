import boto3
from botocore.exceptions import ClientError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        # Auto-create bucket if it doesn't exist
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket '{self.bucket_name}' already exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Successfully created bucket '{self.bucket_name}'")
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket '{self.bucket_name}': {create_error}")
            else:
                logger.error(f"Error checking bucket '{self.bucket_name}': {e}")

    def generate_presigned_url(self, object_key, expiration=3600):
        """Generate a presigned URL for S3 object upload"""
        try:
            response = self.s3_client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for {object_key}")
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    def upload_file(self, file_obj, object_key):
        """Upload file to S3"""
        try:
            self.s3_client.upload_fileobj(
                file_obj, 
                self.bucket_name, 
                object_key
            )
            logger.info(f"Uploaded file to {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            return False

    def delete_file(self, object_key):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted file {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting file: {e}")
            return False

    def list_files(self, prefix=""):
        """List files in the bucket with optional prefix"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            return files
        except ClientError as e:
            logger.error(f"Error listing files: {e}")
            return []

    def get_bucket_info(self):
        """Get information about the bucket"""
        try:
            response = self.s3_client.head_bucket(Bucket=self.bucket_name)
            return {
                'name': self.bucket_name,
                'region': response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amz-bucket-region', 'unknown'),
                'exists': True
            }
        except ClientError as e:
            return {
                'name': self.bucket_name,
                'exists': False,
                'error': str(e)
            }
