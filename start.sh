#!/bin/bash

# Script de inicialização para EasyPanel
echo "🚀 Iniciando Instagram API FastAPI..."
echo "🔧 Versão: 2.0.0"
echo "📅 $(date)"
echo "=" * 50

# Verifica se estamos no container
if [ -d "/app" ]; then
    echo "✅ Executando no container Docker"
    cd /app
else
    echo "⚠️ Executando fora do container"
fi

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

echo "🚀 Iniciando aplicação..."
echo "🔧 Configurações:"
echo "   - Host: 0.0.0.0"
echo "   - Porta: 8000"
echo "   - Workers: 4"
echo "   - Log level: info"

# Inicia a aplicação
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info 