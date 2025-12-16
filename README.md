# 🛠️ Responsive Website Testing Tool

A comprehensive, local-only, AI-integrated tool for analyzing website responsiveness, accessibility, SEO, and performance across multiple devices and screen sizes.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### 🔍 **Comprehensive Analysis**
- **Responsive Testing**: Screenshots across 7 viewport sizes (320px to 2560px)
- **Accessibility Audit**: WCAG compliance checking and accessibility barriers detection
- **SEO Analysis**: Meta tags, headings, structured data, and search engine optimization
- **Performance Audit**: Lighthouse-powered Core Web Vitals and performance metrics
- **Platform Detection**: Automatic CMS/framework identification (WordPress, Shopify, React, etc.)
- **Form Testing**: Automatic form detection, validation, and interaction testing

### 🤖 **AI-Powered Insights**
- **Claude AI Integration**: Intelligent analysis and fix suggestions
- **Code Generation**: Specific HTML/CSS/JS fixes for detected issues
- **Priority Recommendations**: AI-ranked issues by importance and impact
- **Plain English Explanations**: Technical issues explained in understandable language

### 📊 **Detailed Reporting**
- **Real-time Progress**: WebSocket-powered live updates during analysis
- **Interactive Results**: Tabbed interface with detailed breakdowns
- **Downloadable Reports**: Complete ZIP packages with screenshots and JSON data
- **Score Grading**: Overall quality scores (A-F) with detailed breakdowns

### 🏠 **Local-Only Operation**
- **Privacy First**: No data sent to external services (except optional AI analysis)
- **Self-Hosted**: Runs entirely on your local machine
- **No Signup Required**: Start analyzing immediately
- **Offline Capable**: Works without internet connection (except for AI features)

## 🏗️ Architecture

```
responsive-website-tester/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                # FastAPI application entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # SQLite database setup
│   ├── services/              # Core analysis services
│   │   ├── website_analyzer.py    # Main analysis orchestrator
│   │   ├── screenshot_service.py  # Viewport testing
│   │   ├── seo_analyzer.py        # SEO analysis
│   │   ├── form_tester.py         # Form testing
│   │   ├── platform_detector.py   # CMS detection
│   │   ├── ai_service.py          # AI integration
│   │   └── lighthouse_service.py  # Performance auditing
│   └── utils/                 # Utility modules
└── frontend/                  # React TypeScript Frontend
    ├── src/
    │   ├── components/        # Reusable UI components
    │   ├── pages/            # Main application pages
    │   ├── hooks/            # Custom React hooks
    │   ├── services/         # API communication
    │   └── types/            # TypeScript interfaces
    └── public/               # Static assets
```

## 🚀 Quick Start

### Prerequisites

**Required:**
- **Python 3.10+** - Backend runtime
- **Node.js 16+** - Frontend development
- **npm 8+** - Package manager

**Optional:**
- **Lighthouse CLI** - For performance auditing (will use mock data if not available)

### 📦 Installation & Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd responsive-website-tester
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Optional: Install Lighthouse for performance auditing
npm install -g lighthouse
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Build the frontend (optional, for production)
npm run build
```

### 🏃‍♂️ Running the Application

#### Start Backend Server
```bash
cd backend
# Activate virtual environment if not already active
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start FastAPI server
python main.py
# Or using uvicorn directly:
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend API will be available at: `http://localhost:8000`

#### Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### 🎯 Usage

1. **Open your browser** and navigate to `http://localhost:3000`
2. **Enter a website URL** (e.g., `https://example.com`)
3. **Click "Analyze Website"** to start the analysis
4. **Watch real-time progress** as the tool tests different viewports
5. **Review comprehensive results** with scores, issues, and AI suggestions
6. **Download the complete report** as a ZIP file

## 🛠️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# AI Integration (Optional)
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_MODEL=claude-3-sonnet-20240229

# Server Configuration
HOST=127.0.0.1
PORT=8000
DEBUG=true

