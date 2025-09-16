#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "Creating SQS queue..."
aws --endpoint-url=http://localhost:4566 sqs create-queue --queue-name w2-file-events-queue

echo "Listing queues..."
aws --endpoint-url=http://localhost:4566 sqs list-queues

echo "Creating S3 bucket if it doesn't exist..."
aws --endpoint-url=http://localhost:4566 s3 mb s3://w2-bucket

echo "Setup complete!"
