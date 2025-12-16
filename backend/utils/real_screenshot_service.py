"""
Real Screenshot Service - Windows Compatible
Handles screenshot saving with graceful fallbacks
"""

import os
import base64
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PLACEHOLDER_IMAGE_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAASwAAABvCAYAAACDE0XpAAAACXBIWXMAAAsSAAALEgHS3X78AAAA"
    "B3RJTUUH5QsXEiIYth2VINAAABl0RVh0Q3JlYXRpb24gVGltZQAwOS8yMy8yMdxhQ5oAAACJSURB"
    "VHja7cExAQAAAMKg9U9tCF8gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAPgGBAABWs7IkQAAAABJRU5ErkJggg=="
)


class RealScreenshotService:
    """Screenshot service with Windows compatibility"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.screenshots_dir = Path("sessions") / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_screenshot_from_base64(self, viewport_name: str, base64_data: str) -> str:
        """Save screenshot from base64 data"""
        try:
            # Clean up viewport name for filename
            clean_name = viewport_name.lower().replace(" ", "_").replace("-", "_")
            filename = f"{self.session_id}_{clean_name}.png"
            filepath = self.screenshots_dir / filename
            
            # Decode base64 and save
            screenshot_bytes = base64.b64decode(base64_data)
            
            with open(filepath, 'wb') as f:
                f.write(screenshot_bytes)
            
            # Return path relative to the 'sessions' directory served at /static
            # FastAPI mounts StaticFiles(directory="sessions") at /static,
            # so the public URL will be /static/<relative_path>.
            # We want /static/screenshots/<file>, not /static/sessions/screenshots/<file>.
            relative_path = f"screenshots/{filename}"
            logger.info(f"✅ Screenshot saved: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save screenshot for {viewport_name}: {e}")
            return f"error_saving_screenshot_{viewport_name}"
    
    async def save_screenshot_from_buffer(self, viewport_name: str, screenshot_buffer: bytes) -> str:
        """Save screenshot from byte buffer"""
        try:
            clean_name = viewport_name.lower().replace(" ", "_").replace("-", "_")
            filename = f"{self.session_id}_{clean_name}.png"
            filepath = self.screenshots_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(screenshot_buffer)
            
            relative_path = f"screenshots/{filename}"
            logger.info(f"✅ Screenshot saved from buffer: {relative_path}")
            
            return relative_path
            
        except Exception as e:
            logger.error(f"❌ Failed to save screenshot buffer for {viewport_name}: {e}")
            return f"error_saving_screenshot_{viewport_name}"
    
    def get_screenshot_path(self, viewport_name: str) -> str:
        """Get the expected path for a screenshot (relative to 'sessions' root)"""
        clean_name = viewport_name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{self.session_id}_{clean_name}.png"
        return f"screenshots/{filename}"
    
    def cleanup_session_screenshots(self) -> bool:
        """Clean up all screenshots for this session"""
        try:
            pattern = f"{self.session_id}_*.png"
            deleted_count = 0
            
            for screenshot_file in self.screenshots_dir.glob(pattern):
                screenshot_file.unlink()
                deleted_count += 1
            
            logger.info(f"🧹 Cleaned up {deleted_count} screenshots for session {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup screenshots for session {self.session_id}: {e}")
            return False

    @classmethod
    def ensure_placeholder_assets(cls) -> Path:
        """Ensure placeholder image exists for HTTP-only mode."""
        placeholders_dir = Path("sessions") / "placeholders"
        placeholders_dir.mkdir(parents=True, exist_ok=True)
        placeholder_path = placeholders_dir / "http_only.png"
        if not placeholder_path.exists():
            placeholder_bytes = base64.b64decode(PLACEHOLDER_IMAGE_B64)
            placeholder_path.write_bytes(placeholder_bytes)
        return placeholder_path

    @classmethod
    def get_http_only_placeholder_path(cls) -> str:
        """Return relative path to placeholder image served via /static."""
        placeholder_path = cls.ensure_placeholder_assets()
        return f"placeholders/{placeholder_path.name}"