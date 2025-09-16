# 🧪 DOC PROCESSOR - COMPREHENSIVE TEST PLAN

## 📋 **Overview**

This document outlines the complete testing strategy for the Doc Processor system, which implements an event-driven architecture with S3 → SQS → Lambda pipeline for processing W2 document uploads.

## 🏗️ **System Architecture**

```
Frontend (Streamlit) → Backend (Django) → S3 (w2-bucket)
                                    ↓ (Automatic S3 Event)
                                 SQS Queue (w2-file-events-queue)
                                    ↓ (Automatic Message)
                              SQS Handler Lambda
                                    ↓ (Async Event)
                            Core Processor Lambda
                                    ↓ (Logs folder path)
```

## �� **Testing Objectives**

1. **Verify Infrastructure Setup**: All Docker services running correctly
2. **Test S3 Event Flow**: File uploads trigger SQS events
3. **Validate Lambda Functions**: Both Lambda functions process events correctly
4. **End-to-End Flow**: Complete pipeline from upload to folder detection
5. **API Integration**: Django backend and frontend work seamlessly
6. **Error Handling**: System handles failures gracefully

## 📊 **Test Categories**

### **1. Unit Tests**
- Individual Lambda function testing
- S3 service functionality
- Django API endpoints

### **2. Integration Tests**
- S3 → SQS event flow
- SQS → Lambda trigger
- Lambda → Lambda communication

### **3. End-to-End Tests**
- Complete user workflow
- File upload through frontend
- Event processing pipeline

### **4. Performance Tests**
- Concurrent file uploads
- Lambda function scaling
- SQS message processing

## 🚀 **Test Execution Methods**

### **Method 1: Automated Test Suite** ⭐ (Recommended)

#### **Prerequisites**
```bash
# Start the system
docker-compose up --build -d

# Wait for services to be ready
sleep 30
```

#### **Test Script: `test-end-to-end.sh`**
```bash
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
curl -s http://localhost:4566/_localstack/health | jq

echo "Backend health:"
curl -s http://localhost:8000/jobs/bucket_info/ | jq

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
cat core-test-response.json | jq

# Test 4: Django API Testing
echo "🌐 Step 4: Testing Django API..."
JOB_RESPONSE=$(curl -s -X POST http://localhost:8000/jobs/ | jq)
echo "Job created:"
echo "$JOB_RESPONSE"

# Extract and test signed URL
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r '.job_id')
SIGNED_URL=$(echo "$JOB_RESPONSE" | jq -r '.signed_url')

echo "Uploading file using signed URL..."
curl -X PUT "$SIGNED_URL" --data-binary @test-w2-document.pdf

echo "✅ END-TO-END TEST COMPLETE!"
```

### **Method 2: Manual Step-by-Step Testing**

#### **Step 1: Infrastructure Verification**
```bash
# Check all services are running
docker-compose ps

# Verify LocalStack
curl http://localhost:4566/_localstack/health

# Verify Backend API
curl http://localhost:8000/jobs/bucket_info/

# Verify Frontend
open http://localhost:8501
```

#### **Step 2: S3 Event Flow Testing**
```bash
# Upload file to S3
echo "Test content" > test.pdf
aws --endpoint-url=http://localhost:4566 s3 cp test.pdf s3://w2-bucket/uploads/manual-test-001/w2.pdf

# Check SQS queue for messages
QUEUE_URL=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-url --queue-name w2-file-events-queue --query 'QueueUrl' --output text)
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url "$QUEUE_URL"
```

#### **Step 3: Lambda Function Testing**
```bash
# Test Core Processor
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --cli-binary-format raw-in-base64-out \
    --payload '{"bucket_name":"w2-bucket","object_key":"uploads/lambda-test-002/w2.pdf","event_name":"s3:ObjectCreated:Put","timestamp":"2024-01-01T00:00:00.000Z"}' \
    lambda-response.json
cat lambda-response.json | jq
```

### **Method 3: Frontend Integration Testing**

