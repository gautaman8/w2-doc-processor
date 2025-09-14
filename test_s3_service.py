#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/Users/gautamansarangan/doc-processor')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doc_processor_backend.settings')
django.setup()

from shared_services.services.s3_service import S3Service

def test_s3_service():
    print("Testing S3Service...")
    
    # Test initialization
    print("1. Initializing S3Service...")
    s3_service = S3Service()
    print(f"   Bucket: {s3_service.bucket_name}")
    
    # Test bucket info
    print("2. Getting bucket info...")
    bucket_info = s3_service.get_bucket_info()
    print(f"   Bucket info: {bucket_info}")
    
    # Test presigned URL generation
    print("3. Generating presigned URL...")
    object_key = "test/example.txt"
    signed_url = s3_service.generate_presigned_url(object_key)
    print(f"   Signed URL: {signed_url[:50]}..." if signed_url else "   Failed to generate URL")
    
    # Test listing files
    print("4. Listing files...")
    files = s3_service.list_files()
    print(f"   Found {len(files)} files")
    
    print("S3Service test completed!")

if __name__ == "__main__":
    test_s3_service()
