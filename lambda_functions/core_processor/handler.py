import json
import logging
import os
import requests
from urllib.parse import unquote_plus

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def extract_job_id(object_key):
    """Extract job_id from S3 object key"""
    # "uploads/job_id/w2.pdf" -> "job_id"
    decoded_key = unquote_plus(object_key)
    path_parts = decoded_key.split('/')
    
    if len(path_parts) >= 3 and path_parts[0] == 'uploads':
        return path_parts[1]
    else:
        return "unknown"

def placeholder_processing_function(job_id, object_key):
    """Placeholder function for future processing logic"""
    logger.info(f"Processing job {job_id} with file {object_key}")
    # TODO: Add actual processing logic here
    pass

def update_job_status(job_id, updates):
    """Helper function to update job via API"""
    django_url = f"http://backend:8000/jobs/{job_id}/"
    response = requests.patch(django_url, json=updates)
    
    if response.status_code == 200:
        logger.info(f"✅ Successfully updated job {job_id}")
        return True
    else:
        logger.error(f"❌ Failed to update job {job_id}: {response.text}")
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
        if not update_job_status(job_id, {"file_uploaded": True}):
            return {"statusCode": 500, "body": "Failed to mark file as uploaded"}
        
        # Phase 2: Call processing function
        placeholder_processing_function(job_id, object_key)
        
        # Phase 3: Mark as completed
        if not update_job_status(job_id, {"status": "Success"}):
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
