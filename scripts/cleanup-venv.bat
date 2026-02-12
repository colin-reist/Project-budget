@echo off
REM ============================================
REM Script de Nettoyage des Environnements Virtuels Python (Windows)
REM ============================================
REM Ce script supprime les environnements virtuels Python
REM qui ne devraient pas être dans le repository Git
REM
REM Usage: scripts\cleanup-venv.bat

setlocal enabledelayedexpansion

echo ============================================
echo Nettoyage des environnements virtuels Python
echo ============================================
echo.

REM Vérifier si on est à la racine du projet
if not exist "docker-compose.yml" (
    echo [ERROR] Ce script doit etre execute depuis la racine du projet!
    exit /b 1
)

REM Compter les environnements trouvés
set FOUND=0

echo Environnements virtuels trouves:

if exist "myvenv\" (
    echo   - myvenv\ (racine)
    set /a FOUND+=1
)

if exist "backend\myvenv\" (
    echo   - backend\myvenv\
    set /a FOUND+=1
)

if exist "venv\" (
    echo   - venv\ (racine)
    set /a FOUND+=1
)

if exist "backend\venv\" (
    echo   - backend\venv\
    set /a FOUND+=1
)

echo.

if %FOUND%==0 (
    echo [INFO] Aucun environnement virtuel trouve. Projet deja propre!
    exit /b 0
)

echo [WARN] %FOUND% environnement^(s^) virtuel^(s^) trouve^(s^)
echo.

REM Demander confirmation
set /p CONFIRM="Voulez-vous supprimer ces environnements virtuels? (O/N): "

if /i not "%CONFIRM%"=="O" (
    if /i not "%CONFIRM%"=="Y" (
        echo [INFO] Operation annulee.
        exit /b 0
    )
)

echo.
echo [INFO] Suppression en cours...
echo.

REM Supprimer les environnements
if exist "myvenv\" (
    echo [INFO] Suppression de myvenv...
    rmdir /s /q "myvenv" 2>nul
    if !errorlevel! equ 0 (
        echo   OK Supprime avec succes
    ) else (
        echo   X Erreur lors de la suppression
    )
)

if exist "backend\myvenv\" (
    echo [INFO] Suppression de backend\myvenv...
    rmdir /s /q "backend\myvenv" 2>nul
    if !errorlevel! equ 0 (
        echo   OK Supprime avec succes
    ) else (
        echo   X Erreur lors de la suppression
    )
)

if exist "venv\" (
    echo [INFO] Suppression de venv...
    rmdir /s /q "venv" 2>nul
    if !errorlevel! equ 0 (
        echo   OK Supprime avec succes
    ) else (
        echo   X Erreur lors de la suppression
    )
)

if exist "backend\venv\" (
    echo [INFO] Suppression de backend\venv...
    rmdir /s /q "backend\venv" 2>nul
    if !errorlevel! equ 0 (
        echo   OK Supprime avec succes
    ) else (
        echo   X Erreur lors de la suppression
    )
)

echo.
echo [INFO] Nettoyage termine!
echo.
echo Note: Les environnements virtuels sont maintenant dans .gitignore
echo       Utilisez Docker pour le developpement ou creez un nouvel environnement
echo       virtuel avec: cd backend ^&^& python -m venv venv
echo.

endlocal
