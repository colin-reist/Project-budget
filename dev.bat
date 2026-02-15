@echo off
REM Script helper pour Docker Compose en mode dev

REM Si aucun argument, lancer "up" par défaut
if "%1"=="" (
    echo Lancement de l'environnement de developpement...
    docker compose -f docker-compose.dev.yml up
) else (
    docker compose -f docker-compose.dev.yml %*
)
