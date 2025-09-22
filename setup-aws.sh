#!/bin/bash

# AWS Services Initialization Script with Retry Logic
# This script ensures all AWS services are properly initialized with robust error handling

set -e  # Exit on any error

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Wait for a specific service with exponential backoff
wait_for_service() {
    local service_name=$1
    local test_command=$2
    local max_attempts=${3:-20}
    local base_delay=${4:-2}
    local attempt=1
    
    log_info "Testing $service_name availability..."
    
    while [ $attempt -le $max_attempts ]; do
        if eval "$test_command" > /dev/null 2>&1; then
            log_success "$service_name is ready after $attempt attempts"
            return 0
        fi
        
        # Exponential backoff with jitter
        delay=$((base_delay * (2 ** (attempt - 1))))
        # Add jitter: ±25% random variation to prevent thundering herd
        jitter=$((RANDOM % (delay / 4)))
        actual_delay=$((delay + jitter))
        
        # Cap maximum delay at 30 seconds
        if [ $actual_delay -gt 30 ]; then
            actual_delay=30
        fi
        
        log_warning "$service_name not ready, waiting ${actual_delay}s (attempt $attempt/$max_attempts)"
        sleep $actual_delay
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Test LocalStack connectivity
test_localstack_connectivity() {
    log_info "Testing LocalStack connectivity..."
    wait_for_service "LocalStack" "aws sts get-caller-identity" 15 3
}

# Test individual AWS services
test_s3_service() {
    log_info "Testing S3 service..."
    wait_for_service "S3" "aws s3 ls" 15 2
}

test_sqs_service() {
    log_info "Testing SQS service..."
    wait_for_service "SQS" "aws sqs list-queues" 15 2
}

test_lambda_service() {
    log_info "Testing Lambda service..."
    wait_for_service "Lambda" "aws lambda list-functions" 20 3
}

test_secrets_manager_service() {
    log_info "Testing Secrets Manager service..."
    wait_for_service "Secrets Manager" "aws secretsmanager list-secrets" 15 2
}

# Create AWS resources with retry logic
create_sqs_queue() {
    local max_attempts=5
    local attempt=1
    
    log_info "Creating SQS queue: w2-file-events-queue"
    
    while [ $attempt -le $max_attempts ]; do
        if aws sqs create-queue --queue-name w2-file-events-queue > /dev/null 2>&1; then
            log_success "SQS queue created successfully"
            return 0
        else
            log_warning "Failed to create SQS queue (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Failed to create SQS queue after $max_attempts attempts"
    return 1
}

create_s3_bucket() {
    local max_attempts=5
    local attempt=1
    
    log_info "Creating S3 bucket: w2-bucket"
    
    while [ $attempt -le $max_attempts ]; do
        if aws s3 mb s3://w2-bucket > /dev/null 2>&1; then
            log_success "S3 bucket created successfully"
            return 0
        else
            # Check if bucket already exists
            if aws s3 ls s3://w2-bucket > /dev/null 2>&1; then
                log_success "S3 bucket already exists"
                return 0
            fi
            log_warning "Failed to create S3 bucket (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Failed to create S3 bucket after $max_attempts attempts"
    return 1
}

create_secret() {
    local max_attempts=5
    local attempt=1
    
    log_info "Creating secret: external-api-key"
    
    # Generate API key
    API_KEY=$(openssl rand -hex 32)
    log_info "Generated API Key: ${API_KEY:0:8}..."
    
    while [ $attempt -le $max_attempts ]; do
        if aws secretsmanager create-secret \
            --name 'external-api-key' \
            --description 'API key for external services' \
            --secret-string "{\"api_key\": \"$API_KEY\", \"created_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" > /dev/null 2>&1; then
            log_success "Secret created successfully"
            return 0
        else
            # Check if secret already exists
            if aws secretsmanager describe-secret --secret-id 'external-api-key' > /dev/null 2>&1; then
                log_success "Secret already exists"
                return 0
            fi
            log_warning "Failed to create secret (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Failed to create secret after $max_attempts attempts"
    return 1
}

# Configure S3 events with retry logic
configure_s3_events() {
    local max_attempts=5
    local attempt=1
    
    log_info "Configuring S3 bucket events..."
    
    while [ $attempt -le $max_attempts ]; do
        # Get queue URL and ARN
        QUEUE_URL=$(aws sqs get-queue-url --queue-name w2-file-events-queue --query 'QueueUrl' --output text 2>/dev/null)
        if [ -z "$QUEUE_URL" ]; then
            log_warning "Failed to get queue URL (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
            continue
        fi
        
        QUEUE_ARN=$(aws sqs get-queue-attributes --queue-url "$QUEUE_URL" --attribute-names QueueArn --query 'Attributes.QueueArn' --output text 2>/dev/null)
        if [ -z "$QUEUE_ARN" ]; then
            log_warning "Failed to get queue ARN (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
            continue
        fi
        
        # Configure S3 events
        if aws s3api put-bucket-notification-configuration \
            --bucket w2-bucket \
            --notification-configuration "{
                \"QueueConfigurations\": [
                    {
                        \"Id\": \"w2-file-events\",
                        \"QueueArn\": \"$QUEUE_ARN\",
                        \"Events\": [\"s3:ObjectCreated:*\"],
                        \"Filter\": {
                            \"Key\": {
                                \"FilterRules\": [
                                    {
                                        \"Name\": \"prefix\",
                                        \"Value\": \"uploads/\"
                                    }
                                ]
                            }
                        }
                    }
                ]
            }" > /dev/null 2>&1; then
            log_success "S3 events configured successfully"
            return 0
        else
            log_warning "Failed to configure S3 events (attempt $attempt/$max_attempts)"
            sleep 3
            attempt=$((attempt + 1))
        fi
    done
    
    log_error "Failed to configure S3 events after $max_attempts attempts"
    return 1
}

# Verify all services are working
verify_services() {
    log_info "Verifying all services..."
    
    # List resources to verify they exist
    log_info "SQS Queues:"
    aws sqs list-queues --query 'QueueUrls[]' --output table
    
    log_info "S3 Buckets:"
    aws s3 ls
    
    log_info "Secrets:"
    aws secretsmanager list-secrets --query 'SecretList[].Name' --output table
    
    log_success "All services verified!"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 Starting AWS services initialization with retry logic...${NC}"
    echo "=================================================="
    
    # Test LocalStack connectivity
    test_localstack_connectivity
    
    # Test individual services
    test_s3_service
    test_sqs_service
    test_lambda_service
    test_secrets_manager_service
    
    log_success "All LocalStack services are ready!"
    echo "=================================================="
    
    # Create AWS resources
    create_sqs_queue
    create_s3_bucket
    create_secret
    configure_s3_events
    
    echo "=================================================="
    verify_services
    
    echo "=================================================="
    log_success "🎉 AWS setup complete! All services initialized successfully."
    echo -e "${GREEN}📊 Summary:${NC}"
    echo "  ✅ SQS Queue: w2-file-events-queue"
    echo "  ✅ S3 Bucket: w2-bucket"
    echo "  ✅ S3 Events: Configured"
    echo "  ✅ Secrets Manager: external-api-key"
    echo "  ✅ All services verified and ready"
}

# Run main function
main "$@"
