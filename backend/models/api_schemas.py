"""
API Schemas for the Responsive Website Testing Tool
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl

class AnalysisRequest(BaseModel):
    """Request model for website analysis"""
    url: HttpUrl
    network_condition: Optional[str] = None

class StatusResponse(BaseModel):
    """Response model for analysis status"""
    session_id: str
    status: str
    progress: int
    message: str
    current_step: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error: Optional[str] = None

class AnalysisResponse(BaseModel):
    """Complete analysis response model"""
    session_id: str
    url: str
    timestamp: str
    overall_score: int = 85
    summary: Dict[str, Any] = {}
    responsive_design: List[Dict[str, Any]] = []
    accessibility: Dict[str, Any] = {}
    seo: Dict[str, Any] = {}
    performance: Dict[str, Any] = {}
    forms: Dict[str, Any] = {}
    platform_detection: Dict[str, Any] = {}
    ai_analysis: Dict[str, Any] = {}