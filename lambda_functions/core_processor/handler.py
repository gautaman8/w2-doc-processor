import json
import logging
import os
import requests
import boto3
from datetime import datetime
from urllib.parse import unquote_plus
from w2_extractor import extract_w2_data, validate_w2_data

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SQS client
sqs = boto3.client('sqs', endpoint_url='http://localstack:4566', region_name='us-east-1')

def extract_job_id(object_key):
    """Extract job_id from S3 object key"""
    # "uploads/job_id/w2.pdf" -> "job_id"
    decoded_key = unquote_plus(object_key)
    path_parts = decoded_key.split('/')
    
    if len(path_parts) >= 3 and path_parts[0] == 'uploads':
        return path_parts[1]
    else:
        return "unknown"

def process_w2_file(job_id, object_key):
    """Process W2 file and extract data"""
    logger.info(f"Processing W2 file for job {job_id} with file {object_key}")
    
    try:
        # Extract W2 data from the file
        w2_data = extract_w2_data(object_key)
        
        # Validate extracted data
        validate_w2_data(w2_data)
        
        # Convert Decimal to string for JSON serialization
        w2_data_serializable = {}
        for key, value in w2_data.items():
            if hasattr(value, 'quantize'):  # Check if it's a Decimal
                w2_data_serializable[key] = str(value)
            else:
                w2_data_serializable[key] = value
        
        # Update job with extracted W2 data
        update_payload = {
            "w2_data": w2_data_serializable
        }
        
        if not update_job(job_id, update_payload):
            raise Exception("Failed to update job with W2 data")
        
        logger.info(f"✅ Successfully extracted and stored W2 data for job {job_id}")
        return w2_data_serializable
        
    except Exception as e:
        logger.error(f"❌ Error processing W2 file for job {job_id}: {str(e)}")
        raise e

def update_job(job_id, updates):
    """Helper function to update job via API"""
    django_url = f"http://backend:8000/jobs/{job_id}/"
    response = requests.patch(django_url, json=updates)
    
    if response.status_code == 200:
        logger.info(f"✅ Successfully updated job {job_id}")
        return True
    else:
        logger.error(f"❌ Failed to update job {job_id}: {response.text}")
        return False

def publish_external_events(job_id, object_key, w2_data):
    """Publish external upload and data update events to SQS"""
    try:
        # Get SQS queue URL
        queue_url = sqs.get_queue_url(QueueName='w2-file-events-queue')['QueueUrl']
        
        # Prepare S3 URL
        s3_url = f"s3://w2-bucket/{object_key}"
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Event 1: external_upload
        external_upload_event = {
            "event_type": "external_upload",
            "job_id": job_id,
            "s3_url": s3_url,
            "timestamp": timestamp
        }
        
        # Event 2: external_data_update
        external_data_update_event = {
            "event_type": "external_data_update",
            "job_id": job_id,
            "w2_data": w2_data,
            "timestamp": timestamp
        }
        
        # Send both events to SQS
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(external_upload_event)
        )
        
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(external_data_update_event)
        )
        
        logger.info(f"✅ Published external events for job {job_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to publish external events for job {job_id}: {str(e)}")
        return False

def lambda_handler(event, context):
    """
    Core Processor Lambda function
    Processes individual file events and updates job status
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract event details
        bucket_name = event.get('bucket_name')
        object_key = event.get('object_key')
        event_name = event.get('event_name')
        timestamp = event.get('timestamp')
        
        # Extract job_id from object key
        job_id = extract_job_id(object_key)
        
        if job_id == "unknown":
            logger.error(f"Could not extract job_id from object_key: {object_key}")
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid object key format')
            }
        
        logger.info(f"Processing job: {job_id}")
        
        # Phase 1: Mark file as uploaded
        if not update_job(job_id, {"file_uploaded": True}):
            return {"statusCode": 500, "body": "Failed to mark file as uploaded"}
        
        # Phase 2: Process W2 file and extract data
        w2_data = process_w2_file(job_id, object_key)
        
        # Phase 3: Publish external events
        publish_external_events(job_id, object_key, w2_data)
        
        # Phase 4: Mark as completed
        if not update_job(job_id, {"status": "Success"}):
            return {"statusCode": 500, "body": "Failed to mark job as completed"}
        
        # Log success
        logger.info(f"✅ Successfully processed job {job_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Job processed successfully',
                'job_id': job_id,
                'file_uploaded': True,
                'status': 'Success'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing file event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
