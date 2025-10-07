#!/bin/bash

# Bash script to push Docker image to registry
# Usage: ./push-to-registry.sh your-registry your-tag

REGISTRY=${1:-"your-dockerhub-username"}
TAG=${2:-"latest"}

echo "🚀 Pushing AI Trade Report Docker image to registry..."

# Check if Docker is running
if ! docker version >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

echo "✅ Docker is running"

# Tag the image for the registry
IMAGE_NAME="$REGISTRY/ai-trade-report:$TAG"
echo "📦 Tagging image as: $IMAGE_NAME"

if ! docker tag ai-trade-report:latest "$IMAGE_NAME"; then
    echo "❌ Failed to tag image"
    exit 1
fi

echo "✅ Image tagged successfully"

# Push to registry
echo "🚀 Pushing image to registry..."
if ! docker push "$IMAGE_NAME"; then
    echo "❌ Failed to push image. Make sure you're logged in to the registry."
    echo "💡 To login to Docker Hub, run: docker login"
    exit 1
fi

echo "✅ Image pushed successfully!"
echo "🌐 Image is now available at: $IMAGE_NAME"
echo "🎉 Push completed successfully!"
