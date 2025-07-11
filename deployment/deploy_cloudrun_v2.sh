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
elif [ -f "backend/.env" ]; then
    print_status "Using backend/.env file for configuration"
    source backend/.env
elif [ -f "backend/.env.production" ]; then
    print_status "Using backend/.env.production file for configuration"
    source backend/.env.production
else
    print_error "No .env file found in root or backend directory!"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    print_error "Please set your GEMINI_API_KEY in .env file"
    exit 1
fi

# Set default values for missing environment variables
ENVIRONMENT=${ENVIRONMENT:-production}
FLASK_ENV=${FLASK_ENV:-production}
GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}
GEMINI_MAX_TOKENS=${GEMINI_MAX_TOKENS:-4096}
GEMINI_TEMPERATURE=${GEMINI_TEMPERATURE:-0.7}
SEMANTIC_SEARCH_TOP_K=${SEMANTIC_SEARCH_TOP_K:-5}
KEYWORD_SEARCH_TOP_K=${KEYWORD_SEARCH_TOP_K:-5}
HYBRID_SEARCH_TOP_K=${HYBRID_SEARCH_TOP_K:-5}
EMBEDDING_MODEL=${EMBEDDING_MODEL:-all-MiniLM-L6-v2}
SIMILARITY_THRESHOLD=${SIMILARITY_THRESHOLD:-0.3}
LOG_LEVEL=${LOG_LEVEL:-WARNING}
ENABLE_SECURITY=${ENABLE_SECURITY:-True}
ENABLE_RATE_LIMITING=${ENABLE_RATE_LIMITING:-True}
ENABLE_CORS=${ENABLE_CORS:-True}
ENABLE_STATISTICS=${ENABLE_STATISTICS:-True}
LOG_CHAT_SESSIONS=${LOG_CHAT_SESSIONS:-False}
ENABLE_PROMPT_INJECTION_DETECTION=${ENABLE_PROMPT_INJECTION_DETECTION:-True}
DETECTION_CONFIDENCE_THRESHOLD=${DETECTION_CONFIDENCE_THRESHOLD:-0.8}
VIOLATION_THRESHOLD=${VIOLATION_THRESHOLD:-2}
RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-3600}
SESSION_TIMEOUT=${SESSION_TIMEOUT:-3600}
MAX_CONTEXT_LENGTH=${MAX_CONTEXT_LENGTH:-4000}
CONVERSATION_HISTORY_LIMIT=${CONVERSATION_HISTORY_LIMIT:-12}

# Database paths (production paths)
CHROMA_DB_PATH=${CHROMA_DB_PATH:-/app/data/chroma_db}
CHROMA_COLLECTION_NAME=${CHROMA_COLLECTION_NAME:-tum_qa_collection}
CHROMA_PERSIST_DIR=${CHROMA_PERSIST_DIR:-/app/data/chroma_db}
BLACKLIST_DB_PATH=${BLACKLIST_DB_PATH:-/app/data/security.db}
STATS_DB_PATH=${STATS_DB_PATH:-/app/data/statistics.db}

# Knowledge base path
KNOWLEDGE_BASE_PATH=${KNOWLEDGE_BASE_PATH:-/app/TUM_QA.json}

# Logging configuration
LOG_FILE=${LOG_FILE:-/app/logs/tum_chatbot.log}
LOG_FORMAT=${LOG_FORMAT:-%(asctime)s - %(name)s - %(levelname)s - %(message)s}
MAX_LOG_SIZE=${MAX_LOG_SIZE:-10485760}
LOG_BACKUP_COUNT=${LOG_BACKUP_COUNT:-5}
CHAT_SESSION_FILE=${CHAT_SESSION_FILE:-/app/logs/chat_sessions.log}

# CORS configuration
CORS_ORIGINS=${CORS_ORIGINS:-*}

# Statistics and analytics
TRACK_USER_SESSIONS=${TRACK_USER_SESSIONS:-True}
TRACK_QUERY_ANALYTICS=${TRACK_QUERY_ANALYTICS:-True}
ANONYMIZE_DATA=${ANONYMIZE_DATA:-True}

