# Script para limpar ambiente Docker no Windows PowerShell

Write-Host "🧹 Limpando ambiente Docker..." -ForegroundColor Green

Write-Host "📦 Parando todos os serviços..." -ForegroundColor Yellow
docker-compose down

Write-Host "🗑️ Removendo containers..." -ForegroundColor Yellow
docker-compose rm -f

Write-Host "🗑️ Removendo volumes..." -ForegroundColor Yellow
docker-compose down -v --remove-orphans

Write-Host "🗑️ Removendo imagens..." -ForegroundColor Yellow
docker-compose down --rmi all

Write-Host "🧹 Limpeza concluída!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Para recomeçar, execute:" -ForegroundColor Cyan
Write-Host "   docker-compose up --build" -ForegroundColor White 