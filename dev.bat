@echo off
echo Starting backend and frontend...
start "Backend Django" cmd /k "cd backend && python manage.py runserver"
start "Frontend Nuxt" cmd /k "cd frontend && npm run dev"
echo Both servers started in separate windows.
