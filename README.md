# Document Processor

An event-driven document processing system with Django REST API backend, Streamlit frontend, and AWS Lambda functions for automated file processing.

> ⚠️ **Platform Requirements:** This project requires **macOS** or **WSL2 on Windows** to run the setup scripts. The bash scripts (`.sh` files) are not compatible with native Windows Command Prompt or PowerShell.

## Quick Start

**One-command setup with retry logic:**
```bash
./quick-start.sh
```

This script will:
1. Start all Docker services
2. Wait for LocalStack to initialize
3. Create SQS queue and S3 bucket
4. Configure S3 event notifications
5. Initialize AWS Secrets Manager with API key
6. Deploy Lambda functions
7. Configure SQS-Lambda triggers
8. Verify all services are ready

**Access the application:**
- 🌐 Frontend: http://localhost:8501
- 🔧 Backend: http://localhost:8000
- ☁️ LocalStack: http://localhost:4566

## Manual Setup (Step-by-step)

If you prefer to run each step manually:

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

   # Initialize AWS Secrets Manager with API key
   ./init-secrets.sh
   ```

3. **Verify setup:**
   ```bash
   ./test_plan/test-end-to-end.sh
   ```
This test script is WIP. It's best to test using frontend app. 


# Architecture

```
S3 Upload → SQS Queue → Lambda Functions → Django API Updates
```
For more details refer [Design.md](Design.md)
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

