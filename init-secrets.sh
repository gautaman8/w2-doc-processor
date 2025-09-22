#!/bin/bash

# Initialize AWS Secrets Manager with random API key
echo "🔐 Initializing AWS Secrets Manager..."

# Generate a random API key
API_KEY=$(openssl rand -hex 32)
echo "Generated API Key: ${API_KEY:0:8}..." # Show first 8 chars for verification

# Create secret in AWS Secrets Manager
aws --endpoint-url=http://localhost:4566 \
    --region=us-east-1 \
    secretsmanager create-secret \
    --name "external-api-key" \
    --description "API key for external services" \
    --secret-string "{\"api_key\": \"$API_KEY\", \"created_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

if [ $? -eq 0 ]; then
    echo "✅ Secret 'external-api-key' created successfully"
    echo "🔑 API Key stored securely in AWS Secrets Manager"
else
    echo "❌ Failed to create secret"
    exit 1
fi

# Verify the secret was created
echo "🔍 Verifying secret creation..."
aws --endpoint-url=http://localhost:4566 \
    --region=us-east-1 \
    secretsmanager describe-secret \
    --secret-id "external-api-key"

echo "🎉 Secrets Manager initialization complete!"
