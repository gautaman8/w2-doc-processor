#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "=== Testing Complete S3 → SQS → Lambda Flow ==="

# Test 1: Upload file to S3
echo "1. Uploading file to S3..."
echo "Test file content for complete flow" > test-complete.txt
aws --endpoint-url=http://localhost:4566 s3 cp test-complete.txt s3://w2-bucket/uploads/complete-test-123/w2.pdf

# Test 2: Check SQS queue for messages
echo "2. Checking SQS queue for messages..."
QUEUE_URL=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-url --queue-name w2-file-events-queue --query 'QueueUrl' --output text)
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url "$QUEUE_URL" --max-number-of-messages 1

# Test 3: Test Lambda functions directly
echo "3. Testing Lambda functions directly..."

# Test SQS Handler
echo "Testing SQS Handler..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name sqs-handler \
    --payload '{
        "Records": [
            {
                "body": "{\"Records\":[{\"eventName\":\"s3:ObjectCreated:Put\",\"s3\":{\"bucket\":{\"name\":\"w2-bucket\"},\"object\":{\"key\":\"uploads/direct-test-456/w2.pdf\"}},\"eventTime\":\"2024-01-01T00:00:00.000Z\"}]}"
            }
        ]
    }' \
    sqs-handler-response.json

echo "SQS Handler Response:"
cat sqs-handler-response.json

# Test Core Processor
echo "Testing Core Processor..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --payload '{
        "bucket_name": "w2-bucket",
        "object_key": "uploads/direct-test-456/w2.pdf",
        "event_name": "s3:ObjectCreated:Put",
        "timestamp": "2024-01-01T00:00:00.000Z"
    }' \
    core-processor-response.json

echo "Core Processor Response:"
cat core-processor-response.json

echo "=== Test Complete ==="
