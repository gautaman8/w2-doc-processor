#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "Configuring SQS to trigger Lambda function..."

# Get SQS queue URL
QUEUE_URL=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-url --queue-name w2-file-events-queue --query 'QueueUrl' --output text)
echo "Queue URL: $QUEUE_URL"

# Get SQS queue ARN
QUEUE_ARN=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
echo "Queue ARN: $QUEUE_ARN"

# Create event source mapping
echo "Creating event source mapping..."
aws --endpoint-url=http://localhost:4566 lambda create-event-source-mapping \
    --function-name sqs-handler \
    --event-source-arn "$QUEUE_ARN" \
    --batch-size 1

echo "SQS Lambda configuration complete!"
