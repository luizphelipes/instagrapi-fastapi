# Instagram API - FastAPI Version

Esta é uma versão da API Instagram usando **FastAPI** para alta disponibilidade e performance. A API atua como um wrapper para interagir com o Instagram, utilizando a biblioteca `instagrapi` para buscar dados de perfis, posts e reels.

## 🚀 Principais Melhorias com FastAPI

### **Performance e Escalabilidade**
- **Async/Await**: Operações assíncronas para melhor throughput
- **Uvicorn com Workers**: Suporte a múltiplos workers para alta concorrência
- **Connection Pooling**: Pool de conexões otimizado para banco de dados
- **Redis Async**: Cache Redis com operações assíncronas

### **Desenvolvimento e Manutenção**
- **Documentação Automática**: Swagger/OpenAPI integrado
- **Validação de Dados**: Schemas Pydantic para validação automática
- **Type Hints**: Tipagem estática para melhor qualidade do código
- **Hot Reload**: Recarregamento automático durante desenvolvimento

### **Monitoramento e Observabilidade**
- **Health Checks**: Endpoints de saúde da aplicação
- **Cache Stats**: Estatísticas do cache Redis
- **Error Handling**: Tratamento global de exceções
- **Logging Estruturado**: Logs organizados e informativos

## 🏗️ Arquitetura

```
fastapi-instagram-api/
├── main.py                 # Aplicação principal FastAPI
├── database.py            # Configuração do banco async
├── schemas.py             # Schemas Pydantic
├── routes/
│   └── instagram.py       # Rotas da API
├── services/
│   ├── instagram_service.py  # Serviço Instagram async
│   └── redis_cache.py        # Cache Redis async
├── requirements.txt        # Dependências Python
├── Dockerfile             # Containerização
├── docker-compose.yml     # Orquestração de serviços
└── README.md              # Esta documentação
```

## 📋 Funcionalidades

### **Endpoints da API**
- `GET /` - Health check da aplicação
- `GET /docs` - Documentação Swagger automática
- `GET /redoc` - Documentação ReDoc alternativa

### **Endpoints do Instagram**
- `GET /api/v1/accounts` - Lista contas configuradas
- `DELETE /api/v1/accounts/{username}` - Remove conta
- `POST /api/v1/auth/login-by-session` - Login com session_id
- `GET /api/v1/users/{username}` - Informações do perfil
- `GET /api/v1/users/{username}/stories` - Stories do usuário
- `GET /api/v1/users/{username}/posts` - Posts do usuário
- `GET /api/v1/users/{username}/reels` - Reels do usuário
- `GET /api/v1/users/{username}/privacy` - Verificação de privacidade
- `GET /api/v1/proxy-image` - Proxy para imagens (solução CORS)

### **Endpoints de Cache**
- `GET /api/v1/cache/stats` - Estatísticas do cache Redis
- `DELETE /api/v1/cache/clear` - Limpa cache por padrão

## 🛠️ Instalação e Configuração

### **Pré-requisitos**
- Python 3.11+
- Docker e Docker Compose
- Redis
- PostgreSQL 15+

### **1. Clone e Configure**
```bash
cd fastapi-instagram-api
cp env.example .env
# Edite o arquivo .env com suas configurações
```

### **2. Gere Chave de Criptografia**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Copie a chave gerada para ENCRYPTION_KEY no .env
```

### **3. Execute com Docker**
```bash
docker-compose up --build
```

### **4. Execute Localmente**
```bash
# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
export $(cat .env | xargs)

# Execute a aplicação
python main.py
```

## 🔧 Configuração das Variáveis de Ambiente

### **Arquivo .env**
```env
# Banco de Dados
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/instagram_api"

# Criptografia
ENCRYPTION_KEY="sua_chave_gerada_aqui"

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Instagram
INSTAGRAM_SESSION_ID_1="session_id_conta_1"
INSTAGRAM_SESSION_ID_2="session_id_conta_2"

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
```

## 🚀 Execução em Produção

### **Com Uvicorn**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Com Gunicorn + Uvicorn**
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### **Com Docker**
```bash
docker-compose -f docker-compose.yml up -d
```

## 📊 Monitoramento

### **Health Check**
```bash
curl http://localhost:8000/
```

### **Documentação da API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### **Estatísticas do Cache**
```bash
curl http://localhost:8000/api/v1/cache/stats
```

## 🔒 Segurança

- **Criptografia**: Session IDs criptografados com Fernet
- **Validação**: Schemas Pydantic para validação de entrada
- **Sanitização**: Tratamento seguro de URLs e parâmetros
- **Rate Limiting**: Implementar conforme necessário

## 📈 Performance

### **Benchmarks Esperados**
- **Throughput**: 2-3x melhor que Flask síncrono
- **Latência**: Redução de 30-50% em operações I/O
- **Concorrência**: Suporte a 1000+ requests simultâneos
- **Cache Hit Rate**: 80-90% com Redis otimizado

### **Otimizações Implementadas**
- Connection pooling para banco de dados
- Cache Redis assíncrono
- Lazy loading de clientes Instagram
- Rotação de contas para distribuir carga

## 🐛 Troubleshooting

### **Problemas Comuns**

1. **Erro de Conexão com Redis**
   ```bash
   # Verifique se o Redis está rodando
   docker-compose ps redis
   ```

2. **Erro de Conexão com PostgreSQL**
   ```bash
   # Verifique logs do PostgreSQL
   docker-compose logs postgres
   ```

3. **Chave de Criptografia Inválida**
   ```bash
   # Gere nova chave
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🔗 Links Úteis

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Instagrapi Documentation](https://adw0rd.github.io/instagrapi/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Redis Python](https://redis-py.readthedocs.io/) 