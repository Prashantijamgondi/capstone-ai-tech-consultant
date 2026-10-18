@echo off
echo Starting AI Tech Consultant Monorepo Services...

start "Task 1: Knowledge Brain (8001)" cmd /k "cd task1-knowledge-brain && python -m uvicorn app.main:app --port 8001"
timeout /t 2 >nul

start "Task 2: Inbox Agent (8002)" cmd /k "cd task2-inbox-agent && npm start"
timeout /t 2 >nul

start "Task 3: Meeting to Scope (8003)" cmd /k "cd task3-meeting-to-scope && python -m uvicorn app.main:app --port 8003"
timeout /t 2 >nul

start "Unified UI (3000)" cmd /k "cd ui && python -m http.server 3000"

echo All services launched!
echo - Knowledge Brain API: http://127.0.0.1:8001/docs
echo - Inbox Agent API:    http://127.0.0.1:8002
echo - Meeting to SOW API: http://127.0.0.1:8003/docs
echo - Unified Control UI: http://127.0.0.1:3000
pause
