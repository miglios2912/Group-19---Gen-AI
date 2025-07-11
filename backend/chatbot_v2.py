"""
TUM Chatbot Engine
"""

import json
import time
import re
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
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

class TUMChatbotV2:
    
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
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # User sessions storage
        self.user_sessions = {}
        
        self.logger.info(f"TUM Chatbot V2 initialized with {len(self.knowledge_base)} knowledge base entries")
        
        # Startup warning for chat session logging
        if self.config.logging.log_chat_sessions:
            if self.config.environment.lower() == "development":
                print("\n" + "="*80)
                print("⚠️  DEVELOPMENT MODE STARTUP WARNING ⚠️")
                print("="*80)
                print("🔒 CHAT SESSION LOGGING IS ENABLED")
                print("📝 All user conversations will be logged to:")
                print(f"   {self.config.logging.chat_session_file}")
                print("⚠️  This includes sensitive user data and should NEVER be enabled in production!")
                print("🔧 To disable: set LOG_CHAT_SESSIONS=False in your .env file")
                print("="*80 + "\n")
            else:
                print("\n" + "="*80)
                print("🚨 PRODUCTION SECURITY WARNING 🚨")
                print("="*80)
                print("❌ CHAT SESSION LOGGING IS ENABLED IN PRODUCTION!")
                print("🔒 This is a security risk - user conversations will be logged!")
                print("🛑 IMMEDIATELY DISABLE by setting LOG_CHAT_SESSIONS=False")
                print("="*80 + "\n")
    
    def _load_knowledge_base(self) -> List[Dict]:
        """Load the TUM Q&A knowledge base"""
        try:
            kb_path = self.config.knowledge_base.knowledge_base_path
            # Use local path for development
            if kb_path.startswith('/app/'):
                kb_path = './TUM_QA.json'
            
            with open(kb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded knowledge base with {len(data['documents'])} entries")
            return data['documents']
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            raise
    
    def optimized_search(self, query: str, top_k: int = 5, user_context: Dict = None) -> List[Dict]:
        """
        - Focused keyword expansion
        - Enhanced scoring for critical keywords
        - Single, efficient search method
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        # Comprehensive keyword expansion system
        keyword_expansions = {
            # =================================================================
            # CAMPUS & LOCATION KEYWORDS - Enhanced with variations
            # =================================================================
            'library': ['lib', 'liv', 'books', 'study', 'reading', 'research', 'digital resources', 'bibliothek'],
            'liv': ['library', 'lib', 'books', 'study', 'reading', 'research'],
            'location': ['where', 'building', 'address', 'find', 'get to', 'go to', 'room', 'directions', 'navigate'],
            'heilbronn': ['bildungscampus', 'campus', 'chn', 'student handbook', 'bildungscampus heilbronn'],
            'munich': ['münchen', 'main campus', 'city campus', 'downtown', 'zentrum', 'munich campus'],
            'garching': ['garching campus', 'research campus', 'forschungszentrum', 'garching-forschungszentrum'],
            'weihenstephan': ['weihenstephan campus', 'freising', 'freising-weihenstephan', 'life sciences'],
            'singapore': ['asia', 'international', 'tum asia', 'singapore campus'],
            'building': ['edifice', 'structure', 'facility', 'complex', 'hall', 'tower', 'block'],
            'room': ['office', 'classroom', 'lab', 'laboratory', 'space', 'venue', 'hall', 'auditorium'],
            
            # =================================================================
            # DINING & FOOD KEYWORDS - Comprehensive coverage
            # =================================================================
            'lunch': ['mensa', 'cafeteria', 'canteen', 'dining', 'eat', 'food', 'meal', 'restaurant', 'cafe'],
            'dinner': ['mensa', 'cafeteria', 'canteen', 'dining', 'eat', 'food', 'meal', 'restaurant', 'evening meal'],
            'breakfast': ['mensa', 'cafeteria', 'canteen', 'dining', 'eat', 'food', 'meal', 'morning meal'],
            'meal': ['mensa', 'cafeteria', 'canteen', 'dining', 'eat', 'food', 'lunch', 'dinner', 'breakfast'],
            'mensa': ['cafeteria', 'canteen', 'dining hall', 'restaurant', 'eat', 'food', 'lunch', 'meal', 'dining'],
            'cafeteria': ['mensa', 'canteen', 'dining hall', 'restaurant', 'eat', 'food', 'lunch', 'meal'],
            'canteen': ['mensa', 'cafeteria', 'dining hall', 'restaurant', 'eat', 'food', 'lunch', 'meal'],
            'restaurant': ['mensa', 'cafeteria', 'canteen', 'dining', 'food', 'eat', 'meal'],
            'cafe': ['coffee', 'snack', 'beverage', 'drink', 'light meal', 'cafeteria'],
            'dining': ['mensa', 'cafeteria', 'canteen', 'eat', 'food', 'lunch', 'meal', 'restaurant'],
            'hungry': ['mensa', 'cafeteria', 'canteen', 'food', 'dining', 'eat', 'lunch', 'breakfast', 'dinner'],
            'eat': ['mensa', 'cafeteria', 'canteen', 'food', 'dining', 'hungry', 'meal', 'lunch'],
            'food': ['mensa', 'cafeteria', 'canteen', 'dining', 'eat', 'hungry', 'meal', 'vegetarian', 'vegan', 'dietary', 'allergy'],
            'snack': ['food', 'eat', 'vending', 'quick', 'meal', 'light food', 'bite'],
            'vegetarian': ['vegan', 'dietary', 'plant-based', 'meat-free', 'special diet'],
            'vegan': ['vegetarian', 'dietary', 'plant-based', 'dairy-free', 'special diet'],
            
            # =================================================================
            # TECHNOLOGY & IT KEYWORDS - Comprehensive coverage
            # =================================================================
            'laptop': ['computer', 'equipment', 'borrow', 'device', 'hardware', 'notebook', 'pc'],
            'computer': ['laptop', 'desktop', 'pc', 'workstation', 'device', 'hardware', 'machine'],
            'print': ['printing', 'printer', 'copy', 'scan', 'document', 'paper', 'multifunction'],
            'printing': ['print', 'printer', 'copy', 'scanner', 'document', 'paper', 'multifunction'],
            'software': ['application', 'program', 'app', 'install', 'license', 'download', 'tool'],
            'app': ['application', 'software', 'program', 'tool', 'mobile app'],
            'install': ['installation', 'setup', 'configure', 'download', 'deploy'],
            'support': ['help', 'assistance', 'troubleshoot', 'fix', 'problem', 'issue', 'help desk'],
            'help': ['support', 'assistance', 'troubleshoot', 'fix', 'problem', 'issue', 'guidance'],
            'login': ['log-in', 'sign-in', 'access', 'password', 'credentials', 'authentication', 'signin'],
            'password': ['login', 'credentials', 'authentication', 'access', 'security', 'passphrase'],
            'account': ['profile', 'user', 'credentials', 'login', 'access', 'registration'],
            'card': ['tumcard', 'student card', 'id', 'access', 'campuscard', 'student id', 'identification'],
            'tumcard': ['card', 'student card', 'id', 'access', 'identification', 'campus card'],
            'email': ['mail', 'e-mail', 'setup', 'configuration', 'mytum', 'exchange', 'electronic mail'],
            'mail': ['email', 'e-mail', 'electronic mail', 'messaging', 'correspondence'],
            'wifi': ['eduroam', 'internet', 'network', 'connection', 'wireless', 'wlan', 'setup', 'cat', 'wizard'],
            'eduroam': ['wifi', 'wireless', 'internet', 'network', 'wlan', 'connection'],
            'internet': ['wifi', 'network', 'connection', 'online', 'web', 'connectivity'],
            'network': ['wifi', 'internet', 'connection', 'eduroam', 'lan', 'connectivity'],
            'tumonline': ['system', 'portal', 'online', 'registration', 'enrollment', 'student portal'],
            'moodle': ['lms', 'learning', 'course', 'platform', 'learning management system'],
            'vpn': ['remote access', 'secure connection', 'network', 'lrz', 'virtual private network'],
            
            # =================================================================
            # ACADEMIC KEYWORDS - Comprehensive coverage
            # =================================================================
            'course': ['class', 'lecture', 'seminar', 'tutorial', 'subject', 'module', 'program'],
            'class': ['course', 'lecture', 'seminar', 'tutorial', 'lesson', 'session'],
            'lecture': ['class', 'course', 'seminar', 'presentation', 'talk', 'session'],
            'seminar': ['course', 'class', 'workshop', 'tutorial', 'discussion'],
            'exam': ['test', 'assessment', 'quiz', 'evaluation', 'examination', 'final'],
            'test': ['exam', 'assessment', 'quiz', 'evaluation', 'examination'],
            'grade': ['mark', 'score', 'result', 'transcript', 'certificate', 'evaluation'],
            'transcript': ['grade', 'record', 'certificate', 'academic record', 'marks'],
            'enroll': ['register', 'matriculate', 'admission', 'application', 'apply', 'signup'],
            'register': ['enroll', 'registration', 'signup', 'apply', 'matriculate'],
            'admission': ['application', 'apply', 'acceptance', 'enrollment', 'entry'],
            'application': ['apply', 'admission', 'form', 'request', 'submission'],
            'thesis': ['dissertation', 'project', 'research', 'paper', 'final project', 'capstone'],
            'research': ['thesis', 'project', 'lab', 'academic', 'study', 'investigation'],
            'study': ['library', 'quiet', 'space', 'room', 'liv', 'academic', 'learning', 'research'],
            'graduation': ['degree', 'diploma', 'certificate', 'completion', 'finish'],
            'degree': ['graduation', 'diploma', 'certificate', 'bachelor', 'master', 'phd'],
            
            # =================================================================
            # ROLE VARIATIONS - Comprehensive coverage
            # =================================================================
            'student': ['undergraduate', 'graduate', 'bachelor', 'master', 'pupil', 'learner', 'scholar'],
            'undergraduate': ['student', 'bachelor', 'undergrad', 'first degree'],
            'graduate': ['student', 'master', 'postgraduate', 'grad student'],
            'professor': ['prof', 'faculty', 'instructor', 'teacher', 'lecturer', 'academic'],
            'lecturer': ['professor', 'instructor', 'teacher', 'faculty', 'academic'],
            'employee': ['staff', 'worker', 'personnel', 'team member', 'colleague', 'work'],
            'staff': ['employee', 'worker', 'personnel', 'team member', 'faculty'],
            'researcher': ['scientist', 'investigator', 'post-doc', 'postdoc', 'doctoral', 'phd'],
            'phd': ['doctoral', 'doctorate', 'researcher', 'graduate student', 'phd student'],
            'postdoc': ['post-doc', 'postdoctoral', 'researcher', 'fellow'],
            'visitor': ['guest', 'external', 'visiting', 'tour'],
            'international': ['visa', 'foreign', 'exchange', 'global', 'overseas', 'abroad'],
            
            # =================================================================
            # SERVICES & PROCESSES - Comprehensive coverage
            # =================================================================
            'housing': ['accommodation', 'dormitory', 'apartment', 'room', 'rent', 'living', 'residence'],
            'accommodation': ['housing', 'dormitory', 'apartment', 'room', 'residence', 'living'],
            'sports': ['fitness', 'gym', 'recreation', 'exercise', 'activities', 'athletics'],
            'fitness': ['sports', 'gym', 'exercise', 'workout', 'health', 'recreation'],
            'health': ['medical', 'doctor', 'wellness', 'counseling', 'clinic', 'care'],
            'counseling': ['advice', 'guidance', 'support', 'help', 'consultation'],
            'career': ['job', 'internship', 'professional', 'employment', 'work', 'placement'],
            'job': ['career', 'employment', 'work', 'position', 'internship'],
            'internship': ['job', 'career', 'work experience', 'placement', 'training'],
            'visa': ['permit', 'authorization', 'documentation', 'immigration', 'international'],
            'permit': ['access', 'permission', 'authorization', 'card', 'pass', 'employee', 'visa'],
            'form': ['forms', 'application', 'request', 'document', 'paperwork', 'submission'],
            'document': ['form', 'paper', 'file', 'certificate', 'record', 'paperwork'],
            'payment': ['fee', 'cost', 'price', 'charge', 'tuition'],
            'fee': ['payment', 'cost', 'charge', 'tuition', 'expense'],
            
            # =================================================================
            # TRANSPORTATION & MOBILITY - Enhanced
            # =================================================================
            'transport': ['bus', 'train', 'parking', 'bike', 'mvv', 'mobility', 'travel', 'public transport'],
            'parking': ['car', 'vehicle', 'permit', 'space', 'parkhaus', 'park', 'garage', 'lot', 'galileo'],
            'galileo': ['parking', 'garage', 'garching', 'underground', 'park'],
            'car': ['parking', 'vehicle', 'permit', 'space', 'parkhaus', 'park', 'garage', 'automobile'],
            'bike': ['bicycle', 'cycling', 'bikebox', 'sharing', 'cycle'],
            'bus': ['transport', 'public transport', 'mvv', 'transit'],
            'train': ['transport', 'public transport', 'mvv', 's-bahn', 'u-bahn'],
            'parkhaus': ['parking', 'car', 'vehicle', 'permit', 'garage', 'park'],
            'park': ['parking', 'car', 'parkhaus', 'garage', 'lot', 'space'],
            'garage': ['parking', 'parkhaus', 'car', 'park', 'lot'],
            'lot': ['parking', 'park', 'garage', 'parkhaus', 'car', 'space'],
            
            # =================================================================
            # SOCIAL & COMMUNITY - Enhanced
            # =================================================================
            'friends': ['buddy', 'program', 'social', 'meet', 'people', 'connect', 'networking', 'student council'],
            'buddy': ['friends', 'program', 'social', 'meet', 'people', 'connect', 'networking', 'mentor'],
            'social': ['friends', 'community', 'networking', 'events', 'activities', 'clubs'],
            'club': ['organization', 'group', 'society', 'association', 'activity'],
            'event': ['activity', 'program', 'workshop', 'conference', 'meeting'],
            'language': ['german', 'english', 'course', 'learning', 'foreign language'],
            'council': ['student council', 'representation', 'organization'],
            'tired': ['sleep', 'rest', 'study', 'quiet', 'break', 'housing', 'accommodation'],
            
            # =================================================================
            # BUSINESS & ADMINISTRATION - Enhanced
            # =================================================================
            'business': ['card', 'contact', 'information', 'details', 'professional'],
            'onboarding': ['new employee', 'setup', 'orientation', 'getting started', 'induction'],
            'orientation': ['onboarding', 'introduction', 'getting started', 'welcome'],
            'office': ['workplace', 'desk', 'room', 'workspace', 'building'],
            'meeting': ['appointment', 'conference', 'discussion', 'session'],
            'conference': ['meeting', 'seminar', 'workshop', 'event'],
            
            # =================================================================
            # ADDITIONAL ADMINISTRATIVE TERMS - Employee specific
            # =================================================================
            'forms': ['form', 'application', 'request', 'document', 'paperwork'],
            'permits': ['access', 'permission', 'authorization', 'card', 'pass', 'employee'],
            'vacation': ['leave', 'time off', 'holiday', 'absence', 'urlaubsantrag'],
            'travel': ['business trip', 'trip', 'conference', 'expense', 'reimbursement', 'dienstreise', 'forms'],
            'expense': ['reimbursement', 'cost', 'payment', 'travel', 'business', 'auszahlungsanordnung'],
            'reimbursement': ['expense', 'refund', 'payment', 'claim', 'travel', 'auszahlungsanordnung'],
            'trip': ['travel', 'business', 'conference', 'dienstreise', 'expense'],
            'dienstreise': ['travel', 'business', 'trip', 'application', 'dienstreiseantrag'],
            'dienstreiseantrag': ['travel', 'business', 'application', 'trip', 'authorization'],
            'auszahlungsanordnung': ['expense', 'reimbursement', 'payment', 'form', 'claim'],
            'ethics': ['committee', 'approval', 'research', 'proposal', 'ethik', 'ethik-pool', 'portal'],
            'approval': ['permission', 'authorization', 'ethics', 'committee', 'forms', 'ethik-pool'],
            'committee': ['ethics', 'ethik', 'approval', 'research', 'proposal', 'ethikkommission'],
            'ethik': ['ethics', 'committee', 'approval', 'portal', 'pool'],
            'portal': ['ethik-pool', 'mytum', 'online', 'system', 'access'],
            
            # =================================================================
            # COMPUTING & ADVANCED IT - Specialized terms
            # =================================================================
            'computing': ['hpc', 'high performance', 'cluster', 'supercomputer', 'resources', 'lrz'],
            'hpc': ['high performance computing', 'cluster', 'supercomputer', 'computing', 'resources'],
            'performance': ['computing', 'hpc', 'high', 'cluster', 'resources'],
            'cluster': ['computing', 'hpc', 'supercomputer', 'performance', 'resources'],
            'resources': ['computing', 'hpc', 'it', 'cluster', 'access'],
            
            # Food and dining keywords
            'dietary': ['food', 'restriction', 'allergy', 'vegetarian', 'vegan', 'halal', 'mensa', 'dining'],
            'restrictions': ['dietary', 'food', 'allergy', 'limitation', 'requirement', 'vegetarian', 'vegan'],
            'dining': ['food', 'mensa', 'cafeteria', 'restaurant', 'eat', 'meal', 'dietary'],
            'menu': ['food', 'dining', 'mensa', 'meal', 'dietary', 'options'],
            'vegetarian': ['vegan', 'dietary', 'food', 'restrictions', 'mensa', 'dining'],
            'vegan': ['vegetarian', 'dietary', 'food', 'restrictions', 'mensa', 'dining'],
            'allergy': ['dietary', 'restrictions', 'food', 'allergen', 'intolerance'],
            
            # Campus-specific enhancements
            'heilbronn': ['bildungscampus', 'chn', 'campuscard', 'mensa', 'dining'],
            'bildungscampus': ['heilbronn', 'campuscard', 'mensa', 'dining', 'parking'],
            
            # WiFi setup keywords
            'setup': ['eduroam', 'wifi', 'configuration', 'install', 'wizard', 'cat'],
            'configuration': ['setup', 'eduroam', 'wifi', 'wizard', 'profile'],
            'wizard': ['setup', 'eduroam', 'cat', 'configuration', 'tool'],
            'cat': ['eduroam', 'wizard', 'configuration', 'tool', 'setup'],
            'lrz': ['vpn', 'network', 'computing', 'leibniz', 'centre'],
            
            # Emergency and practical keywords
            'emergency': ['help', 'urgent', 'problem', 'issue', 'security'],
            'health': ['insurance', 'medical', 'doctor', 'healthcare'],
            'banking': ['money', 'account', 'financial', 'atm'],
            'shopping': ['store', 'service', 'grocery', 'restaurant']
        }
        
        # Expand query words with related terms
        expanded_words = set(query_words)
        for word in query_words:
            if word in keyword_expansions:
                expanded_words.update(keyword_expansions[word])

        scored_docs = []
        for doc in self.knowledge_base:
            # Search in all relevant fields
            searchable_text = (
                doc['question'] + ' ' +
                doc['answer'] + ' ' +
                doc['category'] + ' ' +
                doc['role'] + ' ' +
                ' '.join(doc['keywords'])
            ).lower()

            # Count keyword matches
            doc_words = set(re.findall(r'\w+', searchable_text))
            matches = len(expanded_words.intersection(doc_words))
            
            # Scoring system
            score = matches
            
            # Keyword substring matching
            critical_keywords = ['liv', 'library', 'mensa', 'cafeteria', 'wifi', 'eduroam', 'parking', 'parkhaus', 'park', 'garage',
                                'vacation', 'ethics', 'permits', 'reimbursement', 'travel', 'expense', 'forms', 'galileo', 
                                'hpc', 'computing', 'dietary', 'restrictions', 'approval', 'committee', 'portal',
                                'dienstreise', 'dienstreiseantrag', 'auszahlungsanordnung', 'heilbronn', 'bildungscampus',
                                'campuscard', 'setup', 'configuration', 'wizard', 'cat', 'vegetarian', 'vegan', 'allergy',
                                'ethik', 'ethikkommission', 'cluster', 'resources', 'lrz']
            for keyword in query_words:
                if keyword in critical_keywords and keyword in searchable_text:
                    score += 3  # High boost for critical keyword substring matches
            
            # Boost for exact phrase matches
            if any(phrase in searchable_text for phrase in [query_lower, ' '.join(query_words)]):
                score += 3
                
            # Boost for question title matches (highest priority)
            if any(word in doc['question'].lower() for word in query_words):
                score += 2
                
            # Boost for category matches
            if any(word in doc['category'].lower() for word in query_words):
                score += 1.5
                
            # Location-specific query boost
            if any(word in query_lower for word in ['where', 'location', 'get to', 'find', 'navigate']) and any(word in searchable_text for word in ['building', 'address', 'campus', 'location', 'room', 'navigate']):
                score += 2
                
            # Room number queries (like L.1.12, building references)
            if re.search(r'[A-Za-z]\.\d+\.\d+|room \d+|building [A-Za-z0-9]', query_lower) and any(word in searchable_text for word in ['building', 'room', 'floor', 'location']):
                score += 3
                
            # Campus-specific boost
            campus_mentioned = None
            if any(word in query_lower for word in ['heilbronn', 'bildungscampus', 'chn']):
                campus_mentioned = 'heilbronn'
            elif any(word in query_lower for word in ['munich', 'münchen', 'garching']):
                campus_mentioned = 'munich'
            elif any(word in query_lower for word in ['singapore']):
                campus_mentioned = 'singapore'
                
            if campus_mentioned and campus_mentioned in searchable_text:
                score += 2
                    
            # Enhanced Role-specific boost
            # Student role detection
            student_keywords = ['student', 'studying', 'international', 'visa', 'foreign', 'bachelor', 'master', 'semester']
            if any(word in query_lower for word in student_keywords):
                if 'student' in doc['role'].lower():
                    score += 2
            
            # Employee role detection
            employee_keywords = ['employee', 'staff', 'work', 'professor', 'lecturer', 'phd', 'postdoc', 
                               'research assistant', 'researcher', 'faculty', 'teaching', 'working']
            if any(word in query_lower for word in employee_keywords):
                if any(role in doc['role'].lower() for role in ['employee', 'lecturer']):
                    score += 3  # Higher boost for employee content
            
            # Special case: PhD students are often both students AND employees
            if 'phd' in query_lower or 'research assistant' in query_lower:
                if any(role in doc['role'].lower() for role in ['student', 'employee']):
                    score += 3  # High boost for dual-role content
            
            # Multi-role context detection (e.g., "PhD student and research assistant")
            if any(combo in query_lower for combo in ['student and', 'also working', 'working as', 'assistant']):
                if 'employee' in doc['role'].lower():
                    score += 4  # Very high boost for employee forms/info
                    
            # Technical query boost
            if any(word in query_lower for word in ['setup', 'configure', 'install', 'technical', 'how to']):
                if any(word in searchable_text for word in ['configuration', 'setup', 'technical', 'install']):
                    score += 1

            # User context-based boost for better matching
            if user_context:
                user_role = user_context.get('role', '').lower()
                user_campus = user_context.get('campus', '').lower()
                
                # Boost entries that match user's role
                if user_role and user_role in doc['role'].lower():
                    score += 3  # High boost for exact role match
                
                # Boost entries that match user's campus
                if user_campus and user_campus.lower() in searchable_text.lower():
                    score += 2  # Campus-specific content boost
                
                # Special boosts for common role variations
                if user_role == 'student' and 'student' in doc['role'].lower():
                    score += 2  # Extra boost for student-specific content
                elif user_role in ['employee', 'staff', 'professor', 'lecturer'] and any(role in doc['role'].lower() for role in ['employee', 'staff']):
                    score += 2  # Extra boost for employee-specific content
                elif user_role == 'visitor' and 'visitor' in doc['role'].lower():
                    score += 2  # Extra boost for visitor-specific content

            if score > 0:
                scored_docs.append((score, doc))

        # Sort by relevance and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs[:top_k]]
    
    def extract_user_info(self, query: str, session_id: str) -> bool:
        """AI-powered extraction of user information from query. Returns True if context was updated."""
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'user_context': {}, 
                'conversation_history': [],
                'pending_question': None,
                'awaiting_context': False
            }
        
        user_context = self.user_sessions[session_id]['user_context']
        context_updated = False
        
        # Use AI to extract role and campus from any format
        extracted = self._ai_extract_context(query)
        
        if extracted.get('role'):
            user_context['role'] = extracted['role']
            self.logger.info(f"DEBUG - AI extracted role: {extracted['role']}")
            context_updated = True
        
        if extracted.get('campus'):
            user_context['campus'] = extracted['campus']
            self.logger.info(f"DEBUG - AI extracted campus: {extracted['campus']}")
            context_updated = True
            
        return context_updated
    
    def _ai_extract_context(self, query: str) -> Dict:
        """Use AI to extract role and campus from user input"""
        try:
            extraction_prompt = f"""Extract the user's role and campus from this text: "{query}"

ROLES (extract exactly as shown):
- student (includes: studying, enrolled, degree, bachelor, master, international student, etc.)
- employee (includes: staff, work, working, job, etc.)
- professor (includes: prof, faculty)
- lecturer (includes: instructor, teacher)
- visitor (includes: visiting, guest, tour)
- phd (includes: doctoral, doctorate, ph.d, phd student)
- postdoc (includes: post-doc, postdoctoral)

CAMPUSES (extract exactly as shown):
- Munich (includes: münchen, main campus)
- Garching
- Heilbronn (includes: bildungscampus, chn)
- Weihenstephan

Examples:
- "employee munich" → role: employee, campus: Munich
- "I am a student at garching" → role: student, campus: Garching
- "visitor heilbronn" → role: visitor, campus: Heilbronn
- "professor" → role: professor, campus: null
- "working at weihenstephan" → role: employee, campus: Weihenstephan

Return ONLY valid JSON format:
{{"role": "extracted_role_or_null", "campus": "extracted_campus_or_null"}}

If no role or campus found, use null for that field."""

            response = self.model.generate_content(extraction_prompt)
            response_text = response.text.strip()
            
            # Try to parse JSON response
            import json
            try:
                # Clean up response (remove any markdown formatting)
                if "```" in response_text:
                    response_text = response_text.split("```")[1].strip()
                    if response_text.startswith("json"):
                        response_text = response_text[4:].strip()
                
                result = json.loads(response_text)
                
                # Validate and normalize the result
                validated_result = {}
                
                if result.get('role') and result['role'] != 'null':
                    role = result['role'].lower()
                    valid_roles = ['student', 'employee', 'professor', 'lecturer', 'visitor', 'phd', 'postdoc']
                    if role in valid_roles:
                        validated_result['role'] = role
                
                if result.get('campus') and result['campus'] != 'null':
                    campus = result['campus'].title()
                    valid_campuses = ['Munich', 'Garching', 'Heilbronn', 'Weihenstephan']
                    if campus in valid_campuses:
                        validated_result['campus'] = campus
                
                self.logger.info(f"DEBUG - AI extraction successful: {validated_result}")
                return validated_result
                
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse AI extraction JSON: {e}, response: {response_text}")
                return {}
                
        except Exception as e:
            self.logger.error(f"AI context extraction failed: {e}")
            # Fallback to simple keyword matching
            return self._fallback_extract_context(query)
        
        return {}
    
    def _fallback_extract_context(self, query: str) -> Dict:
        """Fallback keyword-based extraction if AI fails"""
        query_lower = query.lower()
        result = {}
        
        # Simple role extraction
        if any(word in query_lower for word in ['student', 'studying', 'study']):
            result['role'] = 'student'
        elif any(word in query_lower for word in ['employee', 'staff', 'work', 'working']):
            result['role'] = 'employee'
        elif any(word in query_lower for word in ['professor', 'prof']):
            result['role'] = 'professor'
        elif any(word in query_lower for word in ['lecturer', 'instructor', 'teacher']):
            result['role'] = 'lecturer'
        elif any(word in query_lower for word in ['visitor', 'visiting', 'guest']):
            result['role'] = 'visitor'
        elif any(word in query_lower for word in ['phd', 'doctoral']):
            result['role'] = 'phd'
        elif any(word in query_lower for word in ['postdoc']):
            result['role'] = 'postdoc'
        
        # Simple campus extraction
        if any(word in query_lower for word in ['munich', 'münchen']):
            result['campus'] = 'Munich'
        elif any(word in query_lower for word in ['garching']):
            result['campus'] = 'Garching'
        elif any(word in query_lower for word in ['heilbronn', 'bildungscampus']):
            result['campus'] = 'Heilbronn'
        elif any(word in query_lower for word in ['weihenstephan']):
            result['campus'] = 'Weihenstephan'
        
        return result
    
    def needs_user_info(self, query: str, user_context: Dict) -> str:
        """Context detection with stronger absolute rules"""
        # Get current role and campus
        role = user_context.get('role', '').strip()
        campus = user_context.get('campus', '').strip()
        self.logger.info(f"DEBUG - needs_user_info checking: role='{role}', campus='{campus}', query='{query}'")
        
        # STRONGEST ABSOLUTE RULE: If we have BOTH role and campus stored, NEVER ask again
        if role and campus:
            self.logger.info(f"DEBUG - ABSOLUTE RULE: Have both role='{role}' and campus='{campus}' - NO context needed EVER")
            return None
        
        # ABSOLUTE RULE: If we have role but no campus, only ask for campus for campus-specific questions
        if role and not campus:
            # Only ask for campus if it's clearly a location/campus-specific question
            query_lower = query.lower()
            campus_specific_keywords = ['where', 'location', 'building', 'room', 'parking', 'mensa', 'library', 'map', 'address', 'directions']
            if any(keyword in query_lower for keyword in campus_specific_keywords):
                self.logger.info(f"DEBUG - Have role, need campus for location question: '{query}'")
                return "campus"
            else:
                self.logger.info(f"DEBUG - Have role, question doesn't need campus: '{query}'")
                return None
        
        # Quick pre-filter for obvious personal/casual conversation
        if self._is_personal_conversation(query):
            self.logger.info(f"DEBUG - Detected personal conversation: '{query}'")
            return None
        
        # Use AI to determine if this question needs TUM context (only for new sessions)
        needs_context = self._ai_needs_context_check(query)
        self.logger.info(f"DEBUG - AI says needs context: {needs_context} for query: '{query}'")
        
        if not needs_context:
            return None
        
        # If we need context, check what's missing
        if not role and not campus:
            return "both"  # Need both role and campus
        elif not role:
            return "role"  # Only need role
        elif not campus:
            return "campus"  # Only need campus
        
        return None
    
    def _is_personal_conversation(self, query: str) -> bool:
        """Quick filter for personal/emotional conversation that doesn't need TUM context"""
        query_lower = query.lower()
        
        # Personal/emotional keywords
        personal_keywords = [
            'sad', 'happy', 'tired', 'stressed', 'lonely', 'excited', 'angry', 'depressed',
            'feel', 'feeling', 'emotions', 'mood', 'upset', 'worried', 'anxious', 'nervous',
            'miss', 'love', 'hate', 'like', 'dislike', 'enjoy', 'bored', 'fun', 'funny',
            'family', 'mom', 'dad', 'mother', 'father', 'parents', 'sister', 'brother',
            'friend', 'friends', 'relationship', 'dating', 'boyfriend', 'girlfriend',
            'weather', 'hot', 'cold', 'rain', 'sunny', 'snow', 'temperature',
            'music', 'movie', 'tv', 'game', 'sports', 'hobby', 'weekend', 'vacation',
            'birthday', 'party', 'celebration', 'holiday'
        ]
        
        # Casual greetings and responses
        casual_patterns = [
            'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 'good night',
            'thanks', 'thank you', 'bye', 'goodbye', 'see you', 'take care',
            'yes', 'no', 'okay', 'ok', 'sure', 'fine', 'good', 'great', 'awesome',
            'how are you', 'whats up', "what's up", 'how you doing', 'hows it going'
        ]
        
        # Check for personal keywords
        if any(keyword in query_lower for keyword in personal_keywords):
            return True
            
        # Check for casual patterns
        if any(pattern in query_lower for pattern in casual_patterns):
            return True
            
        # Check for emotional expressions (simple patterns)
        emotional_patterns = [
            'i am ', 'i feel ', 'i think ', 'i believe ', 'i want ', 'i need ',
            'i miss ', 'i love ', 'i hate ', 'i like ', 'my ', 'mine '
        ]
        
        # Only flag as personal if it's a short emotional statement
        if len(query.split()) <= 5:  # Short statements more likely to be personal
            if any(pattern in query_lower for pattern in emotional_patterns):
                # Don't flag as personal if it's about TUM-related needs (food, facilities, etc.)
                tum_related_keywords = ['eat', 'food', 'lunch', 'dinner', 'mensa', 'library', 'parking', 'wifi', 'help', 'study', 'print', 'course', 'exam', 'grade', 'register', 'login', 'card', 'room', 'building', 'location', 'directions']
                if any(keyword in query_lower for keyword in tum_related_keywords):
                    return False  # Not personal - it's TUM-related
                return True
        
        return False
    
    def _ai_needs_context_check(self, query: str) -> bool:
        """Use AI to determine if question needs TUM role/campus context"""
        try:
            check_prompt = f"""You are helping determine if a question needs specific TUM university context (role and campus).

Question: "{query}"

Does this question require knowing the user's role (student/employee/visitor) and campus (Munich/Garching/Heilbronn/Weihenstephan) to answer properly?

Examples that need context (YES):
- "where to eat?" → YES (needs campus for dining locations)
- "how to get laptop?" → YES (needs role and campus for procedures)
- "where is building X?" → YES (needs campus for location)
- "how to register?" → YES (different for students/employees)
- "parking information?" → YES (campus-specific)

Examples that DON'T need context (NO):
- "hi" → NO (casual greeting)
- "i am sad" → NO (personal emotion)
- "i miss my mom" → NO (personal feeling)
- "thanks" → NO (casual response)
- "what is TUMonline?" → NO (general system information)
- "how are you?" → NO (casual conversation)
- "i feel tired" → NO (personal state)
- "good morning" → NO (greeting)
- "i love music" → NO (personal interest)
- "weather is nice" → NO (general comment)

Answer only: YES or NO"""

            response = self.model.generate_content(check_prompt)
            response_text = response.text.strip().upper()
            
            return "YES" in response_text
            
        except Exception as e:
            self.logger.error(f"AI context check failed: {e}")
            # Fallback: if AI fails, err on the side of not asking
            return False
    
    def format_response(self, response: str) -> str:
        """Clean response formatting"""
        # Basic cleanup
        response = response.strip()
        
        # Clean up excessive line breaks
        response = re.sub(r'\n\n\n+', '\n\n', response)
        
        # Remove any accidental "Entry X" references
        response = re.sub(r'(?:Knowledge )?Entry \d+[:\-\s]*', '', response)

        # Add line breaks before numbered lists
        response = re.sub(r'(\d+\.\s)', r'\n\n\1', response)
        
        # Add line breaks before questions
        response = re.sub(r'(\?\s)(\d+\.)', r'\1\n\n\2', response)
        
        # Add line breaks before sentences that start with key indicators
        response = re.sub(r'(\. )([A-Z][a-z]+ you)', r'\1\n\n\2', response)
        response = re.sub(r'(\. )(Once|From|Would|If)', r'\1\n\n\2', response)
        response = re.sub(r'(\. )(Would you|Do you|Are you)', r'\1\n\n\2', response)
        
        # Make system names bold
        response = re.sub(r'\b(TUMonline|Exchange|Outlook|Thunderbird|TUM-ID|TUM-Kennung)\b', r'**\1**', response)
        
        # Make email addresses bold
        response = re.sub(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', r'**\1**', response)
        
        # Clean up any double line breaks
        response = re.sub(r'\n\n+', '\n\n', response)
        
        return response
    
    @log_function_call(logger, "generate_response")
    def generate_response(self, query: str, session_id: str, user_id: str = "anonymous") -> str:
        """Generate response"""
        start_time = time.time()
        
        # Extract user info from current query
        context_just_updated = self.extract_user_info(query, session_id)

        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = {
                'user_context': {}, 
                'conversation_history': [],
                'pending_question': None,
                'awaiting_context': False
            }
        
        # Debug logging
        self.logger.info(f"DEBUG - Query: '{query}'")
        self.logger.info(f"DEBUG - Session context: {self.user_sessions[session_id]['user_context']}")
        self.logger.info(f"DEBUG - Session ID: {session_id}")

        session = self.user_sessions[session_id]
        
        # Check if we just received context and have a pending question
        resuming_question = False
        if context_just_updated and session.get('pending_question') and session.get('awaiting_context'):
            # Resume answering the original question with new context
            original_query = session['pending_question']
            session['pending_question'] = None
            session['awaiting_context'] = False
            resuming_question = True
            # Use original query for search instead of current context response
            self.logger.info(f"Resuming original question: {original_query}")
            query = original_query

        # Add to conversation history
        session['conversation_history'].append(f"User: {query}")

        # Keep only last N exchanges for context
        if len(session['conversation_history']) > 12:  # 6 exchanges = 12 entries
            session['conversation_history'] = session['conversation_history'][-12:]

        # Use optimized search for better results with user context for better matching
        relevant_docs = self.optimized_search(query, top_k=5, user_context=session['user_context'])
        
        # Structure the context
        context = ""
        if relevant_docs:
            for i, doc in enumerate(relevant_docs, 1):
                context += f"\n--- Knowledge Entry {i} ---\n"
                context += f"Category: {doc['category']}\n"
                context += f"Role: {doc['role']}\n"
                context += f"Q: {doc['question']}\n"
                context += f"A: {doc['answer']}\n"
        
        # Include user context
        user_info = ""
        if session['user_context']:
            role = session['user_context'].get('role', '')
            campus = session['user_context'].get('campus', '')
            if role and campus:
                user_info = f"User is a {role} at TUM {campus}"
            elif role:
                user_info = f"User is a {role} at TUM"
            elif campus:
                user_info = f"User is at TUM {campus}"
        
        # Recent conversation context
        recent_conversation = ""
        if len(session['conversation_history']) > 1:
            recent_conversation = "Recent conversation:\n" + "\n".join(session['conversation_history'][-6:]) + "\n"
        
        # Check if we need user info - but skip if context was just updated
        missing_context = None
        if not context_just_updated:  # Only check if context wasn't just provided
            missing_context = self.needs_user_info(query, session['user_context'])
            
        self.logger.info(f"DEBUG - Missing context: {missing_context}")
        self.logger.info(f"DEBUG - Role: '{session['user_context'].get('role', '')}', Campus: '{session['user_context'].get('campus', '')}')")
        self.logger.info(f"DEBUG - Context just updated: {context_just_updated}")
        
        # Create simple context requests
        if missing_context:
            # Store the original question to answer after getting context
            session['pending_question'] = query
            session['awaiting_context'] = True
            
            if missing_context == "both":
                context_response = "Please tell me your role (student/employee/visitor) and campus (Munich/Garching/Heilbronn/Weihenstephan) so I can help you better."
            elif missing_context == "role":
                context_response = "Please tell me your role (student/employee/visitor) so I can provide the right information."
            elif missing_context == "campus":
                context_response = "Please tell me which campus (Munich/Garching/Heilbronn/Weihenstephan) so I can give you specific details."
            
            # Add to conversation history and return
            session['conversation_history'].append(f"Assistant: {context_response}")
            
            # Log chat session for context requests
            log_chat_session(
                user_id=user_id,
                session_id=session_id,
                query=query,
                response=context_response,
                user_role=session['user_context'].get('role'),
                user_campus=session['user_context'].get('campus')
            )
            
            return context_response
        else:
            # Enhanced prompt that leverages AI's conversational intelligence
            user_info = ""
            if session['user_context']:
                role = session['user_context'].get('role', '')
                campus = session['user_context'].get('campus', '')
                if role and campus:
                    user_info = f"You are helping a {role} at TUM {campus} campus."
                elif role:
                    user_info = f"You are helping a {role} at TUM."
                elif campus:
                    user_info = f"You are helping someone at TUM {campus} campus."
            
            # Special handling when resuming a question after getting context
            conversation_context = ""
            if resuming_question:
                conversation_context = f"""
IMPORTANT: The user just provided their role/campus information. Now answer their original question using this context.
The user originally asked: "{query}"
Now that you know they are a {session['user_context'].get('role', '')} at TUM {session['user_context'].get('campus', '')}, provide a helpful, specific answer to their original question.
"""
            else:
                conversation_context = f"""
{recent_conversation}
"""

            prompt = f"""You are an intelligent TUM (Technical University of Munich) assistant with comprehensive knowledge across all campuses.

{user_info}

{conversation_context}

CRITICAL INSTRUCTION - MANDATORY USE OF SPECIFIC INFORMATION:
- You MUST use specific details from the knowledge base when available
- You MUST NOT say "I don't have specific information" when building numbers, locations, or names are provided
- EXAMPLE: If knowledge base shows "Mensa (central cafeteria in Building 8)", you MUST say "You can eat at the Mensa in Building 8"
- EXAMPLE: If knowledge base shows "Café in Building 13", you MUST say "There's also a Café in Building 13"
- Users are frustrated by generic "check the website" responses when you have concrete details
- RULE: Always extract and include specific building numbers, room numbers, and location names from the knowledge base

CONVERSATION INTELLIGENCE:
- Understand the full conversation context and user intent
- For follow-up questions like "where?", "how much?", "when?", understand what the user is referring to from previous context
- Maintain conversation flow naturally - don't lose track of what we were discussing
- Be conversational and intelligent - use context clues to understand what the user really wants
- If user asks "where?" after discussing lunch, they obviously want to know WHERE to get lunch
- Connect related concepts intelligently (lunch = dining = food = mensa = cafeteria)

RESPONSE GUIDELINES:
- FIRST: Look for specific details in the knowledge base and use them
- Provide exact locations, building names, room numbers when available
- Give actionable, practical information with concrete details
- Be helpful and conversational (2-3 sentences typically)
- Only suggest "check the website" if you truly don't have specific information
- Don't reference "Entry X" numbers - speak naturally

KNOWLEDGE BASE WITH SPECIFIC INFORMATION:
{context}

Current question: {query}

REMEMBER: If the knowledge base contains specific details (building numbers, exact locations, names), include them in your response! Users need actionable information, not generic advice."""

        # Generate response using Gemini
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            response_text = f"I apologize, but I'm experiencing technical difficulties. Please try again later or contact IT support at servicedesk@tum.de"
        
        # Apply formatting improvements
        formatted_response = self.format_response(response_text)
        
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
            search_method="optimized",
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
        # Create session storage immediately
        self.user_sessions[session_id] = {'user_context': {}, 'conversation_history': []}
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