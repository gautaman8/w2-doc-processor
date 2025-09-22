#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "Deploying Lambda functions to LocalStack..."

# Create deployment packages
echo "Creating deployment packages..."

# SQS Handler
echo "Packaging SQS Handler..."
cd lambda_functions/sqs_handler

# Clean up any existing packages and zip files
rm -rf requests* urllib3* certifi* charset_normalizer* idna* python_dateutil* six* *.dist-info __pycache__ s3transfer* boto3* botocore* jmespath* dateutil* *.zip temp_packages

# Install only what we need to a temp directory
pip install -r requirements.txt -t temp_packages --quiet

# Copy handler.py and w2_extractor.py to temp directory
cp handler.py temp_packages/
cp w2_extractor.py temp_packages/

# Create clean zip with only essential files (excluding all junk)
cd temp_packages
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.so" -delete 2>/dev/null || true
find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pem" -delete 2>/dev/null || true
find . -name "*.js" -delete 2>/dev/null || true
find . -name "*.rst" -delete 2>/dev/null || true
find . -name "*.txt" -delete 2>/dev/null || true
find . -name "*.md" -delete 2>/dev/null || true
find . -name "*.json" -delete 2>/dev/null || true
find . -name "*.gz" -delete 2>/dev/null || true
find . -name "*.xml" -delete 2>/dev/null || true
find . -name "*.yml" -delete 2>/dev/null || true
find . -name "*.yaml" -delete 2>/dev/null || true
find . -name "*.cfg" -delete 2>/dev/null || true
find . -name "*.ini" -delete 2>/dev/null || true
find . -name "*.toml" -delete 2>/dev/null || true
find . -name "*.pyi" -delete 2>/dev/null || true
find . -name "*.typed" -delete 2>/dev/null || true
find . -name "*.py.typed" -delete 2>/dev/null || true
find . -name "cli" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "contrib" -type d -exec rm -rf {} + 2>/dev/null || true
# Keep http2 directory as urllib3 needs it
# find . -name "http2" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "emscripten" -type d -exec rm -rf {} + 2>/dev/null || true
zip -r ../sqs-handler.zip handler.py requests/ urllib3/ certifi/ charset_normalizer/ idna/ six.py
cd ..

# Clean up temp directory
rm -rf temp_packages
cd ../..

# Core Processor  
echo "Packaging Core Processor..."
cd lambda_functions/core_processor

# Clean up any existing packages and zip files
rm -rf requests* urllib3* certifi* charset_normalizer* idna* python_dateutil* six* *.dist-info __pycache__ s3transfer* boto3* botocore* jmespath* dateutil* *.zip temp_packages

# Install only what we need to a temp directory
pip install -r requirements.txt -t temp_packages --quiet

# Copy handler.py and w2_extractor.py to temp directory
cp handler.py temp_packages/
cp w2_extractor.py temp_packages/

# Create clean zip with only essential files (excluding all junk)
cd temp_packages
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.so" -delete 2>/dev/null || true
find . -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pem" -delete 2>/dev/null || true
find . -name "*.js" -delete 2>/dev/null || true
find . -name "*.rst" -delete 2>/dev/null || true
find . -name "*.txt" -delete 2>/dev/null || true
find . -name "*.md" -delete 2>/dev/null || true
find . -name "*.json" -delete 2>/dev/null || true
find . -name "*.gz" -delete 2>/dev/null || true
find . -name "*.xml" -delete 2>/dev/null || true
find . -name "*.yml" -delete 2>/dev/null || true
find . -name "*.yaml" -delete 2>/dev/null || true
find . -name "*.cfg" -delete 2>/dev/null || true
find . -name "*.ini" -delete 2>/dev/null || true
find . -name "*.toml" -delete 2>/dev/null || true
find . -name "*.pyi" -delete 2>/dev/null || true
find . -name "*.typed" -delete 2>/dev/null || true
find . -name "*.py.typed" -delete 2>/dev/null || true
find . -name "cli" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "contrib" -type d -exec rm -rf {} + 2>/dev/null || true
# Keep http2 directory as urllib3 needs it
# find . -name "http2" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "emscripten" -type d -exec rm -rf {} + 2>/dev/null || true
zip -r ../core-processor.zip handler.py w2_extractor.py requests/ urllib3/ certifi/ charset_normalizer/ idna/ six.py PyPDF2/
cd ..

# Clean up temp directory
rm -rf temp_packages
cd ../..

# Delete existing functions if they exist
echo "Checking for existing functions..."
aws --endpoint-url=http://localhost:4566 lambda delete-function --function-name sqs-handler 2>/dev/null || echo "SQS Handler function not found, will create new one"
aws --endpoint-url=http://localhost:4566 lambda delete-function --function-name core-processor 2>/dev/null || echo "Core Processor function not found, will create new one"

echo "Deploying SQS Handler Lambda..."
aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name sqs-handler \
    --runtime python3.11 \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --handler handler.lambda_handler \
    --zip-file fileb://lambda_functions/sqs_handler/sqs-handler.zip

echo "Deploying Core Processor Lambda..."
aws --endpoint-url=http://localhost:4566 lambda create-function \
    --function-name core-processor \
    --runtime python3.11 \
    --role arn:aws:iam::000000000000:role/lambda-role \
    --handler handler.lambda_handler \
    --zip-file fileb://lambda_functions/core_processor/core-processor.zip

echo "Lambda functions deployed successfully!"