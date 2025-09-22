import json
import boto3
import logging
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
lambda_client = boto3.client(
    'lambda',
    endpoint_url=os.environ.get('AWS_ENDPOINT_URL'),
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name=os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

def lambda_handler(event, context):
    """
    SQS Handler Lambda function
    Processes both S3 events and external events from SQS queue
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Process each record in the SQS event
        for record in event.get('Records', []):
            message_body = json.loads(record['body'])
            
            # Check if this is an S3 event (has eventSource: aws:s3)
            if 'Records' in message_body and len(message_body['Records']) > 0:
                first_record = message_body['Records'][0]
                if first_record.get('eventSource') == 'aws:s3':
                    # This is an S3 event - process as before
                    logger.info("Processing S3 event from AWS")
                    
                    # Extract S3 event records
                    for s3_record in message_body.get('Records', []):
                        bucket_name = s3_record['s3']['bucket']['name']
                        object_key = s3_record['s3']['object']['key']
                        event_name = s3_record['eventName']
                        
                        logger.info(f"Processing S3 event: {event_name} for {bucket_name}/{object_key}")
                        
                        # Create event for core processor
                        core_processor_event = {
                            'event_type': 's3_upload',  # Add event_type for consistency
                            'bucket_name': bucket_name,
                            'object_key': object_key,
                            'event_name': event_name,
                            'timestamp': s3_record['eventTime']
                        }
                        
                        # Invoke core processor Lambda asynchronously
                        response = lambda_client.invoke(
                            FunctionName='core-processor',
                            InvocationType='Event',  # Asynchronous invocation
                            Payload=json.dumps(core_processor_event)
                        )
                        
                        logger.info(f"Triggered core processor for S3 event: {object_key}")
                else:
                    # This is an external event - pass it directly to core processor
                    logger.info(f"Processing external event: {message_body.get('event_type')} for job {message_body.get('job_id')}")
                    
                    # Invoke core processor Lambda asynchronously
                    response = lambda_client.invoke(
                        FunctionName='core-processor',
                        InvocationType='Event',  # Asynchronous invocation
                        Payload=json.dumps(message_body)
                    )
                    
                    logger.info(f"Triggered core processor for external event: {message_body.get('event_type')}")
            else:
                # This is a direct external event (no Records wrapper)
                logger.info(f"Processing direct external event: {message_body.get('event_type')} for job {message_body.get('job_id')}")
                
                # Invoke core processor Lambda asynchronously
                response = lambda_client.invoke(
                    FunctionName='core-processor',
                    InvocationType='Event',  # Asynchronous invocation
                    Payload=json.dumps(message_body)
                )
                
                logger.info(f"Triggered core processor for direct external event: {message_body.get('event_type')}")
                
        return {
            'statusCode': 200,
            'body': json.dumps('SQS events processed successfully')
        }
        
    except Exception as e:
        logger.error(f"Error processing SQS event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
