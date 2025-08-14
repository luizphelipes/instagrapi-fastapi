@echo off
echo 🔧 Reconstruindo container FastAPI com novas dependências...

REM Para os containers
echo 🛑 Parando containers...
docker-compose down

REM Remove containers antigos
echo 🗑️  Removendo containers antigos...
docker-compose rm -f

REM Remove imagens antigas
echo 🗑️  Removendo imagens antigas...
docker-compose down --rmi all

REM Reconstrói sem cache
echo 🔨 Reconstruindo sem cache...
docker-compose build --no-cache

REM Inicia os serviços
echo 🚀 Iniciando serviços...
docker-compose up -d

REM Mostra logs
echo 📋 Logs da aplicação:
docker-compose logs -f api

pause 