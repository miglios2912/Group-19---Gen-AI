#!/bin/bash

# =============================================================================
# TUM Chatbot V2 - Google Cloud Run Deployment Script
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO V2]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS V2]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR V2]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING V2]${NC} $1"
}

# Configuration
PROJECT_ID="tum-chatbot-1751400946"
REGION="europe-west3"  # Frankfurt, Germany
SERVICE_NAME="tum-chatbot"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

print_status "🚀 TUM Chatbot V2 (Smart Context) - Cloud Run Deployment"
echo "=========================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if API key is set - use existing .env file
if [ -f ".env" ]; then
    print_status "Using existing .env file for configuration"
    source .env
elif [ -f ".env.production" ]; then
    print_status "Using .env.production file for configuration"
    source .env.production
else
    print_error "No .env file found!"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    print_error "Please set your GEMINI_API_KEY in .env file"
    exit 1
fi

print_status "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Service Name: $SERVICE_NAME (V2)"
echo "  Image: $IMAGE_NAME"
echo "  API Key: ${GEMINI_API_KEY:0:20}..."
echo ""
print_status "V2 Features:"
echo "  ✓ Smart context detection (only asks necessary questions)"
echo "  ✓ Campus-only questions: Just asks campus"
echo "  ✓ Role-dependent questions: Asks role + campus when needed"
echo "  ✓ General questions: No context needed"
echo "  ✓ Interactive campus maps with 4 campuses"
echo "  ✓ Session persistence across conversations"
echo ""
print_warning "This will UPDATE the existing tum-chatbot service to V2"
print_warning "The current V1 will be replaced with V2 (with all fixes)"
echo ""

read -p "Proceed with V2 deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "V2 deployment cancelled"
    exit 0
fi

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

# Build and push Docker image
print_status "Building V2 Docker image for linux/amd64..."
docker build --platform linux/amd64 -f Dockerfile.cloudrun.v2 -t $IMAGE_NAME .

print_status "Pushing V2 image to Google Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
print_status "Deploying V2 to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,FLASK_ENV=production \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --max-instances 10 \
    --port 8080 \
    --project $PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project $PROJECT_ID)

print_success "🎉 V2 Deployment completed successfully!"
echo "==========================================="
print_success "🌐 Your TUM Chatbot V2 is live at: $SERVICE_URL"
print_success "🔧 V2 API Health Check: $SERVICE_URL/api/v2/health"
print_success "📱 V2 Chat Interface: $SERVICE_URL"
echo ""
print_status "V2 Smart Context Features:"
echo "  • Only asks campus for campus-specific questions"
echo "  • Only asks role+campus for role-dependent questions"
echo "  • No context needed for general questions"
echo "  • Interactive campus maps for all 4 campuses"
echo "  • Session persistence across conversations"
echo ""
print_status "Cloud Run Dashboard (V2):"
echo "https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
echo ""
print_status "Both V1 and V2 are now running:"
echo "  V1: https://tum-chatbot-xxx.a.run.app (original)"
echo "  V2: $SERVICE_URL (smart context)"
echo ""
print_status "To update V2 deployment:"
echo "1. Make your changes"
echo "2. Run this script again"
echo ""
print_status "To delete V2 service:"
echo "gcloud run services delete $SERVICE_NAME --region $REGION --project $PROJECT_ID"
echo ""
print_status "To delete V1 service (if you want to keep only V2):"
echo "gcloud run services delete tum-chatbot --region $REGION --project $PROJECT_ID"