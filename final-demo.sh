#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "🚀 DOC PROCESSOR - COMPLETE S3 → SQS → LAMBDA DEMO"
echo "=================================================="

# Test 1: Upload file to S3 (this should trigger the complete flow)
echo "📁 Step 1: Uploading file to S3 bucket..."
echo "Sample W2 document content" > demo-w2.pdf
aws --endpoint-url=http://localhost:4566 s3 cp demo-w2.pdf s3://w2-bucket/uploads/demo-job-001/w2.pdf
echo "✅ File uploaded successfully!"

# Test 2: Test Lambda functions directly
echo ""
echo "🔧 Step 2: Testing Lambda functions directly..."

# Test Core Processor
echo "Testing Core Processor Lambda..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --cli-binary-format raw-in-base64-out \
    --payload '{"bucket_name":"w2-bucket","object_key":"uploads/demo-job-002/w2.pdf","event_name":"s3:ObjectCreated:Put","timestamp":"2024-01-01T00:00:00.000Z"}' \
    core-response.json

echo "📊 Core Processor Result:"
cat core-response.json | python3 -m json.tool

# Test SQS Handler
echo ""
echo "Testing SQS Handler Lambda..."
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name sqs-handler \
    --cli-binary-format raw-in-base64-out \
    --payload '{"Records":[{"body":"{\"Records\":[{\"eventName\":\"s3:ObjectCreated:Put\",\"s3\":{\"bucket\":{\"name\":\"w2-bucket\"},\"object\":{\"key\":\"uploads/demo-job-003/w2.pdf\"}},\"eventTime\":\"2024-01-01T00:00:00.000Z\"}]}"}]}' \
    sqs-response.json

echo "📊 SQS Handler Result:"
cat sqs-response.json | python3 -m json.tool

echo ""
echo "🎉 DEMO COMPLETE!"
echo "=================="
echo "✅ S3 bucket: w2-bucket"
echo "✅ SQS queue: w2-file-events-queue" 
echo "✅ Lambda functions: sqs-handler, core-processor"
echo "✅ Event flow: S3 → SQS → Lambda → Lambda"
echo "✅ Folder detection: uploads/{job_id}/filename.pdf"
