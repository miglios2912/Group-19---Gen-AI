# LLM-Based Onboarding Chatbot for TUM  
A conversational assistant powered by Large Language Models (LLMs) to streamline the onboarding experience for new professors, staff, and employees at the Technical University of Munich (TUM).

## Project Overview

This project delivers a smart, AI-based chatbot designed to help new employees and faculty members at TUM get quick, accurate answers to onboarding-related questions. It retrieves real-time institutional data and personalizes responses based on department, role, and user context.

Key onboarding support includes:
- Office and equipment requests  
- Department-specific procedures  
- Administrative contact lookups  
- Access to forms, guidelines, and internal links  

## Features

✅ Natural Language Understanding for Vague or Incomplete Questions  
✅ Personalization Based on Department and Role  
✅ Institutional Data Retrieval from TUMwiki and TUMonline  
✅ Clarifying Follow-up Questions to Improve Accuracy  
✅ Chat Interface with Quick Action Links and Document Suggestions  

## Tech Stack

- **Frontend:** React (for web interface)  
- **Backend:** Python (FastAPI or Flask)  
- **LLM Integration:** OpenAI GPT-4 (via API)  
- **Retrieval System:** LangChain or LlamaIndex (RAG pipeline)  
- **Vector DB:** FAISS / Chroma / Pinecone  
- **Hosting:** Render, Vercel, or TUM internal servers  

## Installation & Setup

To run this project locally:

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/miglios2912/Group-19---Gen-AI
cd tum-onboarding-chatbot
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
# or for frontend:
npm install
```

### 3️⃣ Set Up Environment Variables
Create a `.env` file:
```
OPENAI_API_KEY=your_api_key_here
VECTOR_DB_PATH=path_to_your_vector_store
```

### 4️⃣ Start the Backend
```bash
python app.py
```

### 5️⃣ Start the Frontend (if using React)
```bash
npm start
```

## How It Works

1️⃣ User asks a natural-language question (e.g., “How do I get ...?”)  
2️⃣ The chatbot uses retrieval-augmented generation (RAG) to fetch relevant onboarding info  
3️⃣ If needed, it asks follow-up questions (e.g., “Which department are you in?”)  
4️⃣ LLM generates a personalized, concise response with optional links or forms  
5️⃣ The user receives tailored onboarding guidance in seconds  

## Folder Structure

```
tum-onboarding-chatbot/
│
├── backend/
│   ├── app.py                 # Main FastAPI/Flask backend
│   ├── data/                  # Onboarding docs and embeddings
│   └── retrieval/             # Vector DB setup and query logic
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/        # Chat UI, buttons, etc.
│   │   ├── App.js
│   │   └── index.js
│
├── .env
├── requirements.txt
├── package.json
└── README.md
```

## Future Improvements

🔹 **Authentication Integration** – Enable user-specific history and settings  
🔹 **Multilingual Support** – Serve responses in German or English  
🔹 **Advanced Analytics** – Log user behavior to improve chatbot responses  
🔹 **Slack/MS Teams Integration** – Allow usage within internal TUM platforms  

## 📩 Contact

For questions, feedback, or collaboration opportunities:  
📧 Email: simone.miglio@tum.de
