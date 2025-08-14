#!/bin/bash

echo "🧹 Limpando ambiente Docker..."

echo "📦 Parando todos os serviços..."
docker-compose down

echo "🗑️ Removendo containers..."
docker-compose rm -f

echo "🗑️ Removendo volumes..."
docker-compose down -v --remove-orphans

echo "🗑️ Removendo imagens..."
docker-compose down --rmi all

echo "🧹 Limpeza concluída!"
echo ""
echo "🚀 Para recomeçar, execute:"
echo "   docker-compose up --build" 