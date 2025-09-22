@echo off
echo ========================================
echo InsureContent Pro - Local Setup (Windows)
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd insurance_content_api
python -m venv venv
call venv\Scripts\activate
pip install flask flask-cors
echo Backend setup complete!
echo.

echo [2/4] Setting up Frontend...
cd ..\insurance-content-frontend
call npm install -g pnpm
call pnpm install
echo Frontend setup complete!
echo.

echo [3/4] Creating start scripts...
cd ..
echo @echo off > start_backend.bat
echo echo Starting InsureContent Pro Backend... >> start_backend.bat
echo cd insurance_content_api\src >> start_backend.bat
echo call ..\venv\Scripts\activate >> start_backend.bat
echo python main_local.py >> start_backend.bat
echo pause >> start_backend.bat

echo @echo off > start_frontend.bat
echo echo Starting InsureContent Pro Frontend... >> start_frontend.bat
echo cd insurance-content-frontend >> start_frontend.bat
echo call pnpm run dev >> start_frontend.bat
echo pause >> start_frontend.bat

echo @echo off > start_both.bat
echo echo Starting InsureContent Pro... >> start_both.bat
echo start "Backend" start_backend.bat >> start_both.bat
echo timeout /t 3 >> start_both.bat
echo start "Frontend" start_frontend.bat >> start_both.bat
echo echo. >> start_both.bat
echo echo Both servers are starting... >> start_both.bat
echo echo Backend: http://localhost:5000 >> start_both.bat
echo echo Frontend: http://localhost:5173 >> start_both.bat
echo echo. >> start_both.bat
echo echo Open http://localhost:5173 in your browser >> start_both.bat
echo pause >> start_both.bat

echo [4/4] Setup Complete!
echo.
echo ========================================
echo SETUP SUCCESSFUL!
echo ========================================
echo.
echo To start the application:
echo 1. Double-click 'start_both.bat'
echo 2. Wait for both servers to start
echo 3. Open http://localhost:5173 in your browser
echo.
echo Or start manually:
echo - Backend: Double-click 'start_backend.bat'
echo - Frontend: Double-click 'start_frontend.bat'
echo.
echo ========================================
pause
