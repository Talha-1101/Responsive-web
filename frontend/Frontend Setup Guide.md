# 🚀 Frontend Setup Guide

This guide will help you set up the Responsive Website Testing Tool frontend from scratch.

## 📋 Prerequisites

- **Node.js 16+** and **npm 8+**
- Backend server running on port 8000

## 🔧 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
cd frontend
node setup.cjs
npm run dev
```

### Option 2: Step-by-Step Manual Setup

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Create Required Directories

```bash
mkdir -p public
mkdir -p src/components/ui
mkdir -p src/components/analysis
mkdir -p src/components/layout
mkdir -p src/pages
mkdir -p src/hooks
mkdir -p src/services
mkdir -p src/types
mkdir -p src/utils
```

#### 3. Create Public Files

Create `public/robots.txt`:
```
User-agent: *
Allow: /
```

#### 4. Start Development Server

```bash
npm run dev
```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── favicon.svg
│   ├── site.webmanifest
│   └── robots.txt
├── src/
│   ├── components/
│   │   ├── ui/
│   │   ├── analysis/
│   │   └── layout/
│   ├── pages/
│   │   ├── Landing.tsx
│   │   ├── Testing.tsx
│   │   └── Results.tsx
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   ├── api.ts
│   │   └── window.d.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

## ⚙️ Configuration Files Summary

### Core Files:
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite build configuration
- `tailwind.config.js` - Tailwind CSS configuration
- `postcss.config.js` - PostCSS configuration

### React App Files:
- `index.html` - HTML template with loading screen
- `src/main.tsx` - React entry point
- `src/App.tsx` - Main app component with routing
- `src/index.css` - Global styles with Tailwind

### Page Components:
- `src/pages/Landing.tsx` - Home page with URL input
- `src/pages/Testing.tsx` - Analysis progress page
- `src/pages/Results.tsx` - Results display page

### Services & Types:
- `src/services/api.ts` - API client for backend communication
- `src/types/api.ts` - TypeScript interfaces
- `src/types/window.d.ts` - Window type extensions

## 🎯 Expected Behavior

After setup, you should see:

1. **Landing Page** (`/`) - URL input form with gradient background
2. **Testing Page** (`/testing/:sessionId`) - Real-time progress updates
3. **Results Page** (`/results/:sessionId`) - Analysis results with tabs

## 🔍 Troubleshooting

### Common Issues:

**1. "Module not found" errors**
```bash
rm -rf node_modules package-lock.json
npm install
```

**2. TypeScript errors**
```bash
npm run dev
# Ignore minor TypeScript warnings during development
```

**3. Blank screen after loading**
- Check browser console for errors
- Ensure backend is running on port 8000
- Try hard refresh (Ctrl+Shift+R)

**4. API connection issues**
- Verify backend is accessible at `http://localhost:8000`
- Check browser network tab for failed requests
- Ensure CORS is enabled on backend

**5. Tailwind styles not loading**
```bash
npm install -D tailwindcss@latest autoprefixer@latest postcss@latest
npm run dev
```

### Browser Console Should Show:
- ✅ No red errors
- ✅ Successful font loading
- ✅ Clean React component mounting
- ✅ Successful API connections (when testing)

## 🚀 Running the Complete Application

1. **Start Backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend** (in new terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 🧪 Testing the Setup

1. Open http://localhost:3000
2. Enter a URL (e.g., "github.com")
3. Click "Analyze Website"
4. Should redirect to testing page with progress
5. Should eventually show results page

## 🎨 Key Features

- **Responsive Design** - Works on all device sizes
- **Real-time Updates** - Progress tracking via polling
- **Modern UI** - Tailwind CSS with glassmorphism effects
- **Smooth Animations** - Framer Motion transitions
- **Error Handling** - Graceful error boundaries
- **TypeScript** - Full type safety

## 📞 Support

If you encounter issues:
1. Check the browser console for errors
2. Verify all files are created correctly
3. Ensure backend is running and accessible
4. Try the automated setup script
5. Clear browser cache and try incognito mode

The frontend should now be fully functional and ready to analyze websites! 🎉