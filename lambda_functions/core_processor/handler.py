import json
import logging
import os
from urllib.parse import unquote_plus

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Core Processor Lambda function
    Processes individual file events and logs folder information
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract event details
        bucket_name = event.get('bucket_name')
        object_key = event.get('object_key')
        event_name = event.get('event_name')
        timestamp = event.get('timestamp')
        
        # Decode the object key (URL decode)
        decoded_key = unquote_plus(object_key)
        
        # Extract folder path from object key
        # Expected format: uploads/{job_id}/filename.pdf
        path_parts = decoded_key.split('/')
        
        if len(path_parts) >= 3 and path_parts[0] == 'uploads':
            job_id = path_parts[1]
            filename = path_parts[2]
            folder_path = f"uploads/{job_id}/"
        else:
            # Fallback for unexpected path structure
            job_id = "unknown"
            filename = path_parts[-1] if path_parts else "unknown"
            folder_path = "/".join(path_parts[:-1]) + "/" if len(path_parts) > 1 else ""
        
        # Log the folder information
        log_message = {
            'event_type': 'file_upload_processed',
            'bucket_name': bucket_name,
            'object_key': decoded_key,
            'job_id': job_id,
            'filename': filename,
            'folder_path': folder_path,
            'event_name': event_name,
            'timestamp': timestamp,
            'lambda_function': 'core-processor'
        }
        
        logger.info(f"File upload processed: {json.dumps(log_message)}")
        
        # Print to console for easy viewing
        print(f"📁 FOLDER DETECTED: {folder_path}")
        print(f"📄 FILENAME: {filename}")
        print(f"🆔 JOB ID: {job_id}")
        print(f"🪣 BUCKET: {bucket_name}")
        print(f"⏰ TIMESTAMP: {timestamp}")
        print("-" * 50)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File processed successfully',
                'job_id': job_id,
                'folder_path': folder_path,
                'filename': filename
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing file event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }
