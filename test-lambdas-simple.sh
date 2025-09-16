#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "=== Testing Lambda Functions ==="

# Create test payload files
echo '{"bucket_name":"w2-bucket","object_key":"uploads/test-789/w2.pdf","event_name":"s3:ObjectCreated:Put","timestamp":"2024-01-01T00:00:00.000Z"}' > core-processor-payload.json

echo '{"Records":[{"body":"{\"Records\":[{\"eventName\":\"s3:ObjectCreated:Put\",\"s3\":{\"bucket\":{\"name\":\"w2-bucket\"},\"object\":{\"key\":\"uploads/test-789/w2.pdf\"}},\"eventTime\":\"2024-01-01T00:00:00.000Z\"}]}"}]}' > sqs-handler-payload.json

# Test Core Processor
echo "Testing Core Processor..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --payload file://core-processor-payload.json \
    core-processor-response.json

echo "Core Processor Response:"
cat core-processor-response.json
echo ""

# Test SQS Handler
echo "Testing SQS Handler..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name sqs-handler \
    --payload file://sqs-handler-payload.json \
    sqs-handler-response.json

echo "SQS Handler Response:"
cat sqs-handler-response.json
echo ""

echo "=== Test Complete ==="