#### **User Workflow Testing**
1. **Open Frontend**: Navigate to http://localhost:8501
2. **Upload File**: Use the web interface to upload a W2 document
3. **Verify Backend**: Check http://localhost:8000/jobs/ for new job
4. **Monitor Logs**: Watch Lambda function execution in logs

#### **API Testing**
```bash
# Create job
curl -X POST http://localhost:8000/jobs/ | jq

# Get job details
curl http://localhost:8000/jobs/{job_id}/ | jq

# Upload file using signed URL
curl -X PUT "SIGNED_URL" --data-binary @file.pdf
```

### **Method 4: Real-Time Monitoring**

#### **Terminal 1: LocalStack Logs**
```bash
docker logs -f doc-processor-localstack
```

#### **Terminal 2: Lambda Logs**
```bash
docker logs -f doc-processor-sqs-handler
docker logs -f doc-processor-core-processor
```

#### **Terminal 3: Backend Logs**
```bash
docker logs -f doc-processor-backend
```

#### **Terminal 4: Run Tests**
```bash
# Upload file and watch logs
aws --endpoint-url=http://localhost:4566 s3 cp test.pdf s3://w2-bucket/uploads/monitor-test-003/w2.pdf
```

## ✅ **Expected Test Results**

### **Successful Test Indicators**

#### **1. Service Health Checks**
```json
// LocalStack Health
{
  "services": {
    "s3": "running",
    "sqs": "running", 
    "lambda": "running"
  }
}

// Backend API Response
{
  "name": "w2-bucket",
  "exists": true,
  "region": "us-east-1"
}
```

#### **2. Lambda Function Responses**
```json
// Core Processor Success
{
  "statusCode": 200,
  "body": "{\"message\": \"File processed successfully\", \"job_id\": \"test-123\", \"folder_path\": \"uploads/test-123/\", \"filename\": \"w2.pdf\"}"
}

// SQS Handler Success
{
  "statusCode": 200,
  "body": "\"SQS events processed successfully\""
}
```

#### **3. S3 Upload Verification**
```bash
# File should appear in S3
aws --endpoint-url=http://localhost:4566 s3 ls s3://w2-bucket/uploads/ --recursive
# Output: uploads/test-job-123/w2.pdf
```

#### **4. SQS Message Verification**
```bash
# Message should be in queue
aws --endpoint-url=http://localhost:4566 sqs receive-message --queue-url "$QUEUE_URL"
# Output: S3 event message with bucket and object details
```

## 🔧 **Debugging Commands**

### **Infrastructure Debugging**
```bash
# Check Docker containers
docker-compose ps

# Check container logs
docker logs doc-processor-localstack
docker logs doc-processor-backend
docker logs doc-processor-frontend

# Check network connectivity
docker network ls
docker network inspect doc-processor_doc-processor-network
```

### **AWS Services Debugging**
```bash
# List S3 buckets
aws --endpoint-url=http://localhost:4566 s3 ls

# List SQS queues
aws --endpoint-url=http://localhost:4566 sqs list-queues

# List Lambda functions
aws --endpoint-url=http://localhost:4566 lambda list-functions

# Check S3 bucket notifications
aws --endpoint-url=http://localhost:4566 s3api get-bucket-notification-configuration --bucket w2-bucket
```

### **Lambda Function Debugging**
```bash
# Check Lambda function configuration
aws --endpoint-url=http://localhost:4566 lambda get-function --function-name core-processor
aws --endpoint-url=http://localhost:4566 lambda get-function --function-name sqs-handler

# Check event source mappings
aws --endpoint-url=http://localhost:4566 lambda list-event-source-mappings --function-name sqs-handler
```

## 📈 **Performance Testing**

### **Concurrent Upload Testing**
```bash
# Test multiple simultaneous uploads
for i in {1..5}; do
  echo "Test file $i" > "test-$i.pdf"
  aws --endpoint-url=http://localhost:4566 s3 cp "test-$i.pdf" "s3://w2-bucket/uploads/concurrent-test-$i/w2.pdf" &
done
wait
```

