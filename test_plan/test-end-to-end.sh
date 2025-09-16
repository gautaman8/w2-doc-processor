#!/bin/bash
# Complete automated test suite

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "🧪 END-TO-END TESTING SUITE"
echo "============================"

# Test 1: Service Health Checks
echo "🔍 Step 1: Checking service health..."
echo "LocalStack health:"
curl -s http://localhost:4566/_localstack/health 

echo "Backend health:"
curl -s http://localhost:8000/jobs/bucket_info/ 

echo "Frontend health:"
curl -s http://localhost:8501/ | head -5

# Test 2: S3 → SQS → Lambda Flow
echo "🔄 Step 2: Testing S3 → SQS → Lambda flow..."
echo "Sample W2 document for testing" > test-w2-document.pdf
aws --endpoint-url=http://localhost:4566 s3 cp test-w2-document.pdf s3://w2-bucket/uploads/test-job-$(date +%s)/w2.pdf
sleep 3

# Test 3: Lambda Function Testing
echo "⚡ Step 3: Testing Lambda functions..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --cli-binary-format raw-in-base64-out \
    --payload '{"bucket_name":"w2-bucket","object_key":"uploads/test-123/w2.pdf","event_name":"s3:ObjectCreated:Put","timestamp":"2024-01-01T00:00:00.000Z"}' \
    core-test-response.json

echo "Core Processor Response:"
cat core-test-response.json 

# Test 4: Django API Testing
echo "🌐 Step 4: Testing Django API..."
JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/jobs/ )
echo "Job created:"
echo "$JOB_RESPONSE"



echo "✅ END-TO-END TEST COMPLETE!"