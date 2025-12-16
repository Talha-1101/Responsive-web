#!/usr/bin/env python3
"""
Installation helper script for the Responsive Website Testing Tool backend
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def check_python_version():
    """Check if Python version is 3.10+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def main():
    print("🛠️  Responsive Website Testing Tool - Backend Installation")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("\n💡 If pip install fails, try:")
        print("   pip install --upgrade pip")
        print("   pip install -r requirements.txt --no-cache-dir")
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browser"):
        print("\n💡 If Playwright install fails, try:")
        print("   playwright install-deps")
        print("   playwright install")
    
    # Check for optional Lighthouse
    print("\n🔄 Checking for Lighthouse (optional for performance auditing)...")
    lighthouse_available = run_command("lighthouse --version", "Checking Lighthouse availability")
    
    if not lighthouse_available:
        print("⚠️  Lighthouse not found - performance auditing will use mock data")
        print("💡 To install Lighthouse: npm install -g lighthouse")
    
    # Create sessions directory
    sessions_dir = Path("sessions")
    sessions_dir.mkdir(exist_ok=True)
    print("✅ Created sessions directory")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_content = """# Responsive Website Testing Tool Configuration

# AI Integration (Optional - uses mock responses if not set)
# Claude (Anthropic)
CLAUDE_API_KEY=mock-key-for-development
CLAUDE_MODEL=claude-3-sonnet-20240229
CLAUDE_MAX_TOKENS=2000

# Gemini (Google)
# Set GEMINI_API_KEY to enable Gemini. If set, Gemini will be used by default.
GEMINI_API_KEY=AIzaSyCar7UN6yoPSN0qxPbpYve7WfzIq0Rus8w
GEMINI_MODEL=gemini-1.5-pro
GEMINI_MAX_TOKENS=2000

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./website_tester.db

# Analysis Settings
MAX_ANALYSIS_TIME=300
SCREENSHOT_TIMEOUT=30
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env configuration file")
        print("💡 To enable real AI with Gemini, set GEMINI_API_KEY in .env and restart the server.")
    
    print("\n🎉 Installation completed successfully!")
    print("\n🚀 To start the backend server:")
    print("   python main.py")
    print("\n📖 The API will be available at: http://localhost:8000")
    print("📖 API documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main()