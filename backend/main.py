#!/usr/bin/env python3
"""
Corrected main.py with proper imports for your file structure + Windows Playwright Fix
"""

import os
import sys
import logging
import asyncio
import uuid
import base64
import textwrap
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# CRITICAL: Windows-specific fix for Playwright subprocess issues
if sys.platform.startswith('win'):
    # Set Windows-specific event loop policy for subprocess support
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print("🪟 Windows asyncio policy set for Playwright compatibility")

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import your modules with proper error handling
try:
    from models.api_schemas import AnalysisRequest, AnalysisResponse, StatusResponse
    from services.ai_service import AIService
    from utils.session_manager import SessionManager
    from utils.file_manager import FileManager
    from config import Config
    from database import init_db, get_db, db_service
    
    # Import from your existing file structure
    from services.website_analyzer import WebsiteAnalyzer
    from utils.real_screenshot_service import RealScreenshotService
    
except ImportError as e:
    logging.error(f"Import error: {e}")
    print(f" Import error: {e}")
    print("Please ensure all files are in the correct directory structure")
    sys.exit(1)

# Load .env so os.getenv picks up configuration
load_dotenv(dotenv_path=str(project_root / ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Responsive Website Testing Tool - REAL ANALYSIS",
    description="AI-powered website analysis with ACTUAL responsive design testing",
    version="2.0.0"
)

# Configure CORS
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time
from collections import defaultdict

# Simple in-memory rate limiter
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 20, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean up old requests
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.period]
        
        if len(self.requests[client_ip]) >= self.calls:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again later."}
            )
            
        self.requests[client_ip].append(now)
        return await call_next(request)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Restrict methods
    allow_headers=["*"],
)

# Add Trusted Host Middleware (Security)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.ngrok-free.app"]
)

# Add Rate Limiting (Security)
app.add_middleware(RateLimitMiddleware, calls=50, period=60)  # 50 requests per minute

# Serve static files (screenshots)
app.mount("/static", StaticFiles(directory="sessions"), name="static")

# Global services
config = Config()
session_manager = SessionManager()
file_manager = FileManager()
ai_service = AIService()

# Session storage - In production, use Redis or database
active_sessions: Dict[str, Dict[str, Any]] = {}

def update_session_status(
    session_id: str,
    status: str,
    progress: int,
    message: str,
    current_step: str,
    error: Optional[str] = None,
) -> None:
    """Update in-memory + database session status with safe fallbacks."""
    session = active_sessions.setdefault(
        session_id,
        {
            "session_id": session_id,
            "status": "started",
            "progress": 0,
            "message": "Initializing...",
            "current_step": "initialization",
            "start_time": datetime.now().isoformat(),
        },
    )
    session.update(
        {
            "status": status,
            "progress": progress,
            "message": message,
            "current_step": current_step,
            "updated_at": datetime.now().isoformat(),
        }
    )
    if error:
        session["error"] = error
    elif "error" in session:
        session.pop("error")

    async def _persist():
        try:
            await db_service.update_session_status(
                session_id=session_id,
                status=status,
                progress=progress,
                error=error,
            )
        except Exception as db_error:
            logger.error(f"Failed to persist session {session_id} status: {db_error}")

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and not loop.is_closed():
        loop.create_task(_persist())
    else:
        asyncio.run(_persist())

