# Shared Services

Reusable utilities for Django apps.

## Usage

```python
from shared_services.services.s3_service import S3Service

# Generate signed URL
s3_service = S3Service()
signed_url = s3_service.generate_presigned_url("uploads/file.pdf")

# Upload file
s3_service.upload_file(file_obj, "uploads/file.pdf")
```

## Setup

Add to Django settings:

```python
AWS_ACCESS_KEY_ID = 'test'
AWS_SECRET_ACCESS_KEY = 'test'
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_ENDPOINT_URL = 'http://localhost:4566'
AWS_STORAGE_BUCKET_NAME = 'w3'
```

## LocalStack

```bash
docker-compose up -d
```

## Across Projects

Copy `shared_services/` folder to any Django project. Import and use.

## Services

- **S3Service** - AWS S3 with LocalStack support
  - `generate_presigned_url(key, expiration=3600)`
  - `upload_file(file_obj, key)`
  - `delete_file(key)`
  - `list_files(prefix="")`
  - `get_bucket_info()`