# Server configuration
SERVER_HOST=${SERVER_HOST:-0.0.0.0}
SERVER_PORT=${SERVER_PORT:-8080}
REQUEST_TIMEOUT=${REQUEST_TIMEOUT:-30}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-1}

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
    --set-env-vars ENVIRONMENT=$ENVIRONMENT,FLASK_ENV=$FLASK_ENV \
    --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
    --set-env-vars GEMINI_MODEL=$GEMINI_MODEL \
    --set-env-vars GEMINI_MAX_TOKENS=$GEMINI_MAX_TOKENS \
    --set-env-vars GEMINI_TEMPERATURE=$GEMINI_TEMPERATURE \
    --set-env-vars SEMANTIC_SEARCH_TOP_K=$SEMANTIC_SEARCH_TOP_K \
    --set-env-vars KEYWORD_SEARCH_TOP_K=$KEYWORD_SEARCH_TOP_K \
    --set-env-vars HYBRID_SEARCH_TOP_K=$HYBRID_SEARCH_TOP_K \
    --set-env-vars EMBEDDING_MODEL=$EMBEDDING_MODEL \
    --set-env-vars SIMILARITY_THRESHOLD=$SIMILARITY_THRESHOLD \
    --set-env-vars LOG_LEVEL=$LOG_LEVEL \
    --set-env-vars ENABLE_SECURITY=$ENABLE_SECURITY \
    --set-env-vars ENABLE_RATE_LIMITING=$ENABLE_RATE_LIMITING \
    --set-env-vars ENABLE_CORS=$ENABLE_CORS \
    --set-env-vars ENABLE_STATISTICS=$ENABLE_STATISTICS \
    --set-env-vars LOG_CHAT_SESSIONS=$LOG_CHAT_SESSIONS \
    --set-env-vars ENABLE_PROMPT_INJECTION_DETECTION=$ENABLE_PROMPT_INJECTION_DETECTION \
    --set-env-vars DETECTION_CONFIDENCE_THRESHOLD=$DETECTION_CONFIDENCE_THRESHOLD \
    --set-env-vars VIOLATION_THRESHOLD=$VIOLATION_THRESHOLD \
    --set-env-vars RATE_LIMIT_REQUESTS=$RATE_LIMIT_REQUESTS \
    --set-env-vars RATE_LIMIT_WINDOW=$RATE_LIMIT_WINDOW \
    --set-env-vars SESSION_TIMEOUT=$SESSION_TIMEOUT \
    --set-env-vars MAX_CONTEXT_LENGTH=$MAX_CONTEXT_LENGTH \
    --set-env-vars CONVERSATION_HISTORY_LIMIT=$CONVERSATION_HISTORY_LIMIT \
    --set-env-vars CHROMA_DB_PATH=$CHROMA_DB_PATH \
    --set-env-vars CHROMA_COLLECTION_NAME=$CHROMA_COLLECTION_NAME \
    --set-env-vars CHROMA_PERSIST_DIR=$CHROMA_PERSIST_DIR \
    --set-env-vars BLACKLIST_DB_PATH=$BLACKLIST_DB_PATH \
    --set-env-vars STATS_DB_PATH=$STATS_DB_PATH \
    --set-env-vars KNOWLEDGE_BASE_PATH=$KNOWLEDGE_BASE_PATH \
    --set-env-vars LOG_FILE=$LOG_FILE \
    --set-env-vars LOG_FORMAT=$LOG_FORMAT \
    --set-env-vars MAX_LOG_SIZE=$MAX_LOG_SIZE \
    --set-env-vars LOG_BACKUP_COUNT=$LOG_BACKUP_COUNT \
    --set-env-vars CHAT_SESSION_FILE=$CHAT_SESSION_FILE \
    --set-env-vars CORS_ORIGINS=$CORS_ORIGINS \
    --set-env-vars TRACK_USER_SESSIONS=$TRACK_USER_SESSIONS \
    --set-env-vars TRACK_QUERY_ANALYTICS=$TRACK_QUERY_ANALYTICS \
    --set-env-vars ANONYMIZE_DATA=$ANONYMIZE_DATA \
    --set-env-vars SERVER_HOST=$SERVER_HOST \
    --set-env-vars SERVER_PORT=$SERVER_PORT \
    --set-env-vars REQUEST_TIMEOUT=$REQUEST_TIMEOUT \
    --set-env-vars GUNICORN_WORKERS=$GUNICORN_WORKERS \
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