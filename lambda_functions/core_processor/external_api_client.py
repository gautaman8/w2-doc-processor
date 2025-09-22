import logging
import requests
import uuid
from datetime import datetime

logger = logging.getLogger()

# External API configuration
EXTERNAL_API_BASE_URL = "http://external-api:8080"

def call_external_upload_api(s3_url, job_id):
    """
    Call external upload API
    Mock API: POST http://external-api:8080/external/file-upload
    """
    try:
        url = f"{EXTERNAL_API_BASE_URL}/external/file-upload"
        payload = {
            "s3_url": s3_url,
            "job_id": job_id
        }
        
        logger.info(f"🌐 Calling external upload API: {url}")
        logger.info(f"📤 Upload payload: {payload}")
        
        # Mock API call - simulate external service
        response = mock_external_upload_api(payload)
        
        logger.info(f"📥 Upload API response: {response}")
        
        if response.get('status_code') == 201:
            return {
                'success': True,
                'file_id': response.get('file_id'),
                'status': response.get('status')
            }
        else:
            return {
                'success': False,
                'error': f"API returned status {response.get('status_code')}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error calling external upload API: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def call_external_data_update_api(w2_data, job_id):
    """
    Call external data update API
    Mock API: POST http://external-api:8080/external/data-update
    """
    try:
        url = f"{EXTERNAL_API_BASE_URL}/external/data-update"
        payload = {
            "w2_data": w2_data,
            "job_id": job_id
        }
        
        logger.info(f"🌐 Calling external data update API: {url}")
        logger.info(f"📤 Data update payload: {payload}")
        
        # Mock API call - simulate external service
        response = mock_external_data_update_api(payload)
        
        logger.info(f"📥 Data update API response: {response}")
        
        if response.get('status_code') == 201:
            return {
                'success': True,
                'report_id': response.get('report_id'),
                'file_id': response.get('file_id')
            }
        else:
            return {
                'success': False,
                'error': f"API returned status {response.get('status_code')}"
            }
            
    except Exception as e:
        logger.error(f"❌ Error calling external data update API: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def mock_external_upload_api(payload):
    """
    Mock external upload API response
    Simulates: POST /external/file-upload
    """
    # Generate random file_id
    file_id = str(uuid.uuid4())
    
    # Simulate API response
    return {
        'status_code': 201,
        'file_id': file_id,
        'status': 'uploaded',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

def mock_external_data_update_api(payload):
    """
    Mock external data update API response
    Simulates: POST /external/data-update
    """
    # Generate random file_id
    file_id = str(uuid.uuid4())
    job_id = payload.get('job_id')
    
    # Simulate API response
    return {
        'status_code': 201,
        'report_id': job_id,  # Use job_id as report_id
        'file_id': file_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
