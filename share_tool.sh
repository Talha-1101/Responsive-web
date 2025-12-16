#!/bin/bash

# Kill any existing processes on ports 3000/8000 to be clean
echo "🧹 Cleaning up ports..."
pkill ngrok
lsof -ti :3000 | xargs kill -9 2>/dev/null
lsof -ti :8000 | xargs kill -9 2>/dev/null

echo "🚀 Starting Responsive Website Tester (Sharing Mode)..."

# 1. Start Backend in background
echo "backend: Starting FastAPI..."
cd backend
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# 2. Start Frontend in background
echo "frontend: Starting Vite..."
cd frontend
# We use standard npm run dev. The proxy in vite.config.ts handles the /api routing.
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "⏳ Waiting for services to initialize..."
sleep 5

# 3. Start Ngrok for Frontend (Port 3000)
echo "🌍 Starting Ngrok Tunnel for Port 3000..."
# Uses the user's ngrok auth token if configured
ngrok http 3000 --log=stdout > ngrok.log &
NGROK_PID=$!

echo "⏳ Waiting for Ngrok URL..."
sleep 5

# Extract Ngrok URL
NGROK_URL=$(grep -o 'https://[^"]*\.ngrok-free\.[a-z]*' ngrok.log | head -n 1)

if [ -z "$NGROK_URL" ]; then
    echo "⚠️  Could not grab Ngrok URL automatically from logs."
    echo "👉 Please check the 'ngrok.log' file or run 'ngrok http 3000' manually."
else
    echo ""
    echo "✅ SHARE THIS LINK WITH YOUR OFFICE:"
    echo "===================================================="
    echo "   $NGROK_URL"
    echo "===================================================="
    echo ""
fi

echo "Press CTRL+C to stop sharing."
wait
