@echo off 
echo Starting InsureContent Pro Backend... 
cd insurance_content_api\src 
call ..\venv\Scripts\activate 
python main_local.py 
pause 
