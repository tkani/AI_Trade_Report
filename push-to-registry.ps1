# PowerShell script to push Docker image to registry
# Usage: .\push-to-registry.ps1 -Registry "your-registry" -Tag "your-tag"

param(
    [string]$Registry = "your-dockerhub-username",
    [string]$Tag = "latest"
)

Write-Host "🚀 Pushing AI Trade Report Docker image to registry..." -ForegroundColor Green

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Tag the image for the registry
$ImageName = "$Registry/ai-trade-report:$Tag"
Write-Host "📦 Tagging image as: $ImageName" -ForegroundColor Yellow

try {
    docker tag ai-trade-report:latest $ImageName
    Write-Host "✅ Image tagged successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to tag image" -ForegroundColor Red
    exit 1
}

# Push to registry
Write-Host "🚀 Pushing image to registry..." -ForegroundColor Yellow
try {
    docker push $ImageName
    Write-Host "✅ Image pushed successfully!" -ForegroundColor Green
    Write-Host "🌐 Image is now available at: $ImageName" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to push image. Make sure you're logged in to the registry." -ForegroundColor Red
    Write-Host "💡 To login to Docker Hub, run: docker login" -ForegroundColor Yellow
    exit 1
}

Write-Host "🎉 Push completed successfully!" -ForegroundColor Green
