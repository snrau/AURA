@echo off
call venv\Scripts\activate.bat
cd src\backend\
python -m uvicorn app:app --reload --port 8000