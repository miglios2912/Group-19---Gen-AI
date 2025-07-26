# TUM Onboarding Assistant - Smart University Assistant

We built a chatbot that helps TUM students and staff find answers to university questions using generative AI and smart search techniques.

## What We Built

Our chatbot answers questions about TUM's campuses, services, and procedures. We designed it to understand context so users don't have to repeat their role or campus location in every conversation.

### Key Features

**Smart Context Detection**
- Remembers if you're a student, employee, or visitor
- Knows which campus you're at (Munich, Garching, Heilbronn, Weihenstephan)
- Only asks for context when actually needed

**Comprehensive Knowledge Base**
- 270 questions and answers covering university life
- Information about all TUM campuses and services
- Updated procedures and contact details

**Mobile-Friendly Interface**
- Works well on phones and tablets
- Dark mode support
- Interactive campus maps

**Production Ready**
- Deployed on Google Cloud Run
- Session management and analytics
- Rate limiting and error handling

## How We Built It

### Search Evolution

We started with a complex vector database system using ChromaDB and sentence transformers for semantic search. However, we found this was overcomplicated for our university Q&A use case. 

We simplified to a keyword expansion system that maps common student terms to relevant topics. For example, when someone types "liv", we expand it to include "library", "books", "study", etc. This made the system faster and more predictable while maintaining accuracy.

### Smart Context System

Instead of always asking "What's your role and campus?", our system:
1. Detects if a question needs context (campus-specific or role-dependent)
2. Only asks for missing information when required
3. Remembers context across the conversation

### Technical Stack

**Backend:**
- **Flask 3.0+** - Web framework for API endpoints
- **Gunicorn** - WSGI HTTP server for production deployment
- **Python 3.13** - Runtime environment
- Custom RAG implementation with keyword expansion
- Google Gemini AI for response generation
- Session management for context persistence

**Frontend:**
- **React 19.1+** - UI framework with hooks and context
- **Vite 6.3+** - Fast build tool and development server
- Mobile-first responsive design
- Real-time chat interface with WebSocket-like updates
- Interactive campus map integration

**Deployment:**
- **Google Cloud Run** - Serverless container platform
- **Docker** - Single container serving both frontend and backend
- **Container Registry** - Image storage and versioning
- Auto-scaling from 0 to multiple instances
- Environment-based configuration with secrets management

## Project Structure

```
TUM-Chatbot-Submission/
├── backend/           # Python Flask application
├── frontend/          # React web interface  
├── deployment/        # Docker and cloud configs
└── docs/             # Academic documentation
```

## Running the Project

### Development Mode (Separate Frontend/Backend)
1. **Set up environment:**
   ```bash
   cp deployment/env_example.txt .env
   # Add your Google Gemini API key
   ```

2. **Run backend (Flask development server):**
   ```bash
   cd backend
   pip install -r requirements.txt
   python api_v2.py  # Runs on http://localhost:8083
   ```

3. **Run frontend (Vite development server):**
   ```bash
   cd frontend
   npm install
   npm run dev  # Runs on http://localhost:5173
   ```

### Production Mode (Single Container)
1. **Local production testing:**
   ```bash
   cd backend
   gunicorn --bind 0.0.0.0:8083 api_v2:app
   ```

2. **Deploy to Google Cloud Run:**
   ```bash
   cd deployment
   ./deploy_cloudrun_v2.sh
   ```

The deployment script automatically:
- Builds React frontend with Vite
- Copies built files to Flask static folder
- Creates Docker container with both frontend and backend
- Deploys to Cloud Run with auto-scaling

## Team

Group 19 - Generative AI Course
Technical University of Munich

---

This project demonstrates practical application of generative AI in educational technology, focusing on user experience and production readiness.
