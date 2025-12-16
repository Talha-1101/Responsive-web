#!/usr/bin/env python3
"""
Complete Setup Script for Real Website Analysis Tool
This will set up everything needed for ACTUAL website testing
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description, exit_on_fail=True):
    """Run a command with better error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        if exit_on_fail:
            return False
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_real_analyzer_files():
    """Create the real analyzer files in the correct locations"""
    
    # Create the real_website_analyzer.py file
    real_analyzer_content = '''"""
Real Website Analyzer - Complete Implementation
"""
# Note: Copy the content from the first artifact here
# This is the actual implementation that replaces the mock analyzer
'''
    
    # Write to services directory
    services_dir = Path("services")
    services_dir.mkdir(exist_ok=True)
    
    with open(services_dir / "real_website_analyzer.py", "w") as f:
        f.write("# Copy the Real Website Analyzer code here from the artifact")
    
    print("📝 Created placeholder for real_website_analyzer.py")
    print("   ⚠️  IMPORTANT: Copy the Real Website Analyzer code from the provided artifact")

def main():
    print("🛠️  Real Website Testing Tool - Complete Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install core dependencies
    core_packages = [
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.23",
        "aiosqlite>=0.19.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.1",
        "httpx>=0.25.2",
        "python-multipart>=0.0.6",
    ]
    
    print("📦 Installing core Python packages...")
    for package in core_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}", exit_on_fail=False):
            print(f"⚠️  Failed to install {package}")
    
    # Install critical packages for real analysis
    critical_packages = [
        "playwright>=1.40.0",
        "beautifulsoup4>=4.12.2", 
        "lxml>=4.9.3",
        "Pillow>=10.1.0",
        "anthropic>=0.7.8"
    ]
    
    print("\n🔧 Installing critical packages for REAL analysis...")
    for package in critical_packages:
        if not run_command(f"pip install {package}", f"Installing {package.split('>=')[0]}", exit_on_fail=False):
            print(f"❌ CRITICAL: Failed to install {package}")
    
    # Install Playwright browsers - ESSENTIAL for real analysis
    print("\n🌐 Installing Playwright browsers (ESSENTIAL for real testing)...")
    if run_command("playwright install chromium", "Installing Chromium browser", exit_on_fail=False):
        print("✅ Chromium browser installed successfully")
    else:
        print("❌ CRITICAL: Chromium installation failed!")
        print("💡 Try manually: playwright install-deps && playwright install chromium")
    
    # Create necessary directories
    print("\n📁 Setting up directories...")
    directories = ["sessions", "sessions/screenshots", "logs", "services", "utils", "models"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    # Create enhanced .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚙️  Creating enhanced configuration file...")
        env_content = """# REAL Website Testing Tool Configuration

# AI Integration - REAL Claude API (get from https://console.anthropic.com/)
CLAUDE_API_KEY=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
CLAUDE_MODEL=claude-sonnet-4-20250514

# For MOCK AI (testing without API key)
# CLAUDE_API_KEY=mock-key-for-development

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./website_tester.db

# Analysis Settings
MAX_ANALYSIS_TIME=300
SCREENSHOT_TIMEOUT=30

# Browser Settings (for real analysis)
PLAYWRIGHT_TIMEOUT=30000
PLAYWRIGHT_HEADLESS=true
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created enhanced .env configuration file")
    
    # Create placeholder files for the real analyzer
    create_real_analyzer_files()
    
    # Test the installation
    print("\n🧪 Testing installation...")
    
    # Test Playwright
    playwright_test = run_command("python -c \"import playwright; print('Playwright OK')\"", 
                                "Testing Playwright import", exit_on_fail=False)
    
    # Test FastAPI
    fastapi_test = run_command("python -c \"import fastapi; print('FastAPI OK')\"", 
                             "Testing FastAPI import", exit_on_fail=False)
    
    # Test BeautifulSoup
    bs4_test = run_command("python -c \"import bs4; print('BeautifulSoup OK')\"", 
                         "Testing BeautifulSoup import", exit_on_fail=False)
    
    print("\n" + "="*60)
    print("🎉 REAL ANALYSIS SETUP COMPLETE!")
    print("="*60)
    
    if playwright_test and fastapi_test and bs4_test:
        print("✅ All core components installed successfully")
        print("\n🚀 NEXT STEPS:")
        print("1. Copy the Real Website Analyzer code from the artifacts")
        print("2. Replace your existing website_analyzer.py with the real implementation")
        print("3. Update your main.py with the new version")
        print("4. Start the server: python main.py")
        print("\n📖 The API will provide REAL analysis at: http://localhost:8000")
        print("📖 Test with your frontend at: http://localhost:3000")
        
    else:
        print("⚠️  Some components failed to install")
        print("💡 Try running the setup again or install missing packages manually")
    
    print("\n🔧 Manual Commands if needed:")
    print("   pip install playwright beautifulsoup4 lxml")
    print("   playwright install chromium") 
    print("   python main.py")

if __name__ == "__main__":
    main()