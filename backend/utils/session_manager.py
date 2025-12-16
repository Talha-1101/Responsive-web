"""
Session manager for handling analysis sessions
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionManager:
    """Simple session manager for website analysis sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str, url: str) -> Dict[str, Any]:
        """Create a new analysis session"""
        session_data = {
            "session_id": session_id,
            "url": url,
            "status": "created",
            "progress": 0,
            "message": "Session created",
            "current_step": "initialization",
            "created_at": datetime.now().isoformat(),
            "results": None
        }
        
        self.sessions[session_id] = session_data
        logger.info(f"Created session {session_id} for {url}")
        return session_data
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id].update(kwargs)
            self.sessions[session_id]["last_updated"] = datetime.now().isoformat()
            return True
        return False
    
    def update_progress(self, session_id: str, progress: int, message: str, step: str = ""):
        """Update session progress"""
        if session_id in self.sessions:
            self.sessions[session_id].update({
                "progress": progress,
                "message": message,
                "current_step": step or message,
                "last_updated": datetime.now().isoformat()
            })
    
    def complete_session(self, session_id: str, results: Dict[str, Any]):
        """Mark session as completed with results"""
        if session_id in self.sessions:
            self.sessions[session_id].update({
                "status": "completed",
                "progress": 100,
                "message": "Analysis completed",
                "current_step": "completed",
                "results": results,
                "completed_at": datetime.now().isoformat()
            })
    
    def set_session_error(self, session_id: str, error: str):
        """Set session error status"""
        if session_id in self.sessions:
            self.sessions[session_id].update({
                "status": "failed",
                "message": f"Analysis failed: {error}",
                "current_step": "failed",
                "error": error,
                "failed_at": datetime.now().isoformat()
            })