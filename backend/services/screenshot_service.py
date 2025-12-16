"""
Real Screenshot Service - Handles actual screenshot capture and file management
"""

import asyncio
import logging
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealScreenshotService:
    """Service for capturing and managing real screenshots"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.screenshots_dir = Path("sessions") / session_id / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_screenshot(self, viewport_name: str, screenshot_data: bytes) -> str:
        """Save screenshot data to file and return the file path"""
        try:
            # Create filename
            safe_name = viewport_name.lower().replace(' ', '_').replace('(', '').replace(')', '')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.png"
            
            # Full file path
            file_path = self.screenshots_dir / filename
            
            # Save the screenshot
            with open(file_path, 'wb') as f:
                f.write(screenshot_data)
            
            # Return relative path for storage in database
            relative_path = f"sessions/{self.session_id}/screenshots/{filename}"
            
            logger.info(f"✅ Screenshot saved: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save screenshot for {viewport_name}: {e}")
            return ""
    
    async def save_screenshot_from_base64(self, viewport_name: str, screenshot_b64: str) -> str:
        """Save screenshot from base64 string"""
        try:
            # Decode base64 to bytes
            screenshot_data = base64.b64decode(screenshot_b64)
            return await self.save_screenshot(viewport_name, screenshot_data)
        except Exception as e:
            logger.error(f"❌ Failed to decode and save screenshot: {e}")
            return ""
    
    def get_screenshot_url(self, file_path: str) -> str:
        """Get URL for accessing screenshot"""
        # This would typically be served by a static file server
        return f"/static/{file_path}"
    
    def cleanup_old_screenshots(self, hours: int = 24) -> int:
        """Clean up old screenshot files"""
        try:
            deleted = 0
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            for file_path in self.screenshots_dir.glob("*.png"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted += 1
            
            logger.info(f"🧹 Cleaned up {deleted} old screenshots")
            return deleted
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up screenshots: {e}")
            return 0