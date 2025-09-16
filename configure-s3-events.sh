#!/bin/bash

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

echo "Getting SQS queue URL..."
QUEUE_URL=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-url --queue-name w2-file-events-queue --query 'QueueUrl' --output text)
echo "Queue URL: $QUEUE_URL"

echo "Getting SQS queue ARN..."
QUEUE_ARN=$(aws --endpoint-url=http://localhost:4566 sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text)
echo "Queue ARN: $QUEUE_ARN"

echo "Configuring S3 bucket notification..."
aws --endpoint-url=http://localhost:4566 s3api put-bucket-notification-configuration \
    --bucket w2-bucket \
    --notification-configuration '{
        "QueueConfigurations": [
            {
                "Id": "w2-file-events",
                "QueueArn": "'$QUEUE_ARN'",
                "Events": ["s3:ObjectCreated:*"],
                "Filter": {
                    "Key": {
                        "FilterRules": [
                            {
                                "Name": "prefix",
                                "Value": "uploads/"
                            }
                        ]
                    }
                }
            }
        ]
    }'

echo "S3 event configuration complete!"
