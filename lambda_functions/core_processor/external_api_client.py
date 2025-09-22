import logging
import requests
import uuid
import json
import boto3
from datetime import datetime
from unittest.mock import patch, Mock

logger = logging.getLogger()

# External API configuration
EXTERNAL_API_BASE_URL = "http://external-api:8080"

# Initialize AWS Secrets Manager client
secrets_client = boto3.client('secretsmanager', endpoint_url='http://localstack:4566', region_name='us-east-1')

def get_api_key():
    """
    Retrieve API key from AWS Secrets Manager
    """
    try:
        logger.info("🔐 Retrieving API key from AWS Secrets Manager...")
        
        response = secrets_client.get_secret_value(SecretId='external-api-key')
        secret_data = json.loads(response['SecretString'])
        api_key = secret_data.get('api_key')
        
        if api_key:
            logger.info(f"✅ API key retrieved successfully: {api_key[:8]}...")
            return api_key
        else:
            logger.error("❌ API key not found in secret")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error retrieving API key from Secrets Manager: {str(e)}")
        return None

def call_external_upload_api(s3_url, job_id):
    """
    Call external upload API
    Mock API: POST http://external-api:8080/external/file-upload
    """
    try:
        # Get API key from Secrets Manager
        api_key = get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'Failed to retrieve API key from Secrets Manager'
            }
        
        url = f"{EXTERNAL_API_BASE_URL}/external/file-upload"
        payload = {
            "s3_url": s3_url,
            "job_id": job_id
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"🌐 Calling external upload API: {url}")
        logger.info(f"📤 Upload payload: {payload}")
        logger.info(f"🔑 Using API key: {api_key[:8]}...")
        
        # Mock the requests.post call
        with patch('requests.post') as mock_post:
            # Configure mock response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                'file_id': str(uuid.uuid4()),
                'status': 'uploaded',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            mock_post.return_value = mock_response
            
            # Make the actual call (which will be mocked)
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"📥 Upload API response: {response_data}")
            
            return {
                'success': True,
                'file_id': response_data.get('file_id'),
                'status': response_data.get('status')
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error calling external upload API: {str(e)}")
        return {
            'success': False,
            'error': f"Request failed: {str(e)}"
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
        # Get API key from Secrets Manager
        api_key = get_api_key()
        if not api_key:
            return {
                'success': False,
                'error': 'Failed to retrieve API key from Secrets Manager'
            }
        
        url = f"{EXTERNAL_API_BASE_URL}/external/data-update"
        payload = {
            "w2_data": w2_data,
            "job_id": job_id
        }
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"🌐 Calling external data update API: {url}")
        logger.info(f"📤 Data update payload: {payload}")
        logger.info(f"🔑 Using API key: {api_key[:8]}...")
        
        # Mock the requests.post call
        with patch('requests.post') as mock_post:
            # Configure mock response
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {
                'report_id': job_id,  # Use job_id as report_id
                'file_id': str(uuid.uuid4()),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            mock_post.return_value = mock_response
            
            # Make the actual call (which will be mocked)
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"📥 Data update API response: {response_data}")
            
            return {
                'success': True,
                'report_id': response_data.get('report_id'),
                'file_id': response_data.get('file_id')
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Request error calling external data update API: {str(e)}")
        return {
            'success': False,
            'error': f"Request failed: {str(e)}"
        }
    except Exception as e:
        logger.error(f"❌ Error calling external data update API: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
