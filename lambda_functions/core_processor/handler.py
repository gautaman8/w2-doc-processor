import json
import logging
import os
import requests
import boto3
from datetime import datetime
from urllib.parse import unquote_plus
from w2_extractor import extract_w2_data, validate_w2_data
from external_api_client import call_external_upload_api, call_external_data_update_api

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SQS client
sqs = boto3.client('sqs', endpoint_url='http://localstack:4566', region_name='us-east-1')

def update_w2_data_status(job_id, status, message=None):
    """Update W2 data processing status (simplified: success/failure only)"""
    try:
        update_payload = {
            "w2_data_status": status,
            "w2_data_status_msg": message
        }
        
        if update_job(job_id, update_payload):
            logger.info(f"Updated W2 data status for job {job_id}: {status} - {message}")
            return True
        else:
            logger.error(f"Failed to update W2 data status for job {job_id}")
            return False
    except Exception as e:
        logger.error(f"Error updating W2 data status for job {job_id}: {str(e)}")
        return False

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
        
        # Update status to success
        update_w2_data_status(job_id, 'success', 'W2 data extracted successfully')
        
        logger.info(f"✅ Successfully extracted and stored W2 data for job {job_id}")
        return w2_data_serializable
        
    except Exception as e:
        error_msg = f"W2 extraction failed: {str(e)}"
        logger.error(f"❌ Error processing W2 file for job {job_id}: {error_msg}")
        
        # Update status to failed
        update_w2_data_status(job_id, 'failed', error_msg)
        
        # Re-raise exception to trigger SQS retry
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
    Handles different event types: s3_upload, external_upload, external_data_update
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        event_type = event.get('event_type', 's3_upload')  # Default to s3_upload for backward compatibility
        
        if event_type == 's3_upload':
            return handle_s3_upload(event)
        elif event_type == 'external_upload':
            return handle_external_upload(event)
        elif event_type == 'external_data_update':
            return handle_external_data_update(event)
        else:
            logger.warning(f"Unknown event type: {event_type}, defaulting to s3_upload")
            return handle_s3_upload(event)
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def handle_s3_upload(event):
    """Handle S3 upload events - original W2 processing logic"""
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
        
        logger.info(f"Processing S3 upload for job: {job_id}")
        
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
        logger.info(f"✅ Successfully processed S3 upload for job {job_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'S3 upload processed successfully',
                'job_id': job_id,
                'file_uploaded': True,
                'status': 'Success'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing S3 upload: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def handle_external_upload(event):
    """Handle external upload events"""
    try:
        job_id = event.get('job_id')
        s3_url = event.get('s3_url')
        
        if not job_id or not s3_url:
            logger.error(f"Missing required fields in external_upload event: {event}")
            return {
                'statusCode': 400,
                'body': json.dumps('Missing job_id or s3_url')
            }
        
        logger.info(f"Processing external upload for job: {job_id}")
        
        # Call external upload API
        api_result = call_external_upload_api(s3_url, job_id)
        
        if api_result['success']:
            # Update database with success
            if update_job(job_id, {"external_upload": True}):
                update_w2_data_status(job_id, 'success', 'External upload completed successfully')
                logger.info(f"✅ Successfully processed external upload for job {job_id}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'External upload processed successfully',
                        'job_id': job_id,
                        'file_id': api_result.get('file_id')
                    })
                }
            else:
                error_msg = "Failed to update database after external upload"
                update_w2_data_status(job_id, 'failed', error_msg)
                logger.error(f"❌ Failed to update database for external upload job {job_id}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('Failed to update database')
                }
        else:
            error_msg = f"External upload API failed: {api_result.get('error')}"
            update_w2_data_status(job_id, 'failed', error_msg)
            logger.error(f"❌ External upload API failed for job {job_id}: {api_result.get('error')}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"External API failed: {api_result.get('error')}")
            }
            
    except Exception as e:
        logger.error(f"Error processing external upload: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def handle_external_data_update(event):
    """Handle external data update events"""
    try:
        job_id = event.get('job_id')
        w2_data = event.get('w2_data')
        
        if not job_id or not w2_data:
            logger.error(f"Missing required fields in external_data_update event: {event}")
            return {
                'statusCode': 400,
                'body': json.dumps('Missing job_id or w2_data')
            }
        
        logger.info(f"Processing external data update for job: {job_id}")
        
        # Call external data update API
        api_result = call_external_data_update_api(w2_data, job_id)
        
        if api_result['success']:
            # Update database with success
            if update_job(job_id, {"external_data_update": True}):
                update_w2_data_status(job_id, 'success', 'External data update completed successfully')
                logger.info(f"✅ Successfully processed external data update for job {job_id}")
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'External data update processed successfully',
                        'job_id': job_id,
                        'report_id': api_result.get('report_id'),
                        'file_id': api_result.get('file_id')
                    })
                }
            else:
                error_msg = "Failed to update database after external data update"
                update_w2_data_status(job_id, 'failed', error_msg)
                logger.error(f"❌ Failed to update database for external data update job {job_id}")
                return {
                    'statusCode': 500,
                    'body': json.dumps('Failed to update database')
                }
        else:
            error_msg = f"External data update API failed: {api_result.get('error')}"
            update_w2_data_status(job_id, 'failed', error_msg)
            logger.error(f"❌ External data update API failed for job {job_id}: {api_result.get('error')}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"External API failed: {api_result.get('error')}")
            }
            
    except Exception as e:
        logger.error(f"Error processing external data update: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
