@echo off
REM Script helper pour Docker Compose en mode dev

docker-compose -f docker-compose.dev.yml %*
