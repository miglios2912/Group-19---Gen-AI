"""
Statistics and Analytics module for TUM Chatbot Backend
Tracks usage, performance, and user interactions
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import os

# Handle imports for both module and direct execution
try:
    from .config import get_config
    from .logger import get_logger
except ImportError:
    from config import get_config
    from logger import get_logger

logger = get_logger(__name__)

@dataclass
class ChatInteraction:
    """Chat interaction data structure"""
    timestamp: datetime
    user_id: str
    session_id: str
    query: str
    response: str
    search_method: str
    search_results_count: int
    response_time: float
    user_role: Optional[str] = None
    user_campus: Optional[str] = None
    query_length: int = 0
    response_length: int = 0

@dataclass
class SearchPerformance:
    """Search performance data structure"""
    timestamp: datetime
    query: str
    search_method: str
    results_count: int
    search_time: float
    avg_similarity: float
    max_similarity: float
    min_similarity: float

@dataclass
class UserSession:
    """User session data structure"""
    session_id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    interaction_count: int = 0
    total_time: float = 0.0
    user_role: Optional[str] = None
    user_campus: Optional[str] = None

class StatisticsManager:
    """Manages statistics and analytics data"""
    
    def __init__(self):
        self.config = get_config()
        self.db_path = self.config.statistics.stats_db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the statistics database with required tables"""
        try:
            # Ensure database directory exists
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                
                # Chat interactions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chat_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        query TEXT NOT NULL,
                        response TEXT NOT NULL,
                        search_method TEXT NOT NULL,
                        search_results_count INTEGER NOT NULL,
                        response_time REAL NOT NULL,
                        user_role TEXT,
                        user_campus TEXT,
                        query_length INTEGER NOT NULL,
                        response_length INTEGER NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Search performance table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS search_performance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        query TEXT NOT NULL,
                        search_method TEXT NOT NULL,
                        results_count INTEGER NOT NULL,
                        search_time REAL NOT NULL,
                        avg_similarity REAL NOT NULL,
                        max_similarity REAL NOT NULL,
                        min_similarity REAL NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # User sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        user_id TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        interaction_count INTEGER DEFAULT 0,
                        total_time REAL DEFAULT 0.0,
                        user_role TEXT,
                        user_campus TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Query analytics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS query_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_hash TEXT UNIQUE NOT NULL,
                        query_text TEXT NOT NULL,
                        frequency INTEGER DEFAULT 1,
                        avg_response_time REAL,
                        success_rate REAL DEFAULT 1.0,
                        first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_seen TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON chat_interactions(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_interactions(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session_id ON chat_interactions(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_search_timestamp ON search_performance(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON user_sessions(session_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_query_hash ON query_analytics(query_hash)")
                
                conn.commit()
                logger.info("Statistics database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize statistics database: {e}")
            raise
    
    def anonymize_user_id(self, user_id: str) -> str:
        """Anonymize user ID if configured"""
        if self.config.statistics.anonymize_data:
            return hashlib.sha256(user_id.encode()).hexdigest()[:16]
        return user_id
    
    def record_chat_interaction(self, interaction: ChatInteraction):
        """Record a chat interaction"""
        if not self.config.statistics.enable_statistics:
            return
        
        try:
            logger.debug(f"Recording chat interaction for session: {interaction.session_id}")
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                logger.debug("Database connection established for chat interaction")
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO chat_interactions 
                    (timestamp, user_id, session_id, query, response, search_method, 
                     search_results_count, response_time, user_role, user_campus, 
                     query_length, response_length)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    interaction.timestamp.isoformat(),
                    self.anonymize_user_id(interaction.user_id),
                    interaction.session_id,
                    interaction.query,
                    interaction.response,
                    interaction.search_method,
                    interaction.search_results_count,
                    interaction.response_time,
                    interaction.user_role,
                    interaction.user_campus,
                    interaction.query_length,
                    interaction.response_length
                ))
                
                # Update query analytics
                logger.debug("Calling _update_query_analytics")
                try:
                    self._update_query_analytics(interaction.query, interaction.response_time, conn)
                    logger.debug("_update_query_analytics completed successfully")
                except Exception as e:
                    logger.error(f"Exception in _update_query_analytics: {e}")
                    logger.error(f"Exception type: {type(e).__name__}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")
                
                conn.commit()
                logger.debug(f"Chat interaction recorded successfully for session {interaction.session_id}")
                
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logger.error(f"Database locked during chat interaction recording: {e}")
                logger.error(f"Session ID: {interaction.session_id}")
                logger.error(f"User ID: {interaction.user_id}")
                logger.error(f"Query: {interaction.query[:50]}...")
                logger.error(f"Database path: {self.db_path}")
                logger.error(f"Current timestamp: {datetime.utcnow().isoformat()}")
            else:
                logger.error(f"SQLite operational error during chat interaction recording: {e}")
        except Exception as e:
            logger.error(f"Failed to record chat interaction: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Session ID: {interaction.session_id}")
            logger.error(f"User ID: {interaction.user_id}")
    
    def record_search_performance(self, performance: SearchPerformance):
        """Record search performance metrics"""
        if not self.config.statistics.enable_statistics:
            return
        
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO search_performance 
                    (timestamp, query, search_method, results_count, search_time,
                     avg_similarity, max_similarity, min_similarity)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    performance.timestamp.isoformat(),
                    performance.query,
                    performance.search_method,
                    performance.results_count,
                    performance.search_time,
                    performance.avg_similarity,
                    performance.max_similarity,
                    performance.min_similarity
                ))
                
                conn.commit()
                logger.debug(f"Recorded search performance for {performance.search_method}")
                
        except Exception as e:
            logger.error(f"Failed to record search performance: {e}")
    
    def start_user_session(self, session_id: str, user_id: str, 
                          user_role: Optional[str] = None, 
                          user_campus: Optional[str] = None):
        """Start tracking a user session"""
        if not self.config.statistics.track_user_sessions:
            return
        
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_sessions 
                    (session_id, user_id, start_time, user_role, user_campus, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    self.anonymize_user_id(user_id),
                    datetime.utcnow().isoformat(),
                    user_role,
                    user_campus,
                    datetime.utcnow().isoformat()
                ))
                
                conn.commit()
                logger.debug(f"Started tracking session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to start user session: {e}")
    
    def end_user_session(self, session_id: str):
        """End tracking a user session"""
        if not self.config.statistics.track_user_sessions:
            return
        
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE user_sessions 
                    SET end_time = ?, updated_at = ?
                    WHERE session_id = ?
                """, (
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                    session_id
                ))
                
                conn.commit()
                logger.debug(f"Ended tracking session {session_id}")
                
        except Exception as e:
            logger.error(f"Failed to end user session: {e}")
    
    def _check_database_status(self):
        """Check database status and log useful debugging information"""
        try:
            with sqlite3.connect(self.db_path, timeout=5) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA database_list;")
                databases = cursor.fetchall()
                logger.debug(f"Database list: {databases}")
                
                cursor.execute("PRAGMA journal_mode;")
                journal_mode = cursor.fetchone()
                logger.debug(f"Journal mode: {journal_mode}")
                
                cursor.execute("PRAGMA busy_timeout;")
                busy_timeout = cursor.fetchone()
                logger.debug(f"Busy timeout: {busy_timeout}")
                
        except Exception as e:
            logger.error(f"Failed to check database status: {e}")

    def _update_query_analytics(self, query: str, response_time: float, conn=None):
        """Update query analytics"""
        if not self.config.statistics.track_query_analytics:
            return
        
        query_hash = hashlib.sha256(query.lower().strip().encode()).hexdigest()
        
        try:
            logger.debug(f"Attempting to update query analytics for hash: {query_hash[:8]}...")
            self._check_database_status()  # Add debugging info
            
            # Use provided connection or create new one
            if conn is None:
                logger.debug("Creating new database connection for query analytics")
                conn = sqlite3.connect(self.db_path, timeout=30)
                conn.execute("PRAGMA journal_mode=WAL;")
                should_close = True
            else:
                logger.debug("Using existing database connection for query analytics")
                should_close = False
            
            cursor = conn.cursor()
            
            # Check if query exists
            cursor.execute("SELECT frequency, avg_response_time FROM query_analytics WHERE query_hash = ?", (query_hash,))
            result = cursor.fetchone()
            
            if result:
                frequency, current_avg = result
                new_frequency = frequency + 1
                new_avg = ((current_avg * frequency) + response_time) / new_frequency
                
                logger.debug(f"Updating existing query analytics: frequency {frequency} -> {new_frequency}")
                cursor.execute("""
                    UPDATE query_analytics 
                    SET frequency = ?, avg_response_time = ?, last_seen = ?
                    WHERE query_hash = ?
                """, (new_frequency, new_avg, datetime.utcnow().isoformat(), query_hash))
            else:
                logger.debug(f"Inserting new query analytics for hash: {query_hash[:8]}...")
                cursor.execute("""
                    INSERT INTO query_analytics 
                    (query_hash, query_text, avg_response_time)
                    VALUES (?, ?, ?)
                """, (query_hash, query, response_time))
            
            if should_close:
                conn.commit()
                conn.close()
            logger.debug("Query analytics update completed successfully")
            
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                logger.error(f"Database locked during query analytics update: {e}")
                logger.error(f"Query hash: {query_hash[:8]}..., Query: {query[:50]}...")
                # Log additional context
                logger.error(f"Database path: {self.db_path}")
                logger.error(f"Current timestamp: {datetime.utcnow().isoformat()}")
                self._check_database_status()  # Add debugging info when lock occurs
            else:
                logger.error(f"SQLite operational error during query analytics update: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during query analytics update: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Query hash: {query_hash[:8]}..., Query: {query[:50]}...")
    
    def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive statistics for the specified period"""
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
                
                # Total interactions
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_interactions 
                    WHERE timestamp >= ?
                """, (start_date,))
                total_interactions = cursor.fetchone()[0]
                
                # Average response time
                cursor.execute("""
                    SELECT AVG(response_time) FROM chat_interactions 
                    WHERE timestamp >= ?
                """, (start_date,))
                avg_response_time = cursor.fetchone()[0] or 0
                
                # Search method distribution
                cursor.execute("""
                    SELECT search_method, COUNT(*) FROM chat_interactions 
                    WHERE timestamp >= ? GROUP BY search_method
                """, (start_date,))
                search_methods = dict(cursor.fetchall())
                
                # User role distribution
                cursor.execute("""
                    SELECT user_role, COUNT(*) FROM chat_interactions 
                    WHERE timestamp >= ? AND user_role IS NOT NULL 
                    GROUP BY user_role
                """, (start_date,))
                user_roles = dict(cursor.fetchall())
                
                # Campus distribution
                cursor.execute("""
                    SELECT user_campus, COUNT(*) FROM chat_interactions 
                    WHERE timestamp >= ? AND user_campus IS NOT NULL 
                    GROUP BY user_campus
                """, (start_date,))
                campuses = dict(cursor.fetchall())
                
                # Most common queries
                cursor.execute("""
                    SELECT query_text, frequency FROM query_analytics 
                    ORDER BY frequency DESC LIMIT 10
                """)
                top_queries = cursor.fetchall()
                
                # Active sessions
                cursor.execute("""
                    SELECT COUNT(*) FROM user_sessions 
                    WHERE end_time IS NULL OR end_time >= ?
                """, (start_date,))
                active_sessions = cursor.fetchone()[0]
                
                return {
                    'period_days': days,
                    'total_interactions': total_interactions,
                    'avg_response_time': round(avg_response_time, 3),
                    'search_methods': search_methods,
                    'user_roles': user_roles,
                    'campuses': campuses,
                    'top_queries': top_queries,
                    'active_sessions': active_sessions,
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def get_performance_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get performance metrics for the specified period"""
        try:
            with sqlite3.connect(self.db_path, timeout=30) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                cursor = conn.cursor()
                start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
                
                # Search performance by method
                cursor.execute("""
                    SELECT search_method, 
                           AVG(search_time) as avg_time,
                           AVG(results_count) as avg_results,
                           AVG(avg_similarity) as avg_similarity,
                           COUNT(*) as total_searches
                    FROM search_performance 
                    WHERE timestamp >= ? 
                    GROUP BY search_method
                """, (start_date,))
                search_performance = cursor.fetchall()
                
                # Response time percentiles
                cursor.execute("""
                    SELECT response_time FROM chat_interactions 
                    WHERE timestamp >= ? ORDER BY response_time
                """, (start_date,))
                response_times = [row[0] for row in cursor.fetchall()]
                
                if response_times:
                    p50 = response_times[len(response_times) // 2]
                    p95 = response_times[int(len(response_times) * 0.95)]
                    p99 = response_times[int(len(response_times) * 0.99)]
                else:
                    p50 = p95 = p99 = 0
                
                return {
                    'period_days': days,
                    'search_performance': search_performance,
                    'response_time_percentiles': {
                        'p50': round(p50, 3),
                        'p95': round(p95, 3),
                        'p99': round(p99, 3)
                    },
                    'generated_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {}

# Global statistics manager instance
stats_manager = StatisticsManager() 