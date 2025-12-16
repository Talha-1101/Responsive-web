"""
Simplified database setup using synchronous SQLite for better compatibility
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SimpleDatabase:
    """Simple SQLite database manager"""
    
    def __init__(self, db_path: str = "website_tester.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                # Analysis sessions table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS analysis_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        url TEXT NOT NULL,
                        status TEXT DEFAULT 'started',
                        progress REAL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP NULL,
                        screenshots_data TEXT NULL,
                        issues_data TEXT NULL,
                        seo_data TEXT NULL,
                        performance_data TEXT NULL,
                        platform_data TEXT NULL,
                        ai_analysis TEXT NULL,
                        responsiveness_score REAL NULL,
                        accessibility_score REAL NULL,
                        seo_score REAL NULL,
                        performance_score REAL NULL,
                        error_message TEXT NULL
                    )
                """)
                
                # Detected issues table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS detected_issues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        category TEXT NOT NULL,
                        issue_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        description TEXT NOT NULL,
                        element_selector TEXT NULL,
                        viewport TEXT NULL,
                        ai_suggestion TEXT NULL,
                        fix_code TEXT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES analysis_sessions (session_id)
                    )
                """)
                
                conn.commit()
                logger.info("✅ Database initialized successfully")
                
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def create_session(self, session_id: str, url: str) -> Dict:
        """Create new analysis session"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO analysis_sessions (session_id, url, created_at)
                    VALUES (?, ?, ?)
                """, (session_id, url, datetime.utcnow().isoformat()))
                
                conn.commit()
                
                # Return the created session
                cursor = conn.execute("""
                    SELECT * FROM analysis_sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                return dict(row) if row else {}
                
        except Exception as e:
            logger.error(f"Error creating session {session_id}: {e}")
            raise
    
    def update_session_status(self, session_id: str, status: str, progress: float = None, error: str = None) -> bool:
        """Update session status and progress"""
        try:
            with self.get_connection() as conn:
                updates = ["status = ?", "updated_at = ?"]
                params = [status, datetime.utcnow().isoformat()]
                
                if progress is not None:
                    updates.append("progress = ?")
                    params.append(progress)
                
                if error:
                    updates.append("error_message = ?")
                    params.append(error)
                
                if status == "completed":
                    updates.append("completed_at = ?")
                    params.append(datetime.utcnow().isoformat())
                
                params.append(session_id)
                
                conn.execute(f"""
                    UPDATE analysis_sessions 
                    SET {', '.join(updates)}
                    WHERE session_id = ?
                """, params)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM analysis_sessions WHERE session_id = ?
                """, (session_id,))
                
                row = cursor.fetchone()
                if row:
                    session_dict = dict(row)
                    # Parse JSON fields
                    json_fields = ['screenshots_data', 'issues_data', 'seo_data', 
                                 'performance_data', 'platform_data', 'ai_analysis']
                    for field in json_fields:
                        if session_dict.get(field):
                            try:
                                session_dict[field] = json.loads(session_dict[field])
                            except (json.JSONDecodeError, TypeError):
                                session_dict[field] = {}
                    
                    return session_dict
                return None
                
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return None
    
    def save_analysis_results(self, session_id: str, results: Dict) -> bool:
        """Save complete analysis results"""
        try:
            with self.get_connection() as conn:
                # Convert complex objects to JSON strings
                screenshots_json = json.dumps(results.get("viewports", []))
                issues_json = json.dumps(results.get("issues", []))
                seo_json = json.dumps(results.get("seo", {}))
                performance_json = json.dumps(results.get("performance", {}))
                platform_json = json.dumps(results.get("platform", {}))
                ai_analysis_json = json.dumps(results.get("ai_analysis", {}))
                
                scores = results.get("scores", {})
                
                conn.execute("""
                    UPDATE analysis_sessions 
                    SET screenshots_data = ?, issues_data = ?, seo_data = ?, 
                        performance_data = ?, platform_data = ?, ai_analysis = ?,
                        responsiveness_score = ?, accessibility_score = ?, 
                        seo_score = ?, performance_score = ?,
                        status = 'completed', completed_at = ?, updated_at = ?
                    WHERE session_id = ?
                """, (
                    screenshots_json, issues_json, seo_json,
                    performance_json, platform_json, ai_analysis_json,
                    scores.get("responsiveness", 0), scores.get("accessibility", 0),
                    scores.get("seo", 0), scores.get("performance", 0),
                    datetime.utcnow().isoformat(), datetime.utcnow().isoformat(),
                    session_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving results for {session_id}: {e}")
            return False
    
    def add_detected_issue(self, session_id: str, issue_data: Dict) -> bool:
        """Add a detected issue"""
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO detected_issues (
                        session_id, category, issue_type, severity, description,
                        element_selector, viewport, ai_suggestion, fix_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    issue_data.get("category"),
                    issue_data.get("type"),
                    issue_data.get("severity"),
                    issue_data.get("description"),
                    issue_data.get("selector"),
                    issue_data.get("viewport"),
                    issue_data.get("ai_suggestion"),
                    issue_data.get("fix_code")
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error adding issue for {session_id}: {e}")
            return False
    
    def get_session_issues(self, session_id: str) -> List[Dict]:
        """Get all issues for a session"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT * FROM detected_issues WHERE session_id = ?
                    ORDER BY created_at DESC
                """, (session_id,))
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error getting issues for {session_id}: {e}")
            return []
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Clean up sessions older than specified hours"""
        try:
            with self.get_connection() as conn:
                cutoff_time = datetime.utcnow().timestamp() - (hours * 3600)
                
                # Delete old issues first
                cursor = conn.execute("""
                    DELETE FROM detected_issues 
                    WHERE session_id IN (
                        SELECT session_id FROM analysis_sessions 
                        WHERE created_at < datetime(?, 'unixepoch')
                    )
                """, (cutoff_time,))
                
                issues_deleted = cursor.rowcount
                
                # Delete old sessions
                cursor = conn.execute("""
                    DELETE FROM analysis_sessions 
                    WHERE created_at < datetime(?, 'unixepoch')
                """, (cutoff_time,))
                
                sessions_deleted = cursor.rowcount
                conn.commit()
                
                logger.info(f"Cleaned up {sessions_deleted} old sessions and {issues_deleted} issues")
                return sessions_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT session_id, url, status, progress, created_at, updated_at
                    FROM analysis_sessions 
                    ORDER BY created_at DESC
                    LIMIT 100
                """)
                
                return [dict(row) for row in cursor.fetchall()]
                
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

# Create global database instance
db = SimpleDatabase()

# Wrapper functions for compatibility with existing code
async def init_db():
    """Initialize database (async wrapper)"""
    db.init_db()

async def get_db():
    """Get database instance (async wrapper)"""
    return db

class DatabaseService:
    """Database service class for compatibility"""
    
    @staticmethod
    async def create_session(session_id: str, url: str):
        return db.create_session(session_id, url)
    
    @staticmethod
    async def update_session_status(session_id: str, status: str, progress: float = None, error: str = None):
        return db.update_session_status(session_id, status, progress, error)
    
    @staticmethod
    async def get_session(session_id: str):
        return db.get_session(session_id)
    
    @staticmethod
    async def save_analysis_results(session_id: str, results: Dict):
        return db.save_analysis_results(session_id, results)
    
    @staticmethod
    async def add_detected_issue(session_id: str, issue_data: Dict):
        return db.add_detected_issue(session_id, issue_data)
    
    @staticmethod
    async def get_session_issues(session_id: str):
        return db.get_session_issues(session_id)
    
    @staticmethod
    async def cleanup_old_sessions(hours: int = 24):
        return db.cleanup_old_sessions(hours)

# Create database service instance
db_service = DatabaseService()