#!/bin/bash

echo "🔧 Reconstruindo container FastAPI com novas dependências..."

# Para os containers
echo "🛑 Parando containers..."
docker-compose down

# Remove containers antigos
echo "🗑️  Removendo containers antigos..."
docker-compose rm -f

# Remove imagens antigas
echo "🗑️  Removendo imagens antigas..."
docker-compose down --rmi all

# Reconstrói sem cache
echo "🔨 Reconstruindo sem cache..."
docker-compose build --no-cache

# Inicia os serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Mostra logs
echo "📋 Logs da aplicação:"
docker-compose logs -f api 