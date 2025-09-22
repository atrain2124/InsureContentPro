#!/bin/bash

echo "========================================"
echo "InsureContent Pro - Local Setup (Mac/Linux)"
echo "========================================"
echo

echo "[1/4] Setting up Backend..."
cd insurance_content_api
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors
echo "Backend setup complete!"
echo

echo "[2/4] Setting up Frontend..."
cd ../insurance-content-frontend
npm install -g pnpm
pnpm install
echo "Frontend setup complete!"
echo

echo "[3/4] Creating start scripts..."
cd ..

# Create backend start script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "Starting InsureContent Pro Backend..."
cd insurance_content_api/src
source ../venv/bin/activate
python main_local.py
EOF
chmod +x start_backend.sh

# Create frontend start script
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "Starting InsureContent Pro Frontend..."
cd insurance-content-frontend
pnpm run dev
EOF
chmod +x start_frontend.sh

# Create combined start script
cat > start_both.sh << 'EOF'
#!/bin/bash
echo "Starting InsureContent Pro..."
echo "Starting backend server..."
./start_backend.sh &
BACKEND_PID=$!

echo "Waiting 3 seconds for backend to start..."
sleep 3

echo "Starting frontend server..."
./start_frontend.sh &
FRONTEND_PID=$!

echo
echo "========================================"
echo "InsureContent Pro is starting..."
echo "========================================"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:5173"
echo
echo "Open http://localhost:5173 in your browser"
echo
echo "Press Ctrl+C to stop both servers"
echo "========================================"

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
chmod +x start_both.sh

echo "[4/4] Setup Complete!"
echo
echo "========================================"
echo "SETUP SUCCESSFUL!"
echo "========================================"
echo
echo "To start the application:"
echo "1. Run: ./start_both.sh"
echo "2. Wait for both servers to start"
echo "3. Open http://localhost:5173 in your browser"
echo
echo "Or start manually:"
echo "- Backend: ./start_backend.sh"
echo "- Frontend: ./start_frontend.sh"
echo
echo "========================================"
