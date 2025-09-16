#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "Deploying Lambda functions to LocalStack..."

# Create deployment packages
echo "Creating deployment packages..."

# SQS Handler
cd lambda_functions/sqs_handler
zip -r sqs-handler.zip handler.py
cd ../..

# Core Processor  
cd lambda_functions/core_processor
zip -r core-processor.zip handler.py
cd ../..

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
