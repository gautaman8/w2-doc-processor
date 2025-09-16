#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/Users/gautamansarangan/doc-processor/doc_processor_backend')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doc_processor_backend.settings')
django.setup()

from shared_services.services.s3_service import S3Service
import uuid
import time

def test_new_object_key_format():
    print("Testing new object key format...")
    
    # Simulate the view logic
    timestamp = str(int(time.time()))
    unique_id = str(uuid.uuid4())[:8]
    job_id = f"{timestamp}_{unique_id}"
    
    # New object key format
    object_key = f"uploads/{job_id}/w2.pdf"
    print(f"Job ID: {job_id}")
    print(f"Object Key: {object_key}")
    
    # Test S3Service with new format
    s3_service = S3Service()
    signed_url = s3_service.generate_presigned_url(object_key)
    
    if signed_url:
        print(f"✅ Generated signed URL successfully")
        print(f"URL: {signed_url[:80]}...")
        
        # Test that the URL contains the correct path
        if f"uploads/{job_id}/w2.pdf" in signed_url:
            print("✅ Object key format is correct in signed URL")
        else:
            print("❌ Object key format is incorrect in signed URL")
    else:
        print("❌ Failed to generate signed URL")

if __name__ == "__main__":
    test_new_object_key_format()