# Database
DATABASE_URL=sqlite:///./website_tester.db

# Analysis Settings
MAX_ANALYSIS_TIME=300
SCREENSHOT_TIMEOUT=30
```

### Viewport Configuration

Modify `backend/config.py` to customize viewport breakpoints:

```python
viewport_breakpoints = [
    {"name": "Mobile Small", "width": 320, "height": 568},
    {"name": "Mobile Medium", "width": 375, "height": 667},
    {"name": "Mobile Large", "width": 425, "height": 812},
    {"name": "Tablet", "width": 768, "height": 1024},
    {"name": "Tablet Landscape", "width": 1024, "height": 768},
    {"name": "Desktop", "width": 1440, "height": 900},
    {"name": "Desktop Large", "width": 2560, "height": 1440},
]
```

## 📊 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze` | Start website analysis |
| `GET` | `/status/{session_id}` | Get analysis progress |
| `GET` | `/results/{session_id}` | Get complete results |
| `GET` | `/download/{session_id}` | Download report ZIP |
| `WebSocket` | `/ws/{session_id}` | Real-time updates |

### Example API Usage

```python
import requests

# Start analysis
response = requests.post('http://localhost:8000/analyze', 
                        json={'url': 'https://example.com'})
session_id = response.json()['session_id']

# Check status
status = requests.get(f'http://localhost:8000/status/{session_id}')
print(f"Progress: {status.json()['progress']}%")

# Get results when complete
results = requests.get(f'http://localhost:8000/results/{session_id}')
print(f"Overall score: {results.json()['scores']['overall']}")
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Example Test URLs
Try these URLs to test the tool:
- `https://github.com` - Good responsive design
- `https://tailwindcss.com` - Excellent modern site
- `https://example.com` - Simple test site
- `https://old-website.com` - Sites with potential issues

## 🔧 Troubleshooting

### Common Issues

#### Backend Issues

**Playwright Installation Fails:**
```bash
# Try manual installation
playwright install chromium
# Or install system dependencies
playwright install-deps
```

**Port Already in Use:**
```bash
# Change port in main.py or use environment variable
uvicorn main:app --port 8001
```

**Database Issues:**
```bash
# Delete and recreate database
rm website_tester.db
python main.py  # Will recreate automatically
```

#### Frontend Issues

**Node.js Version Conflicts:**
```bash
# Use Node Version Manager
nvm use 18
npm install
```

**Build Failures:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS Issues:**
- Ensure backend is running on `http://localhost:8000`
- Check `vite.config.ts` proxy configuration

#### Analysis Issues

**Screenshots Not Capturing:**
- Verify Playwright installation: `playwright install`
- Check if the target website is accessible
- Some sites block automated browsers

**Performance Audit Missing:**
- Install Lighthouse: `npm install -g lighthouse`
- Check if Node.js is available in PATH
- Tool will use mock data if Lighthouse is unavailable

**AI Analysis Not Working:**
- Set `CLAUDE_API_KEY` in `.env` file
- Tool provides mock AI responses by default
- Real AI integration requires Anthropic API access

## 🚀 Deployment

### Docker Deployment (Optional)

```dockerfile
# Dockerfile example
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Security**: Configure proper CORS origins
2. **Performance**: Use production ASGI server (Gunicorn)
3. **Monitoring**: Add logging and health checks
4. **Storage**: Configure session cleanup
5. **Rate Limiting**: Implement request throttling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for all frontend code
- Add tests for new features
- Update documentation
- Ensure all checks pass

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - Frontend user interface library
- **Playwright** - Browser automation
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Lighthouse** - Performance auditing
- **Anthropic Claude** - AI analysis (optional)

## 📞 Support

For support and questions:
- Create an [Issue](https://github.com/your-repo/issues)
- Check [Documentation](https://github.com/your-repo/wiki)
- Review [FAQ](https://github.com/your-repo/discussions)

---

**Built with ❤️ for developers who care about responsive design and web accessibility.**