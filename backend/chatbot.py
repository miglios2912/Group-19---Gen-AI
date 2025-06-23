"""
TUM Chatbot Engine
Main chatbot implementation with vector database, logging, and statistics
"""

import json
import time
import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# Handle imports for both module and direct execution
try:
    from .config import get_config
    from .logger import get_logger, log_function_call, log_chat_session
    from .statistics import stats_manager, ChatInteraction, SearchPerformance
except ImportError:
    from config import get_config
    from logger import get_logger, log_function_call, log_chat_session
    from statistics import stats_manager, ChatInteraction, SearchPerformance

logger = get_logger(__name__)

class TUMChatbotEngine:
    """Main TUM Chatbot Engine with vector database and analytics"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = logger
        
        # Initialize Gemini API
        genai.configure(api_key=self.config.api.gemini_api_key)
        self.model = genai.GenerativeModel(
            self.config.api.gemini_model,
            generation_config={
                'max_output_tokens': self.config.api.max_tokens,
                'temperature': self.config.api.temperature
            }
        )
        
        # Initialize sentence transformer
        self.embedding_model = SentenceTransformer(self.config.search.embedding_model)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=self.config.database.chroma_db_path)
        self.collection_name = self.config.database.collection_name
        
        # Load knowledge base and setup vector database
        self.knowledge_base = self._load_knowledge_base()
        self._setup_vector_database()
        
        # User sessions storage
        self.user_sessions = {}
        
        self.logger.info(f"TUM Chatbot Engine initialized with {len(self.knowledge_base)} knowledge base entries")
    
    def _load_knowledge_base(self) -> List[Dict]:
        """Load the TUM Q&A knowledge base"""
        try:
            with open(self.config.knowledge_base.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded knowledge base with {len(data['documents'])} entries")
            return data['documents']
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    def _setup_vector_database(self):
        """Setup ChromaDB collection with embeddings"""
        try:
            # Try to get existing collection
            self.collection = self.chroma_client.get_collection(self.collection_name)
            self.logger.info(f"Using existing vector database with {self.collection.count()} documents")
        except:
            # Create new collection
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "TUM Q&A Knowledge Base"}
            )
            
            # Prepare documents for vector database
            documents = []
            metadatas = []
            ids = []
            
            for doc in self.knowledge_base:
                searchable_text = f"{doc['question']} {doc['answer']} {' '.join(doc['keywords'])} {doc['category']} {doc['role']}"
                
                documents.append(searchable_text)
                metadatas.append({
                    'id': doc['id'],
                    'category': doc['category'],
                    'role': doc['role'],
                    'question': doc['question'],
                    'answer': doc['answer'],
                    'keywords': ','.join(doc['keywords']),
                    'source': doc.get('source', '')
                })
                ids.append(doc['id'])
            
            # Add documents to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.info(f"Created vector database with {len(documents)} documents")
    
    @log_function_call(logger, "semantic_search")
    def semantic_search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Semantic search using ChromaDB"""
        top_k = top_k or self.config.search.semantic_search_top_k
        
        try:
            start_time = time.time()
            
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=['metadatas', 'distances']
            )
            
            search_time = time.time() - start_time
            
            # Convert results to our format
            documents = []
            similarity_scores = []
            
            for i, metadata in enumerate(results['metadatas'][0]):
                similarity_score = 1 - results['distances'][0][i]
                similarity_scores.append(similarity_score)
                
                doc = {
                    'id': metadata['id'],
                    'category': metadata['category'],
                    'role': metadata['role'],
                    'question': metadata['question'],
                    'answer': metadata['answer'],
                    'keywords': metadata['keywords'].split(','),
                    'source': metadata.get('source', ''),
                    'similarity_score': similarity_score
                }
                documents.append(doc)
            
            # Log search performance
            if similarity_scores:
                performance = SearchPerformance(
                    timestamp=datetime.utcnow(),
                    query=query,
                    search_method="semantic",
                    results_count=len(documents),
                    search_time=search_time,
                    avg_similarity=sum(similarity_scores) / len(similarity_scores),
                    max_similarity=max(similarity_scores),
                    min_similarity=min(similarity_scores)
                )
                stats_manager.record_search_performance(performance)
            
            return documents
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return self.keyword_search(query, top_k)
    
    @log_function_call(logger, "keyword_search")
    def keyword_search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Keyword-based search as fallback"""
        top_k = top_k or self.config.search.keyword_search_top_k
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        # Keyword expansions
        keyword_expansions = {
            'library': ['lib', 'liv', 'books', 'study', 'reading', 'research'],
            'location': ['where', 'building', 'address', 'find', 'get to', 'room'],
            'email': ['mail', 'e-mail', 'setup', 'configuration', 'mytum', 'exchange'],
            'wifi': ['eduroam', 'internet', 'network', 'connection', 'wireless'],
            'tumonline': ['system', 'portal', 'online', 'registration'],
            'moodle': ['lms', 'learning', 'course', 'platform'],
            'printing': ['print', 'copy', 'scanner', 'document'],
            'vpn': ['remote access', 'secure connection', 'network'],
            'hungry': ['mensa', 'cafeteria', 'canteen', 'food', 'dining', 'eat'],
            'study': ['library', 'quiet', 'space', 'room', 'academic', 'learning'],
            'housing': ['accommodation', 'dormitory', 'apartment', 'room', 'rent'],
            'sports': ['fitness', 'gym', 'recreation', 'exercise', 'activities'],
            'transport': ['bus', 'train', 'parking', 'bike', 'mvv', 'mobility'],
            'international': ['visa', 'foreign', 'exchange', 'global', 'overseas'],
            'career': ['job', 'internship', 'professional', 'employment', 'work'],
            'emergency': ['help', 'urgent', 'problem', 'issue', 'security'],
        }
        
        # Expand query words
        expanded_words = set(query_words)
        for word in query_words:
            if word in keyword_expansions:
                expanded_words.update(keyword_expansions[word])

        scored_docs = []
        for doc in self.knowledge_base:
            searchable_text = (
                doc['question'] + ' ' +
                doc['answer'] + ' ' +
                doc['category'] + ' ' +
                doc['role'] + ' ' +
                ' '.join(doc['keywords'])
            ).lower()

            doc_words = set(re.findall(r'\w+', searchable_text))
            matches = len(expanded_words.intersection(doc_words))
            
            score = matches
            
            # Boost for exact matches
            if any(phrase in searchable_text for phrase in [query_lower, ' '.join(query_words)]):
                score += 3
                
            if any(word in doc['question'].lower() for word in query_words):
                score += 2
                
            if any(word in doc['category'].lower() for word in query_words):
                score += 1.5

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]
    
    @log_function_call(logger, "hybrid_search")
    def hybrid_search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Combine semantic and keyword search for better results"""
        top_k = top_k or self.config.search.hybrid_search_top_k
        
        start_time = time.time()
        
        # Get semantic search results
        semantic_results = self.semantic_search(query, top_k=top_k*2)
        
        # Get keyword search results
        keyword_results = self.keyword_search(query, top_k=top_k*2)
        
        # Combine and deduplicate results
        combined = {}
        
        # Add semantic results with higher weight
        for doc in semantic_results:
            doc_id = doc['id']
            if doc_id not in combined:
                combined[doc_id] = doc
                combined[doc_id]['final_score'] = doc.get('similarity_score', 0) * 2
        
        # Add keyword results
        for doc in keyword_results:
            doc_id = doc['id']
            if doc_id in combined:
                combined[doc_id]['final_score'] += 1
            else:
                combined[doc_id] = doc
                combined[doc_id]['final_score'] = 1
        
        # Sort by final score and return top_k
        sorted_results = sorted(combined.values(), key=lambda x: x['final_score'], reverse=True)
        
        search_time = time.time() - start_time
        
        # Log hybrid search performance
        similarity_scores = [doc.get('similarity_score', 0) for doc in sorted_results if 'similarity_score' in doc]
        if similarity_scores:
            performance = SearchPerformance(
                timestamp=datetime.utcnow(),
                query=query,
                search_method="hybrid",
                results_count=len(sorted_results),
                search_time=search_time,
                avg_similarity=sum(similarity_scores) / len(similarity_scores),
                max_similarity=max(similarity_scores),
                min_similarity=min(similarity_scores)
            )
            stats_manager.record_search_performance(performance)
        
        return sorted_results[:top_k]
    
    def _extract_user_info(self, query: str, session_id: str):
        """Extract and store user information from query"""
        query_lower = query.lower()
        
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {'user_context': {}, 'conversation_history': []}
        
        user_context = self.user_sessions[session_id]['user_context']
        
        # Enhanced role extraction
        if any(word in query_lower for word in ['student', 'studying', 'study', 'enrolled', 'degree', 'bachelor', 'master', 'international student', 'foreign student', 'visa', 'residence permit']):
            user_context['role'] = 'student'
        elif any(word in query_lower for word in ['professor', 'prof']):
            user_context['role'] = 'professor'
        elif any(word in query_lower for word in ['lecturer', 'faculty', 'instructor', 'teacher']):
            user_context['role'] = 'lecturer'
        elif any(word in query_lower for word in ['phd', 'ph.d', 'doctoral', 'doctorate', 'phd student']):
            user_context['role'] = 'phd'
        elif any(word in query_lower for word in ['postdoc', 'post-doc', 'postdoctoral', 'post doctor']):
            user_context['role'] = 'postdoc'
        elif any(word in query_lower for word in ['employee', 'staff', 'work', 'working']):
            user_context['role'] = 'employee'
        elif any(word in query_lower for word in ['new employee', 'starting work', 'first day']):
            user_context['role'] = 'new employee'
        elif any(word in query_lower for word in ['visitor', 'visiting', 'guest', 'tour']):
            user_context['role'] = 'visitor'

        # Enhanced campus extraction
        if any(word in query_lower for word in ['heilbronn', 'bildungscampus', 'chn']):
            user_context['campus'] = 'Heilbronn'
        elif any(word in query_lower for word in ['munich', 'münchen', 'garching', 'main campus']):
            user_context['campus'] = 'Munich'
        elif any(word in query_lower for word in ['singapore', 'asia']):
            user_context['campus'] = 'Singapore'
    
    def _needs_user_info(self, query: str, user_info: str) -> bool:
        """Determine if we need to ask for user role/campus for this query"""
        query_lower = query.lower()
        
        # If we already have complete user info, never ask again
        if user_info and ('student' in user_info or 'employee' in user_info or 'visitor' in user_info):
            if ('Munich' in user_info or 'Heilbronn' in user_info or 'Singapore' in user_info):
                return False
        
        # Questions that need specific role/campus information
        specific_questions = [
            'borrow', 'laptop', 'equipment', 'access', 'card', 'id', 'student service', 
            'office', 'location', 'where', 'how to get', 'email setup', 'account',
            'registration', 'enroll', 'library', 'wifi', 'vpn', 'moodle', 'tumonline',
            'mental health', 'support', 'counseling', 'help', 'fürstenberg',
            'housing', 'accommodation', 'dormitory', 'visa', 'residence permit',
            'insurance', 'health', 'dining', 'mensa', 'cafeteria', 'parking',
            'transport', 'bike', 'career', 'internship', 'job', 'research',
            'thesis', 'language course', 'german', 'orientation', 'welcome day',
            'student council', 'organizations', 'sports', 'fitness', 'events',
            'cultural', 'international', 'emergency', 'banking', 'shopping'
        ]
        
        # Casual conversation that doesn't need user info
        casual = ['thanks', 'thank you', 'good', 'fine', 'okay', 'bye', 'goodbye', 'yes', 'no']

        # If it's just casual conversation, don't ask for info
        if any(word in query_lower for word in casual) and len(query.split()) <= 3:
            return False
        
        # If it's a greeting and we don't have user info, ask for it
        greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        if any(word in query_lower for word in greetings) and len(query.split()) <= 3:
            return not user_info
        
        # If it's a specific question and we don't have user info, ask for it
        if any(word in query_lower for word in specific_questions):
            return not user_info
        
        return False
    
    def _format_response(self, response: str) -> str:
        """Post-process response to improve formatting"""
        # Add line breaks before numbered lists
        response = re.sub(r'(\d+\.\s)', r'\n\n\1', response)
        
        # Add line breaks before questions
        response = re.sub(r'(\?\s)(\d+\.)', r'\1\n\n\2', response)
        
        # Add line breaks before sentences that start with key indicators
        response = re.sub(r'(\. )([A-Z][a-z]+ you)', r'\1\n\n\2', response)
        response = re.sub(r'(\. )(Once|From|Would|If)', r'\1\n\n\2', response)
        response = re.sub(r'(\. )(Would you|Do you|Are you)', r'\1\n\n\2', response)
        
        # Remove any existing markdown bold formatting
        response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        
        # Clean up any double line breaks
        response = re.sub(r'\n\n+', '\n\n', response)
        
        return response.strip()
    
    @log_function_call(logger, "generate_response")
    def generate_response(self, query: str, session_id: str, user_id: str = "anonymous") -> str:
        """Generate response using enhanced RAG approach with vector database"""
        start_time = time.time()
        
        # Extract user info from current query
        self._extract_user_info(query, session_id)

        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {'user_context': {}, 'conversation_history': []}

        session = self.user_sessions[session_id]

        # Add to conversation history
        session['conversation_history'].append(f"User: {query}")

        # Keep only last N exchanges for context
        if len(session['conversation_history']) > self.config.knowledge_base.conversation_history_limit:
            session['conversation_history'] = session['conversation_history'][-self.config.knowledge_base.conversation_history_limit:]

        # Use hybrid search for better results
        relevant_docs = self.hybrid_search(query, top_k=5)
        
        # Prepare context from retrieved documents
        context = ""
        if relevant_docs:
            for i, doc in enumerate(relevant_docs, 1):
                context += f"\n--- Knowledge Entry {i} ---\n"
                context += f"Category: {doc['category']}\n"
                context += f"Role: {doc['role']}\n"
                context += f"Q: {doc['question']}\n"
                context += f"A: {doc['answer']}\n"
                if 'similarity_score' in doc:
                    context += f"Relevance: {doc['similarity_score']:.2f}\n"
        
        # Include user context
        user_info = ""
        if session['user_context']:
            role = session['user_context'].get('role', '')
            campus = session['user_context'].get('campus', '')
            if role or campus:
                user_info = f"User is a {role} at TUM {campus}"
        
        # Recent conversation context
        recent_conversation = ""
        if len(session['conversation_history']) > 1:
            recent_conversation = "Recent conversation:\n" + "\n".join(session['conversation_history'][-6:]) + "\n"
        
        # Check if we need user info for this type of question
        needs_clarification = self._needs_user_info(query, user_info)
        
        # Create intelligent prompt
        if needs_clarification:
            prompt = f"""You are an intelligent, helpful TUM (Technical University of Munich) assistant. 

{recent_conversation}
Current question: {query}

{user_info if user_info else "You don't know the user's role or campus yet."}

To provide the best answer, you need to know:
- Are they a student, employee, or visitor?
- Which campus (Munich, Heilbronn, Singapore)?

Ask for this information in a natural, conversational way. Explain briefly why you need it to help them better.

Available knowledge base information:
{context}"""
        else:
            prompt = f"""You are a helpful TUM (Technical University of Munich) assistant with comprehensive knowledge across all campuses.

{recent_conversation}
USER: {session['user_context'].get('role', '')} at TUM {session['user_context'].get('campus', '')}

Guidelines:
- Prioritize information for their specific campus and role
- For comprehensive questions, draw from multiple knowledge entries
- For locations, provide exact building/room details
- For technical help, give clear step-by-step instructions
- Maintain conversation context - if user asks follow-up questions like "how much?", "where?", "when?", understand they're referring to the previous topic
- If you don't have specific information, admit it clearly rather than providing unrelated details
- Stay focused on the user's actual question throughout the conversation
- Stay conversational, brief (2-3 sentences), and on-topic
- Don't reference "Entry X" numbers

{context}

Key contacts: IT Support (servicedesk@tum.de, it-support@tum.de) | Emergency: 112/110

Current question: {query}"""

        # Generate response using Gemini
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            response_text = f"I apologize, but I'm experiencing technical difficulties. Please try again later or contact IT support at servicedesk@tum.de"
        
        # Apply formatting improvements
        formatted_response = self._format_response(response_text)
        
        # Add response to conversation history
        session['conversation_history'].append(f"Assistant: {formatted_response}")
        
        # Calculate response time
        response_time = time.time() - start_time
        
        # Record statistics
        interaction = ChatInteraction(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            response=formatted_response,
            search_method="hybrid",
            search_results_count=len(relevant_docs),
            response_time=response_time,
            user_role=session['user_context'].get('role'),
            user_campus=session['user_context'].get('campus'),
            query_length=len(query),
            response_length=len(formatted_response)
        )
        stats_manager.record_chat_interaction(interaction)
        
        # Log chat session for development debugging
        log_chat_session(
            user_id=user_id,
            session_id=session_id,
            query=query,
            response=formatted_response,
            user_role=session['user_context'].get('role'),
            user_campus=session['user_context'].get('campus')
        )
        
        return formatted_response
    
    def start_session(self, session_id: str, user_id: str = "anonymous"):
        """Start a new user session"""
        stats_manager.start_user_session(session_id, user_id)
        self.logger.info(f"Started session {session_id} for user {user_id}")
    
    def end_session(self, session_id: str):
        """End a user session"""
        stats_manager.end_user_session(session_id)
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
        self.logger.info(f"Ended session {session_id}")
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get information about a session"""
        if session_id in self.user_sessions:
            return {
                'session_id': session_id,
                'user_context': self.user_sessions[session_id]['user_context'],
                'conversation_count': len(self.user_sessions[session_id]['conversation_history']) // 2
            }
        return None 