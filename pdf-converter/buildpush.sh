#!/bin/bash

# Configuration
ECR_REPOSITORY="batch-poc-pdfconverter"
AWS_REGION="eu-central-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
IMAGE_TAG="latest"

# Full ECR URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "Building and pushing PDF converter to ECR..."
echo "Repository: ${ECR_URI}"

# Get ECR login token
echo "Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build the image
echo "Building Docker image..."
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

# Tag for ECR
echo "Tagging image for ECR..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Push to ECR
echo "Pushing to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

echo "✅ Successfully pushed ${ECR_URI}:${IMAGE_TAG}"
EOF