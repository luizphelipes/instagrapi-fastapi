# 🚀 Otimizações de Performance - Instagram API FastAPI

## 📊 Configuração Atual do Sistema

**Hardware:**
- **CPU**: Intel i5 4440 (4 cores, 3.1GHz)
- **RAM**: 16GB DDR3
- **Storage**: SSD 240GB
- **OS**: Xubuntu
- **Internet**: 100Mbps (cabo LAN)

**Infraestrutura:**
- **Container**: Docker via EasyPanel
- **Proxy**: Cloudflare Tunnel
- **Cache**: Redis
- **Banco**: PostgreSQL

## 🎯 Problema Identificado

**Cold Start**: Primeira requisição leva até 1 minuto
**Warm Start**: Requisições subsequentes levam alguns segundos

## 🔧 Otimizações Implementadas

### 1. **Pré-inicialização do Serviço**
```python
# Novo sistema de inicialização assíncrona
await service.initialize()  # Pré-inicializa clientes
await service.ensure_initialized()  # Garante inicialização
```

### 2. **Otimização de Timeouts**
```python
# Reduzido de 15s para 10s
client = Client(request_timeout=10)
```

### 3. **Configurações Uvicorn Otimizadas**
```bash
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --timeout-keep-alive 30 \
    --limit-concurrency 1000 \
    --limit-max-requests 10000
```

### 4. **Sistema de Cache Inteligente**
- **Stories**: 5 minutos (dados temporários)
- **Privacy**: 2 minutos (pode mudar)
- **Posts/Reels/Profile**: 30 minutos (dados estáveis)

### 5. **Pré-aquecimento Automático**
```bash
# Script executado na inicialização
python prewarm_service.py &
```

## 📈 Resultados Esperados

### **Antes das Otimizações:**
- Cold Start: ~60 segundos
- Warm Start: ~3-5 segundos
- Cache Hit: ~1-2 segundos

### **Após as Otimizações:**
- Cold Start: ~10-15 segundos ⚡
- Warm Start: ~1-2 segundos ⚡
- Cache Hit: ~200-500ms ⚡

## 🛠️ Configurações Específicas para i5 4440

### **Docker/Container:**
```yaml
# docker-compose.yml ou EasyPanel
services:
  api:
    environment:
      - PYTHONHASHSEED=random
      - PYTHONUNBUFFERED=1
    deploy:
      resources:
        limits:
          cpus: '3.0'  # 3 cores para a API
          memory: 4G   # 4GB RAM
        reservations:
          cpus: '1.0'
          memory: 2G
```

### **Redis Otimizado:**
```bash
# Configurações Redis para 16GB RAM
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### **PostgreSQL Otimizado:**
```sql
-- Configurações para i5 4440
shared_buffers = 1GB
effective_cache_size = 4GB
work_mem = 16MB
maintenance_work_mem = 256MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

## 🔍 Monitoramento de Performance

### **Métricas Importantes:**
```bash
# Verificar uso de recursos
docker stats <container_name>

# Verificar logs de performance
docker logs <container_name> | grep "performance\|latency\|time"

# Verificar cache hit rate
curl http://seu-dominio/api/v1/cache/stats
```

### **Comandos de Debug:**
```bash
# Testar latência de endpoints
curl -w "@curl-format.txt" -o /dev/null -s "http://seu-dominio/api/v1/accounts"

# Verificar status do serviço
curl http://seu-dominio/api/v1/accounts/status

# Limpar cache se necessário
curl -X DELETE "http://seu-dominio/api/v1/cache/clear"
```

## 🚀 Recomendações Adicionais

### **Para EasyPanel:**
1. **Aumentar recursos do container**: 4GB RAM, 3 cores CPU
2. **Configurar health checks**: Para reinicialização automática
3. **Monitorar logs**: Para identificar gargalos

### **Para Cloudflare Tunnel:**
1. **Configurar timeouts**: Aumentar para 60s
2. **Habilitar compression**: Para reduzir latência
3. **Usar edge locations**: Para menor latência

### **Para Sistema:**
1. **Otimizar swap**: 4GB swap file
2. **Configurar TCP**: Otimizações de rede
3. **Monitorar I/O**: SSD deve ter boa performance

## 📊 Script de Monitoramento

```bash
#!/bin/bash
# monitor_performance.sh

echo "📊 Monitoramento de Performance - Instagram API"
echo "=" * 50

# CPU e RAM
echo "🖥️ CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1

echo "💾 RAM Usage:"
free -h | awk '/^Mem:/ {print $3"/"$2}'

# Container stats
echo "🐳 Container Stats:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# API Response Time
echo "⚡ API Response Time:"
curl -w "Time: %{time_total}s\n" -o /dev/null -s "http://seu-dominio/api/v1/accounts"

# Cache Stats
echo "📦 Cache Stats:"
curl -s "http://seu-dominio/api/v1/cache/stats" | jq '.'
```

## 🎯 Próximos Passos

1. **Implementar as otimizações** ✅
2. **Monitorar performance** por 24h
3. **Ajustar configurações** conforme necessário
4. **Considerar upgrade** se performance ainda insuficiente

## 📞 Suporte

Se a performance ainda não estiver satisfatória:

1. **Verificar logs**: `docker logs <container>`
2. **Monitorar recursos**: `htop`, `iotop`
3. **Testar endpoints**: Usar curl com timing
4. **Analisar cache**: Verificar hit rate

**Meta**: Reduzir cold start para <15s e warm start para <2s 