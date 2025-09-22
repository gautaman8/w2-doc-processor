#!/bin/bash

# Quick start script with retry mechanism
echo "🚀 Quick Start: Starting all services with retry logic..."

# Start all services
docker-compose up -d

# Wait for LocalStack to be ready
echo "⏳ Waiting for LocalStack to initialize..."
sleep 10

# Run AWS setup with retry logic
echo "🔧 Setting up AWS services..."
./setup-aws.sh

# Deploy Lambda functions
echo "📦 Deploying Lambda functions..."
./deploy-lambdas.sh

# Configure SQS-Lambda trigger
echo "🔗 Configuring SQS-Lambda trigger..."
./configure-sqs-lambda.sh

echo "🎉 All services are ready!"
echo "📊 Services running:"
echo "  🌐 Frontend: http://localhost:8501"
echo "  🔧 Backend: http://localhost:8000"
echo "  ☁️  LocalStack: http://localhost:4566"
