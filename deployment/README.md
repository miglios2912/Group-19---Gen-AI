# TUM Chatbot Deployment

We deploy our chatbot to Google Cloud Run for automatic scaling and high availability.

## Files

- `Dockerfile.cloudrun.v2` - Container configuration that builds both backend and frontend
- `deploy_cloudrun_v2.sh` - Deployment script for Google Cloud
- `env_example.txt` - Environment variable template

## Deployment Process

1. **Set up Google Cloud:**
   - Install Google Cloud CLI
   - Authenticate: `gcloud auth login`
   - Set project: `gcloud config set project YOUR_PROJECT_ID`

2. **Configure environment:**
   - Copy `env_example.txt` to `.env`
   - Add your Gemini API key and project details

3. **Deploy:**
   ```bash
   ./deploy_cloudrun_v2.sh
   ```

## How It Works

Our deployment creates a single container that serves both the React frontend and Python backend. This simplifies deployment and reduces costs.

**Container Build Process:**
1. Install Python dependencies
2. Copy backend code
3. Install Node.js and build frontend
4. Copy built frontend to Flask static folder
5. Configure Flask to serve frontend and API

**Cloud Run Configuration:**
- **Auto-scaling**: 0 to multiple instances based on demand
- **Cold starts**: ~2-3 seconds for new container instances
- **Session management**: 1 worker per container for session persistence
- **Health checks**: `/api/v2/health` endpoint for liveness probes
- **Environment variables**: Secure configuration management
- **Request limits**: Configurable timeout and concurrency settings

## Production Features

**Platform Features:**
- **HTTPS by default** with automatic SSL certificates
- **Automatic container scaling** based on CPU and memory usage
- **Built-in load balancing** across multiple container instances
- **Zero-downtime deployments** with rolling updates
- **Request logging and monitoring** integrated with Google Cloud

**Performance Optimizations:**
- **Single container** serves both frontend and backend
- **Gunicorn workers** handle concurrent requests efficiently
- **Container Registry** for fast image pulls
- **Regional deployment** for low latency
- **Pay-per-use** pricing model (only pay when containers are running)

**Monitoring and Observability:**
- Request count and latency metrics
- Container resource utilization
- Error tracking and alerting
- Access logs for debugging

The deployment script handles Docker building, pushing to Container Registry, and updating the Cloud Run service automatically with proper versioning and rollback capabilities.