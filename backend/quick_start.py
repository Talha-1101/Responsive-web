#!/usr/bin/env python3
"""
Quick start script for the Responsive Website Testing Tool
Installs dependencies and starts the server
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
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        if exit_on_fail:
            print(f"   Error code: {e.returncode}")
            return False
        return False

def install_package(package, description):
    """Install a single package"""
    return run_command(f"pip install {package}", f"Installing {description}", exit_on_fail=False)

def main():
    print("🛠️  Responsive Website Testing Tool - Quick Start")
    print("=" * 60)
    
    # Install core dependencies one by one for better compatibility
    core_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn[standard]", "ASGI server"),
        ("sqlalchemy", "Database ORM"),
        ("aiosqlite", "Async SQLite driver"),
        ("playwright", "Browser automation"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment variables"),
        ("aiofiles", "Async file operations"),
        ("beautifulsoup4", "HTML parsing"),
        ("lxml", "XML/HTML parser"),
        ("Pillow", "Image processing"),
        ("websockets", "WebSocket support"),
        ("httpx", "HTTP client"),
    ]
    
    print("📦 Installing Python packages...")
    success_count = 0
    for package, description in core_packages:
        if install_package(package, description):
            success_count += 1
        time.sleep(0.5)  # Small delay between installs
    
    print(f"\n📊 Installed {success_count}/{len(core_packages)} packages successfully")
    
    # Install Playwright browsers
    print("\n🌐 Installing browser for automation...")
    if run_command("playwright install chromium", "Installing Chromium browser", exit_on_fail=False):
        print("✅ Browser installation successful")
    else:
        print("⚠️  Browser installation failed - will try to continue")
    
    # Create necessary directories
    print("\n📁 Setting up directories...")
    directories = ["sessions", "sessions/screenshots", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    # Create .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("\n⚙️  Creating configuration file...")
        env_content = """# Responsive Website Testing Tool Configuration
# You can modify these settings as needed

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Database (SQLite)
DATABASE_URL=sqlite:///./website_tester.db

# Analysis Settings
MAX_ANALYSIS_TIME=300
SCREENSHOT_TIMEOUT=30

# AI Integration (Optional - uses mock responses by default)
CLAUDE_API_KEY=mock-key-for-development
CLAUDE_MODEL=claude-3-sonnet-20240229
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env configuration file")
    
    print("\n🎉 Setup completed!")
    print("\n" + "="*60)
    print("🚀 STARTING THE SERVER...")
    print("="*60)
    
    # Start the server
    try:
        print("📡 Backend API will be available at: http://localhost:8000")
        print("📖 API Documentation at: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print()
        
        # Import and run the main app
        os.system("python main.py")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\n💡 Try running manually with: python main.py")

if __name__ == "__main__":
    main()