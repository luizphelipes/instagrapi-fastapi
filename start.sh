#!/bin/bash

# Script de inicialização para EasyPanel com otimizações de performance
echo "🚀 Iniciando Instagram API FastAPI..."
echo "🔧 Versão: 2.0.0"
echo "📅 $(date)"
echo "🖥️ CPU: $(nproc) cores"
echo "💾 RAM: $(free -h | awk '/^Mem:/{print $2}')"
echo "=" * 50

# Verifica se estamos no container
if [ -d "/app" ]; then
    echo "✅ Executando no container Docker"
    cd /app
else
    echo "⚠️ Executando fora do container"
fi

# Otimizações do sistema
echo "🔧 Aplicando otimizações de sistema..."

# Ajusta limites do sistema para melhor performance
ulimit -n 65536 2>/dev/null || echo "⚠️ Não foi possível ajustar limite de arquivos"

# Executa a inicialização do banco de dados
echo "🔧 Inicializando banco de dados..."
python init_db.py
DB_INIT_RESULT=$?

# Verifica se a inicialização foi bem-sucedida
if [ $DB_INIT_RESULT -eq 0 ]; then
    echo "✅ Banco de dados inicializado com sucesso!"
else
    echo "❌ Falha na inicialização do banco de dados!"
    echo "⚠️ Código de saída: $DB_INIT_RESULT"
fi

# Pré-aquecimento do serviço (opcional)
echo "🔥 Iniciando pré-aquecimento do serviço..."
python prewarm_service.py &
PREWARM_PID=$!

# Aguarda um pouco para o pré-aquecimento
sleep 5

echo "🚀 Iniciando aplicação com otimizações..."
echo "🔧 Configurações otimizadas:"
echo "   - Host: 0.0.0.0"
echo "   - Porta: 8000"
echo "   - Workers: 4"
echo "   - Log level: info"
echo "   - Preload: enabled"
echo "   - Keep-alive: enabled"
echo "   - Pre-warming: enabled"

# Inicia a aplicação com otimizações
exec uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --access-log \
    --use-colors \
    --timeout-keep-alive 30 \
    --limit-concurrency 1000 \
    --limit-max-requests 10000 