async def run_real_analysis(session_id: str, url: str, network_condition: Optional[str] = None) -> None:
    """Execute the REAL website analysis workflow."""
    logger.info(f"🔬 REAL analysis started for session {session_id} ({url})")
    analyzer = WebsiteAnalyzer()
    screenshot_service = RealScreenshotService(session_id)
    analysis_results: Optional[Dict[str, Any]] = None

    try:
        update_session_status(
            session_id,
            "processing",
            10,
            "Preparing REAL analyzer...",
            "initializing",
        )

        # Define progress callback
        async def update_progress(progress: int, message: str, step: str):
            update_session_status(session_id, "processing", progress, message, step)
            # Short sleep to ensure updates are sent via WebSocket (handled by update_session_status background task)
            await asyncio.sleep(0.1)

        analysis_results = await analyzer.analyze_website(
            url, 
            session_id=session_id, 
            progress_callback=update_progress,
            network_condition=network_condition
        )
        if not analysis_results:
            raise RuntimeError("Analyzer returned no results")

        update_session_status(
            session_id,
            "processing",
            65,
            "Processing REAL analysis results...",
            "processing_results",
        )

        timestamp = datetime.now().isoformat()
        analysis_results.setdefault("session_id", session_id)
        analysis_results.setdefault("url", url)
        analysis_results.setdefault("url", url)
        analysis_results.setdefault("timestamp", timestamp)

        # 🤖 AI ANALYSIS INTEGRATION
        try:
            update_session_status(
                session_id,
                "processing",
                75,
                "Generating AI insights...",
                "ai_analysis",
            )
            # Run AI analysis
            ai_results = await ai_service.analyze_website(analysis_results)
            analysis_results["ai_analysis"] = ai_results
            
            # Map AI suggestions to issues
            for issue in analysis_results.get("issues", []):
                suggestion = await ai_service.get_fix_suggestion(issue)
                issue["ai_suggestion"] = suggestion
                
            logger.info(f"✅ AI analysis completed for {session_id}")
        except Exception as e:
            logger.error(f"⚠️ AI analysis failed: {e}")
            analysis_results["ai_analysis"] = {"error": str(e)}

        viewports = analysis_results.get("viewports", [])
        for viewport in viewports:
            screenshot_data = viewport.pop("screenshot_data", None)
            if screenshot_data:
                screenshot_path = await screenshot_service.save_screenshot_from_base64(
                    viewport.get("name", "viewport"),
                    screenshot_data,
                )
                viewport["screenshot_path"] = screenshot_path

        active_sessions[session_id].update(
            {
                "status": "processing",
                "progress": 85,
                "message": "Finalizing REAL analysis results...",
                "current_step": "finalizing",
                "results": analysis_results,
                "updated_at": timestamp,
            }
        )

        update_session_status(
            session_id,
            "processing",
            95,
            "Saving REAL analysis data...",
            "saving_results",
        )
        await db_service.save_analysis_results(session_id, analysis_results)

        update_session_status(
            session_id,
            "completed",
            100,
            "Analysis completed successfully!",
            "completed",
        )
        active_sessions[session_id].update(
            {
                "status": "completed",
                "progress": 100,
                "message": "Analysis completed successfully!",
                "current_step": "completed",
                "results": analysis_results,
                "end_time": datetime.now().isoformat(),
            }
        )
        logger.info(f"✅ REAL analysis completed for {url} ({session_id})")

    except Exception as exc:
        logger.error(f"❌ REAL analysis failed for {url}: {exc}")
        update_session_status(
            session_id,
            "failed",
            100,
            "Analysis completed with limitations",
            "failed",
            error=str(exc),
        )
        if session_id in active_sessions:
            active_sessions[session_id].update(
                {
                    "status": "completed",
                    "progress": 100,
                    "message": "Analysis completed with some limitations",
                    "current_step": "completed",
                    "error": str(exc),
                    "results": analysis_results,
                    "end_time": datetime.now().isoformat(),
                }
            )
    finally:
        if (
            session_id in active_sessions
            and active_sessions[session_id].get("status") != "completed"
        ):
            active_sessions[session_id].update(
                {
                    "status": "completed",
                    "progress": 100,
                    "current_step": "completed",
                    "end_time": datetime.now().isoformat(),
                }
            )

async def verify_playwright_installation():
    """Verify Playwright is properly installed and browser is available"""
    try:
        from playwright.async_api import async_playwright
        
        logger.info("🔧 Testing Playwright browser launch...")
        
        playwright = await async_playwright().start()
        
        # Build launch args per platform
        common_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
        ]
        if sys.platform.startswith('win'):
            launch_args = common_args + [
                '--disable-setuid-sandbox',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--disable-gpu',
                '--single-process',  # Windows-specific stabilization
                '--disable-web-security'
            ]
        else:
            # Minimal args for stability
            launch_args = common_args + [
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        
        browser = await playwright.webkit.launch(headless=True)
        
        # Quick test to ensure browser works
        page = await browser.new_page()
        await page.goto('data:text/html,<h1>Playwright Test</h1>')
        content = await page.content()
        await page.close()
        await browser.close()
        await playwright.stop()
        
        if 'Playwright Test' in content:
            logger.info("✅ Playwright browser test successful on Windows")
            return True
        else:
            logger.error("❌ Playwright browser test failed - content check failed")
            return False
        
    except Exception as e:
        logger.error(f"❌ Playwright browser test failed: {e}")
        logger.error("💡 Try running: playwright install chromium")
        return False

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    logger.info("🚀 Starting REAL Responsive Website Testing Tool...")
    
    # Check if Playwright is available and working
    try:
        import playwright
        logger.info("✅ Playwright package is available")
        
        # Test actual browser launch with Windows compatibility
        playwright_works = await verify_playwright_installation()
        if playwright_works:
            logger.info("✅ Playwright browser verification successful")
        else:
            logger.warning("⚠️ Playwright browser verification failed - analysis may not work properly")
            logger.warning("💡 Install Playwright browsers: playwright install chromium")
            
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        raise
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Create sessions directory
    Path("sessions").mkdir(exist_ok=True)
    Path("sessions/screenshots").mkdir(exist_ok=True)
    
    logger.info("✅ Application startup complete - REAL ANALYSIS READY!")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "analysis_type": "REAL",
        "platform": sys.platform,
        "services": {}
    }
    
    # Check Playwright
    try:
        import playwright
        health_status["services"]["playwright"] = "available"
    except ImportError:
        health_status["services"]["playwright"] = "not_installed"
    
    # Check database
    try:
        health_status["services"]["database"] = "connected" if db_service else "disconnected"
    except:
        health_status["services"]["database"] = "error"
    
    return health_status

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Responsive Website Testing Tool - REAL ANALYSIS", 
        "version": "2.0.0",
        "docs": "/docs",
        "platform": sys.platform,
        "status": "ready"
    }

