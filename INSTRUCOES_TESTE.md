# 🧪 Instruções para Testar a API FastAPI

## ✅ Status da Implementação

Todos os arquivos foram criados e corrigidos com sucesso:
- ✅ `main.py` - Aplicação principal FastAPI
- ✅ `database.py` - Configuração do banco async
- ✅ `schemas.py` - Schemas Pydantic
- ✅ `routes/instagram.py` - Rotas da API
- ✅ `services/instagram_service.py` - Serviço Instagram async
- ✅ `services/redis_cache.py` - Cache Redis async
- ✅ `requirements.txt` - Dependências Python
- ✅ `Dockerfile` - Containerização
- ✅ `docker-compose.yml` - Orquestração de serviços
- ✅ `Makefile` - Comandos úteis
- ✅ `start_dev.py` - Script de desenvolvimento
- ✅ `clean-docker.sh` - Script de limpeza Docker (Linux/Mac)
- ✅ `clean-docker.ps1` - Script de limpeza Docker (Windows)

## 🚀 Como Testar

### **1. Configuração Inicial**

```bash
cd fastapi-instagram-api

# Copie o arquivo de exemplo
cp env.example .env

# Edite o .env com suas configurações
# IMPORTANTE: Gere uma chave de criptografia válida
```

### **2. Gere Chave de Criptografia**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copie a chave gerada para ENCRYPTION_KEY no .env
```

### **3. Teste com Docker (Recomendado)**

```bash
# Constrói e inicia os serviços
docker-compose up --build

# Em outro terminal, verifique os logs
docker-compose logs -f api
```

### **4. Teste Localmente**

```bash
# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
export $(cat .env | xargs)

# Execute a aplicação
python start_dev.py
```

### **5. Verifique se está Funcionando**

```bash
# Health check
curl http://localhost:8000/

# Documentação Swagger
curl http://localhost:8000/docs

# Documentação ReDoc
curl http://localhost:8000/redoc
```

## 🔧 Comandos Úteis

### **Com Makefile**
```bash
make help          # Mostra comandos disponíveis
make setup-dev     # Configura ambiente
make dev           # Inicia desenvolvimento
make docker-up     # Inicia Docker
make docker-logs   # Mostra logs
make docker-clean  # Remove containers e volumes
make docker-clean-all  # Limpa completamente
make docker-fresh  # Limpa tudo e reconstrói
make reset-docker  # Reseta ambiente Docker
```

### **Com Docker Compose**
```bash
docker-compose up --build    # Constrói e inicia
docker-compose down          # Para serviços
docker-compose logs -f       # Mostra logs
docker-compose restart       # Reinicia serviços
docker-compose down -v       # Remove volumes
```

### **Scripts de Limpeza**
```bash
# Linux/Mac
./clean-docker.sh

# Windows PowerShell
.\clean-docker.ps1
```

## 📋 Endpoints para Testar

### **Endpoints Básicos**
- `GET /` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

### **Endpoints do Instagram**
- `GET /api/v1/accounts` - Lista contas
- `POST /api/v1/auth/login-by-session` - Login
- `GET /api/v1/users/{username}` - Perfil
- `GET /api/v1/users/{username}/stories` - Stories
- `GET /api/v1/users/{username}/posts` - Posts
- `GET /api/v1/users/{username}/reels` - Reels
- `GET /api/v1/users/{username}/privacy` - Privacidade
- `GET /api/v1/proxy-image` - Proxy de imagens

### **Endpoints de Cache**
- `GET /api/v1/cache/stats` - Estatísticas do cache
- `DELETE /api/v1/cache/clear` - Limpa cache

## 🐛 Troubleshooting

### **Erro de Importação**
Se houver erro de importação, verifique:
- Todos os arquivos `__init__.py` estão presentes
- Caminhos de importação estão corretos
- Dependências instaladas

### **Erro de Conexão**
Se houver erro de conexão:
- Redis está rodando? `docker-compose ps redis`
- PostgreSQL está rodando? `docker-compose ps postgres`
- Variáveis de ambiente configuradas?

### **Erro de Criptografia**
Se houver erro de criptografia:
- `ENCRYPTION_KEY` está definida no `.env`?
- A chave é válida? Gere uma nova se necessário

### **Erro de Banco de Dados (NOVO!)**
Se houver erro de banco de dados:
- **Problema**: Conflito de tabelas já existentes
- **Solução 1**: Limpe completamente o ambiente:
  ```bash
  make docker-clean-all
  docker-compose up --build
  ```
- **Solução 2**: Use o script de limpeza:
  ```bash
  # Linux/Mac
  ./clean-docker.sh
  
  # Windows
  .\clean-docker.ps1
  ```
- **Solução 3**: O código agora verifica automaticamente se as tabelas existem

## 📊 Monitoramento

### **Logs da Aplicação**
```bash
docker-compose logs -f api
```

### **Logs do Redis**
```bash
docker-compose logs -f redis
```

### **Logs do PostgreSQL**
```bash
docker-compose logs -f postgres
```

### **Estatísticas do Cache**
```bash
curl http://localhost:8000/api/v1/cache/stats
```

## 🔄 Resolução de Problemas Comuns

### **1. Conflito de Tabelas no PostgreSQL**
**Sintoma**: `duplicate key value violates unique constraint`
**Solução**: 
```bash
make docker-clean-all
docker-compose up --build
```

### **2. Aplicação não Inicia**
**Sintoma**: `Application startup failed`
**Solução**:
```bash
# Verifique logs
docker-compose logs api

# Limpe e reinicie
make docker-fresh
```

### **3. Erro de Conexão com Banco**
**Sintoma**: `connection refused`
**Solução**:
```bash
# Aguarde o PostgreSQL inicializar
docker-compose logs postgres

# Verifique health check
docker-compose ps postgres
```

## 🎯 Próximos Passos

1. **Teste a aplicação** com os comandos acima
2. **Configure contas Instagram** no arquivo `.env`
3. **Teste os endpoints** usando Swagger UI
4. **Monitore performance** e logs
5. **Implemente melhorias** conforme necessário

## 🔗 Links Úteis

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/
- **Cache Stats**: http://localhost:8000/api/v1/cache/stats

## 🆕 Novidades na Versão Atualizada

- ✅ **Verificação automática de tabelas** - Evita conflitos de banco
- ✅ **Health checks melhorados** - PostgreSQL aguarda inicialização
- ✅ **Scripts de limpeza** - Para Linux/Mac e Windows
- ✅ **Comandos Makefile** - Limpeza e reset do ambiente
- ✅ **Tratamento de erros** - Continua inicialização mesmo com problemas de banco

---

**🎉 Sua API FastAPI está pronta para testes e agora é mais robusta!** 