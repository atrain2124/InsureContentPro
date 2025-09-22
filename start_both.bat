@echo off 
echo Starting InsureContent Pro... 
start "Backend" start_backend.bat 
timeout /t 3 
start "Frontend" start_frontend.bat 
echo. 
echo Both servers are starting... 
echo Backend: http://localhost:5000 
echo Frontend: http://localhost:5173 
echo. 
echo Open http://localhost:5173 in your browser 
pause 
