@echo off
echo Installing dependencies if missing...
py -m pip install -r "Intel Ai Proj/requirements.txt"

echo.
echo Starting the Enterprise PDF Knowledge Base...
cd "Intel Ai Proj"
py -m streamlit run app.py
pause
