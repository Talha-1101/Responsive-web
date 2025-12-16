"""
Configuration settings for the Responsive Website Testing Tool
"""

import os
from pathlib import Path
from typing import List, Dict, Any

# Try to import BaseSettings from the correct location
try:
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        from pydantic import BaseSettings
    except ImportError:
        # Fallback for very old versions
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # App Settings
    app_name: str = "Responsive Website Testing Tool"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Settings
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Database Settings
    database_url: str = "sqlite:///./website_tester.db"
    
    # Gemini (Google) settings (values pulled from environment variables)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    gemini_max_tokens: int = int(os.getenv("GEMINI_MAX_TOKENS", "2000"))
    
    # Analysis Settings
    max_analysis_time: int = 300  # 5 minutes max per analysis
    screenshot_timeout: int = 30  # 30 seconds per screenshot
    
    # Viewport Breakpoints for Responsive Testing
    viewport_breakpoints: list = [
        {"name": "Mobile Small", "width": 320, "height": 568},      # iPhone SE
        {"name": "Mobile Medium", "width": 375, "height": 667},     # iPhone 8
        {"name": "Mobile Large", "width": 425, "height": 812},      # iPhone X
        {"name": "Tablet", "width": 768, "height": 1024},           # iPad
        {"name": "Tablet Landscape", "width": 1024, "height": 768}, # iPad Landscape
        {"name": "Desktop", "width": 1440, "height": 900},          # Desktop
        {"name": "Desktop Large", "width": 2560, "height": 1440},   # Large Desktop
    ]
    
    # File Storage Settings
    sessions_dir: str = "sessions"
    max_session_age_hours: int = 24  # Auto-cleanup after 24 hours
    
    # Device Profiles for True Emulation
    device_profiles: dict = {
        "Mobile Small": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 375, "height": 667},
            "device_scale_factor": 2,
            "is_mobile": True,
            "has_touch": True
        },
        "Mobile": {
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 390, "height": 844},
            "device_scale_factor": 3,
            "is_mobile": True,
            "has_touch": True
        },
        "Tablet": {
            "user_agent": "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "viewport": {"width": 820, "height": 1180},
            "device_scale_factor": 2,
            "is_mobile": True,
            "has_touch": True
        },
        "Tablet Landscape": {
             "user_agent": "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
             "viewport": {"width": 1180, "height": 820},
             "device_scale_factor": 2,
             "is_mobile": True,
             "has_touch": True
        },
        "Desktop Large": {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "viewport": {"width": 1920, "height": 1080},
            "device_scale_factor": 1,
            "is_mobile": False,
            "has_touch": False
        }
    }

    # Network Profiles for Simulation
    network_profiles: dict = {
        "4G": {
            "offline": False,
            "downloadThroughput": 4 * 1024 * 1024,  # 4 Mbps
            "uploadThroughput": 3 * 1024 * 1024,    # 3 Mbps
            "latency": 20
        },
        "Slow 3G": {
            "offline": False,
            "downloadThroughput": 500 * 1024,       # 500 kbps
            "uploadThroughput": 500 * 1024,
            "latency": 400
        },
        "Offline": {
            "offline": True,
            "downloadThroughput": 0,
            "uploadThroughput": 0,
            "latency": 0
        }
    }
    
    # Playwright Settings
    playwright_timeout: int = 30000  # 30 seconds
    playwright_headless: bool = True
    playwright_user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # SEO Check Settings
    seo_checks: dict = {
        "title": {"required": True, "min_length": 10, "max_length": 60},
        "description": {"required": True, "min_length": 120, "max_length": 160},
        "h1": {"required": True, "max_count": 1},
        "viewport_meta": {"required": True},
        "lang_attribute": {"required": True},
    }
    
    # Form Testing Settings
    form_test_data: dict = {
        "email": "test@example.com",
        "name": "Test User",
        "phone": "+1234567890",
        "text": "This is a test message",
        "number": "123",
        "url": "https://example.com",
        "password": "TestPassword123!",
    }
    
    # Platform Detection Patterns
    platform_patterns: dict = {
        "WordPress": [
            "/wp-content/",
            "/wp-includes/",
            "wp-json",
            'name="generator" content="WordPress',
        ],
        "Shopify": [
            "cdn.shopify.com",
            "shop.shopify.com",
            "Shopify.theme",
            "shopify-section",
        ],
        "Webflow": [
            "webflow.com",
            "data-wf-",
            "webflow-style",
        ],
        "Wix": [
            "wix.com",
            "_wixCIDX",
            "wix-theme",
        ],
        "Squarespace": [
            "squarespace.com",
            "squarespace-cdn",
            "sqs-block",
        ],
        "React": [
            "react",
            "__REACT_DEVTOOLS_GLOBAL_HOOK__",
            "data-reactroot",
        ],
        "Vue": [
            "vue.js",
            "__VUE__",
            "v-",
        ],
        "Angular": [
            "angular",
            "ng-",
            "_ngcontent",
        ]
    }
    
    # Issue Severity Levels
    severity_levels: dict = {
        "high": {
            "color": "#ef4444",  # red-500
            "priority": 1,
            "issues": [
                "missing_viewport_meta",
                "horizontal_scroll",
                "broken_layout",
                "missing_alt_text",
                "poor_contrast"
            ]
        },
        "medium": {
            "color": "#f59e0b",  # amber-500  
            "priority": 2,
            "issues": [
                "small_touch_targets",
                "missing_title",
                "missing_description",
                "slow_loading"
            ]
        },
        "low": {
            "color": "#10b981",  # emerald-500
            "priority": 3,
            "issues": [
                "missing_h1",
                "image_optimization",
                "caching_issues"
            ]
        }
    }
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create global settings instance
settings = Settings()

# ADDED: Config class for main.py compatibility
class Config:
    """Simple config class for main.py compatibility"""
    def __init__(self):
        # Load from settings
        for key, value in settings.__dict__.items():
            setattr(self, key, value)

# Create directories if they don't exist
def create_directories():
    """Create necessary directories"""
    Path(settings.sessions_dir).mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

# Initialize directories
create_directories()