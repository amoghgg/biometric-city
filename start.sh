#!/bin/bash
# Start Biometric City — backend + frontend dev servers

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting Biometric City..."

# Backend
cd "$SCRIPT_DIR/backend"
venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "Backend started (PID $BACKEND_PID) → http://localhost:8000"

# Wait for backend
sleep 2

# Frontend
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend started (PID $FRONTEND_PID) → http://localhost:5173"

echo ""
echo "  BIOMETRIC CITY running at http://localhost:5173"
echo "  Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