@app.post("/analyze")
async def start_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Start REAL website analysis"""
    session_id = str(uuid.uuid4())[:8]
    
    logger.info(f"🔍 Starting REAL analysis for: {request.url}")
    
    # Initialize session
    active_sessions[session_id] = {
        "session_id": session_id,
        "url": str(request.url),
        "status": "started",
        "progress": 0,
        "message": "Initializing real browser analysis...",
        "current_step": "initialization",
        "start_time": datetime.now().isoformat(),
        "results": None,
        "error": None
    }
    
    # Start background analysis with REAL analyzer
    background_tasks.add_task(run_real_analysis, session_id, str(request.url), request.network_condition)
    
    return {
        "session_id": session_id,
        "status": "started",
        "message": "REAL analysis started successfully"
    }

@app.get("/status/{session_id}")
async def get_analysis_status(session_id: str):
    """Get analysis status"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return StatusResponse(**session)

@app.get("/results/{session_id}")
async def get_analysis_results(session_id: str):
    """Get analysis results"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed. Current status: {session['status']}"
        )
    
    if session["results"] is None:
        raise HTTPException(status_code=500, detail="Results not available")
    
    # Normalize issues so frontend always has expected fields
    results = session["results"]
    normalized_issues = []
    for issue in results.get("issues", []):
        if not isinstance(issue, dict):
            continue
        issue_type = issue.get("issue_type") or issue.get("type") or "general_issue"
        category = issue.get("category") or "general"
        severity = issue.get("severity") or "medium"
        description = issue.get("description") or issue_type.replace("_", " ")
        normalized = {
            **issue,
            "issue_type": issue_type,
            "category": category,
            "severity": severity,
            "description": description,
        }
        normalized_issues.append(normalized)
    results["issues"] = normalized_issues
    
    results["issues"] = normalized_issues
    
    return results

class GuideRequest(BaseModel):
    category: str
    context: Dict[str, Any]

@app.post("/guide")
async def get_guide(request: GuideRequest):
    """Get AI improvement guide for a specific category"""
    guide = await ai_service.get_category_guide(request.category, request.context)
    return {"guide": guide}

@app.get("/download/{session_id}")
async def download_results(session_id: str):
    """Download analysis results as text report"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    # Create simple text report
    results = session["results"]
    report_content = textwrap.dedent(
        f"""
WEBSITE ANALYSIS REPORT
======================

Website: {results.get('url', 'Unknown')}
Analysis Date: {results.get('timestamp', 'Unknown')}
Session ID: {session_id}

OVERALL SCORES:
- Overall Score: {results.get('scores', {}).get('overall', 'N/A')}/100
- Responsiveness: {results.get('scores', {}).get('responsiveness', 'N/A')}/100
- Accessibility: {results.get('scores', {}).get('accessibility', 'N/A')}/100
- SEO: {results.get('scores', {}).get('seo', 'N/A')}/100
- Performance: {results.get('scores', {}).get('performance', 'N/A')}/100

ISSUES FOUND: {len(results.get('issues', []))}

VIEWPORTS TESTED: {len(results.get('viewports', []))}

PLATFORM: {results.get('platform', {}).get('platform', 'Unknown')}

Generated by Responsive Website Testing Tool
"""
    ).strip() + "\n"

    report_path = Path("sessions") / f"report_{session_id}.txt"
    report_path.write_text(report_content, encoding="utf-8")

    logger.info(f"📄 Report generated for session {session_id}: {report_path}")
    return FileResponse(
        path=str(report_path),
        media_type="text/plain",
        filename=f"website_analysis_{session_id}.txt",
    )

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: HTTPException):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={"detail": f"Endpoint not found: {request.url.path}"}
    )

@app.exception_handler(500)
async def custom_500_handler(request: Request, exc: Exception):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

if __name__ == "__main__":
    # Additional Windows-specific configuration at runtime
    if sys.platform.startswith('win'):
        # Ensure the event loop policy is set
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        logger.info("🪟 Windows-specific asyncio configuration applied")
    
    logger.info("🚀 Starting REAL analysis server...")
    
    # Check for Playwright installation
    try:
        import playwright
        logger.info("✅ Playwright is available")
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )