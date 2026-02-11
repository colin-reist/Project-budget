@echo off
REM ============================================
REM Script de déploiement Docker (Windows)
REM Mise à jour sans perte de données
REM ============================================

setlocal enabledelayedexpansion

REM Vérifier les prérequis
if not exist ".env" (
    echo ❌ .env n'existe pas
    echo Créer .env depuis .env.example ou .env.docker
    exit /b 1
)

REM Variables
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set TIMESTAMP=%%a
set TIMESTAMP=%TIMESTAMP:~0,8%_%TIMESTAMP:~8,6%

REM Menu
cls
echo.
echo ========================================
echo 🐳 Budget Tracker - Deployment Script
echo ========================================
echo.
echo Commandes disponibles:
echo   1 - Déploiement complet (Frontend + Backend)
echo   2 - Mise à jour Frontend uniquement
echo   3 - Mise à jour Backend uniquement
echo   4 - Sauvegarde base de données
echo   5 - État de l'application
echo   6 - Voir les logs
echo   7 - Démarrer les conteneurs
echo   8 - Arrêter les conteneurs
echo   0 - Quitter
echo.
set /p choice="Choisissez une option (0-8): "

if "%choice%"=="1" goto deploy_all
if "%choice%"=="2" goto deploy_frontend
if "%choice%"=="3" goto deploy_backend
if "%choice%"=="4" goto backup_db
if "%choice%"=="5" goto check_status
if "%choice%"=="6" goto show_logs
if "%choice%"=="7" goto start_containers
if "%choice%"=="8" goto stop_containers
if "%choice%"=="0" goto end
echo Option invalide
goto end

:deploy_all
cls
echo.
echo ========================================
echo Déploiement Complet
echo ========================================
echo.
echo 1. Récupération des modifications...
git pull origin main
if errorlevel 1 (
    echo ❌ Erreur lors du git pull
    goto end
)
echo ✓ Modifications récupérées

echo.
echo 2. Construction des images...
docker-compose build
if errorlevel 1 (
    echo ❌ Erreur lors de la construction
    goto end
)
echo ✓ Images construites

echo.
echo 3. Redémarrage des services...
docker-compose up -d
echo ✓ Services redémarrés

echo.
echo 4. Vérification du statut...
timeout /t 5 /nobreak
docker-compose ps
echo.
echo ✓ Déploiement complet terminé!
goto end

:deploy_frontend
cls
echo.
echo ========================================
echo Mise à Jour Frontend
echo ========================================
echo.
git pull origin main
docker-compose build frontend
docker-compose up -d frontend
echo.
timeout /t 3 /nobreak
docker-compose ps frontend
echo ✓ Frontend mis à jour!
goto end

:deploy_backend
cls
echo.
echo ========================================
echo Mise à Jour Backend
echo ========================================
echo.
git pull origin main
docker-compose build backend
docker-compose up -d backend
echo.
timeout /t 5 /nobreak
docker-compose logs --tail 20 backend
echo ✓ Backend mis à jour!
goto end

:backup_db
cls
echo.
echo ========================================
echo Sauvegarde Base de Données
echo ========================================
echo.
if not exist "backups" mkdir backups

echo Création de la sauvegarde: backups/backup_%TIMESTAMP%.sql
docker-compose exec -T database pg_dump -U budget_user budget_db > backups/backup_%TIMESTAMP%.sql

if errorlevel 1 (
    echo ❌ Erreur lors de la sauvegarde
    goto end
)

echo ✓ Sauvegarde créée: backups/backup_%TIMESTAMP%.sql
dir /s backups\backup_%TIMESTAMP%.sql
goto end

:check_status
cls
echo.
echo ========================================
echo État de l'Application
echo ========================================
echo.
docker-compose ps
echo.
echo Utilisation des ressources:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
goto end

:show_logs
cls
echo.
echo ========================================
echo Logs
echo ========================================
echo.
echo 1 - Backend
echo 2 - Frontend
echo 3 - Database
echo 4 - Tout
echo.
set /p log_choice="Choisissez le service (1-4): "

if "%log_choice%"=="1" docker-compose logs -f backend
if "%log_choice%"=="2" docker-compose logs -f frontend
if "%log_choice%"=="3" docker-compose logs -f database
if "%log_choice%"=="4" docker-compose logs -f
goto end

:start_containers
cls
echo.
echo ========================================
echo Démarrage des conteneurs
echo ========================================
echo.
docker-compose up -d
timeout /t 5 /nobreak
docker-compose ps
echo ✓ Conteneurs démarrés!
goto end

:stop_containers
cls
echo.
echo ========================================
echo Arrêt des conteneurs
echo ========================================
echo.
docker-compose down
echo ✓ Conteneurs arrêtés (données conservées)
goto end

:end
echo.
pause
