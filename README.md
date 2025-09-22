# Document Processor

An event-driven document processing system with Django REST API backend, Streamlit frontend, and AWS Lambda functions for automated file processing.

## Architecture

```
S3 Upload → SQS Queue → Lambda Functions → Django API Updates
```

## Project Structure

```
doc-processor/
├── shared_services/          # Shared utilities package
│   └── services/
│       ├── s3_service.py     # S3 service with LocalStack support
│       ├── sqs_service.py    # SQS service for event handling
│       └── event_setup_service.py # Event configuration service
├── doc_processor_backend/    # Django REST API
│   ├── w2_job_app/          # Main app with W2Job model
│   └── manage.py
├── frontend/                # Streamlit frontend
│   └── app.py
├── lambda_functions/        # AWS Lambda functions
│   ├── sqs_handler/         # Processes SQS messages
│   └── core_processor/      # Core document processing logic
├── test_plan/              # Test scripts and documentation
├── requirements.txt         # All dependencies
├── docker-compose.yml       # Complete local setup
└── deploy-lambdas.sh        # Lambda deployment script
```

## Setup & Installation

### Quick Start (Recommended)

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Configure AWS services (SQS, S3, Lambda):**
   ```bash
   # Create SQS queue and S3 bucket
   AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name w2-file-events-queue
   AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url=http://localhost:4566 s3 mb s3://w2-bucket
   
   # Configure S3 events to push to SQS
   ./configure-s3-events.sh
   
   # Deploy Lambda functions
   ./deploy-lambdas.sh
   
   # Configure SQS-Lambda trigger
   ./configure-sqs-lambda.sh
   ```

3. **Verify setup:**
   ```bash
   ./test_plan/test-end-to-end.sh
   ```

### Manual Setup (Alternative)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start LocalStack:**
   ```bash
   docker-compose up localstack -d
   ```

3. **Setup Django database:**
   ```bash
   cd doc_processor_backend
   python manage.py migrate
   ```

4. **Run Django backend:**
   ```bash
   export PYTHONPATH="/Users/gautamansarangan/doc-processor:$PYTHONPATH"
   cd doc_processor_backend
   python manage.py runserver 8000
   ```

5. **Run Streamlit frontend:**
   ```bash
   cd frontend
   streamlit run app.py
   ```

## API Endpoints

- `POST /jobs/` - Create a new job with S3 signed URL
- `GET /jobs/{job_id}/` - Get job details
- `PATCH /jobs/{job_id}/` - Update job status (used by Lambda functions)
- `GET /jobs/bucket_info/` - Get S3 bucket information

## Event-Driven Processing

### Flow Overview
1. **File Upload** → User uploads file to S3 via signed URL
2. **S3 Event** → S3 automatically pushes event to SQS queue
3. **SQS Trigger** → SQS triggers `sqs-handler` Lambda function
4. **Lambda Processing** → `core-processor` Lambda processes the file
5. **Django Update** → Lambda updates job status in Django database

### Lambda Functions
- **`sqs-handler`** - Processes SQS messages and triggers core processing
- **`core-processor`** - Handles document processing and updates job status

## Usage

1. Open http://localhost:8501 in your browser
2. Click "Upload Document" to create a job
3. Upload your file using the provided signed URL
4. **Automatic Processing** - Lambda functions process the file automatically
5. Check job status - it will update from "started" → "Success" automatically

## AWS Services Integration

- **LocalStack** - Simulates AWS services locally (S3, SQS, Lambda)
- **S3 Bucket** - `w2-bucket` with event notifications
- **SQS Queue** - `w2-file-events-queue` for event handling
- **Lambda Functions** - Serverless processing with dependencies
- **Folder structure** - `uploads/{job_id}/w2.pdf`
- **Real signed URLs** - Compatible with AWS S3

## Models

The `W2Job` model includes:
- `job_id` - Unique identifier
- `filename` - Original filename
- `file_uploaded` - Boolean flag (updated by Lambda)
- `status` - Processing status ("started" → "Success")
- `signed_url` - S3 presigned URL for upload
- `created_at` / `updated_at` - Timestamps

```python
from w2_job_app.models import W2Job
```

## Testing

### End-to-End Test
```bash
./test_plan/test-end-to-end.sh
```

### Manual Testing
```bash
# Test S3 upload
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url=http://localhost:4566 s3 cp test-file.pdf s3://w2-bucket/uploads/test-job-123/test-file.pdf

# Check SQS messages
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/w2-file-events-queue

# Test Lambda functions
AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=us-east-1 aws --endpoint-url=http://localhost:4566 lambda list-functions
```

## Troubleshooting

### Common Issues

1. **Lambda functions not found:**
   ```bash
   ./deploy-lambdas.sh
   ```

2. **S3 events not working:**
   ```bash
   ./configure-s3-events.sh
   ```

3. **SQS-Lambda trigger not configured:**
   ```bash
   ./configure-sqs-lambda.sh
   ```

4. **Services not starting:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Shared Services

The `S3Service` can be used across multiple Django projects:

```python
from shared_services.services.s3_service import S3Service

s3_service = S3Service()
signed_url = s3_service.generate_presigned_url("uploads/file.pdf")
```
