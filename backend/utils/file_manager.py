"""
File manager for handling analysis files and results
"""

import asyncio
import logging
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager:
    """Simple file manager for analysis results and screenshots"""
    
    def __init__(self):
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
    
    async def save_screenshot(self, session_id: str, viewport_name: str, screenshot_data: bytes) -> str:
        """Save screenshot data to file"""
        try:
            session_dir = self.sessions_dir / session_id
            session_dir.mkdir(exist_ok=True)
            
            # Create screenshots subdirectory
            screenshots_dir = session_dir / "screenshots"
            screenshots_dir.mkdir(exist_ok=True)
            
            # Save screenshot
            filename = f"{viewport_name.lower().replace(' ', '_')}.png"
            file_path = screenshots_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(screenshot_data)
            
            logger.info(f"Saved screenshot: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return ""
    
    async def save_report_data(self, session_id: str, results: Dict[str, Any]) -> str:
        """Save analysis results to JSON file"""
        try:
            session_dir = self.sessions_dir / session_id
            session_dir.mkdir(exist_ok=True)
            
            # Save results as JSON
            results_file = session_dir / "analysis_results.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Saved analysis results: {results_file}")
            return str(results_file)
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            return ""
    
    async def create_results_archive(self, session_id: str, results: Dict[str, Any]) -> Path:
        """Create ZIP archive of all session files"""
        try:
            session_dir = self.sessions_dir / session_id
            
            if not session_dir.exists():
                raise FileNotFoundError(f"Session directory not found: {session_dir}")
            
            # Create ZIP file
            zip_filename = f"analysis_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            zip_path = session_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all files in session directory
                for file_path in session_dir.rglob('*'):
                    if file_path.is_file() and file_path.name != zip_filename:
                        # Add file to ZIP with relative path
                        arcname = file_path.relative_to(session_dir)
                        zipf.write(file_path, arcname)
                
                # Add summary report
                summary = self._create_summary_report(results)
                zipf.writestr("ANALYSIS_SUMMARY.txt", summary)
            
            logger.info(f"Created results archive: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Failed to create archive: {e}")
            raise
    
    def _create_summary_report(self, results: Dict[str, Any]) -> str:
        """Create a human-readable summary report"""
        try:
            url = results.get("url", "Unknown URL")
            timestamp = results.get("timestamp", "Unknown time")
            scores = results.get("scores", {})
            issues = results.get("issues", [])
            
            summary = f"""
WEBSITE ANALYSIS SUMMARY
========================

Website: {url}
Analysis Date: {timestamp}

OVERALL SCORES:
- Overall Score: {scores.get('overall', 'N/A')}/100
- Responsive Design: {scores.get('responsive', 'N/A')}/100  
- Accessibility: {scores.get('accessibility', 'N/A')}/100
- SEO: {scores.get('seo', 'N/A')}/100
- Performance: {scores.get('performance', 'N/A')}/100

ISSUES FOUND ({len(issues)} total):
"""
            
            # Group issues by severity
            high_issues = [i for i in issues if i.get('severity') == 'high']
            medium_issues = [i for i in issues if i.get('severity') == 'medium']
            low_issues = [i for i in issues if i.get('severity') == 'low']
            
            if high_issues:
                summary += f"\nHIGH PRIORITY ({len(high_issues)} issues):\n"
                for issue in high_issues:
                    summary += f"- {issue.get('description', 'No description')}\n"
            
            if medium_issues:
                summary += f"\nMEDIUM PRIORITY ({len(medium_issues)} issues):\n"
                for issue in medium_issues:
                    summary += f"- {issue.get('description', 'No description')}\n"
            
            if low_issues:
                summary += f"\nLOW PRIORITY ({len(low_issues)} issues):\n"
                for issue in low_issues:
                    summary += f"- {issue.get('description', 'No description')}\n"
            
            summary += f"""

PLATFORM INFORMATION:
Platform: {results.get('platform', {}).get('platform', 'Unknown')}

FILES INCLUDED:
- analysis_results.json (Complete analysis data)
- screenshots/ (Responsive design screenshots)
- ANALYSIS_SUMMARY.txt (This summary)

Generated by Responsive Website Testing Tool
"""
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {e}"
    
    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """Clean up old session files"""
        try:
            cleaned = 0
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            for session_dir in self.sessions_dir.iterdir():
                if session_dir.is_dir():
                    # Check if directory is older than cutoff
                    if session_dir.stat().st_mtime < cutoff_time:
                        # Remove entire session directory
                        import shutil
                        shutil.rmtree(session_dir)
                        cleaned += 1
                        logger.info(f"Cleaned up old session: {session_dir.name}")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Failed to cleanup sessions: {e}")
            return 0