### **Load Testing**
```bash
# Test with multiple files
for i in {1..10}; do
  echo "Load test file $i" > "load-test-$i.pdf"
  aws --endpoint-url=http://localhost:4566 s3 cp "load-test-$i.pdf" "s3://w2-bucket/uploads/load-test-$i/w2.pdf"
  sleep 1
done
```

## 🚨 **Error Scenarios Testing**

### **1. S3 Service Down**
```bash
# Stop LocalStack
docker-compose stop localstack

# Try to upload file
aws --endpoint-url=http://localhost:4566 s3 cp test.pdf s3://w2-bucket/uploads/error-test/w2.pdf
# Expected: Connection error
```

### **2. Lambda Function Failure**
```bash
# Test with invalid payload
aws --endpoint-url=http://localhost:4566 lambda invoke \
    --function-name core-processor \
    --cli-binary-format raw-in-base64-out \
    --payload '{"invalid": "payload"}' \
    error-response.json
cat error-response.json
```

### **3. SQS Queue Full**
```bash
# Send multiple messages rapidly
for i in {1..100}; do
  aws --endpoint-url=http://localhost:4566 s3 cp test.pdf "s3://w2-bucket/uploads/stress-test-$i/w2.pdf"
done
```

## 📋 **Test Checklist**

### **Pre-Test Setup**
- [ ] Docker and Docker Compose installed
- [ ] AWS CLI installed and configured
- [ ] All services started with `docker-compose up --build -d`
- [ ] Services are healthy (LocalStack, Backend, Frontend)

### **Infrastructure Tests**
- [ ] LocalStack health check passes
- [ ] S3 bucket `w2-bucket` exists
- [ ] SQS queue `w2-file-events-queue` exists
- [ ] Lambda functions `sqs-handler` and `core-processor` deployed
- [ ] S3 event notifications configured

### **Functional Tests**
- [ ] File upload to S3 triggers SQS event
- [ ] SQS event triggers Lambda function
- [ ] Core processor extracts folder path correctly
- [ ] Django API creates jobs successfully
- [ ] Frontend uploads files via signed URL

### **Integration Tests**
- [ ] Complete end-to-end flow works
- [ ] Multiple file uploads processed correctly
- [ ] Error handling works as expected
- [ ] Logs show proper event processing

### **Performance Tests**
- [ ] System handles concurrent uploads
- [ ] Lambda functions process events within timeout
- [ ] SQS queue processes messages efficiently
- [ ] No memory leaks or resource issues

## 🎯 **Success Criteria**

The system is considered fully functional when:

1. **✅ All services start without errors**
2. **✅ File uploads trigger complete event flow**
3. **✅ Lambda functions process events and extract folder paths**
4. **✅ Django API creates jobs and generates signed URLs**
5. **✅ Frontend allows file uploads through web interface**
6. **✅ System handles errors gracefully**
7. **✅ Performance meets requirements (concurrent uploads)**
8. **✅ All logs show proper event processing**

## 📝 **Test Report Template**

### **Test Execution Summary**
- **Date**: [DATE]
- **Tester**: [NAME]
- **Environment**: Local Docker
- **Test Duration**: [TIME]

### **Results**
- **Total Tests**: [NUMBER]
- **Passed**: [NUMBER]
- **Failed**: [NUMBER]
- **Success Rate**: [PERCENTAGE]

### **Issues Found**
1. **Issue**: [DESCRIPTION]
   - **Severity**: [HIGH/MEDIUM/LOW]
   - **Status**: [OPEN/RESOLVED]

### **Recommendations**
1. [RECOMMENDATION 1]
2. [RECOMMENDATION 2]

---

## 🚀 **Quick Start Testing**

For immediate testing, run this one-liner:

```bash
# Complete test in one command
docker-compose up --build -d && sleep 30 && ./test-end-to-end.sh
```

This comprehensive test plan ensures your Doc Processor system is thoroughly tested and ready for production! 🎉
