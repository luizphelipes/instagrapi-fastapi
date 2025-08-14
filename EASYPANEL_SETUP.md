# Configuração EasyPanel - Instagram API FastAPI

## 📋 Pré-requisitos

1. **PostgreSQL** - Serviço de banco de dados configurado no EasyPanel
   - Nome do serviço: `servidor_fastapi-postgres`
   - Usuário: `postgres`
   - Senha: `d30bfb311dd156dad365`
   - Banco: `servidor`
   - Porta: `5432`

2. **Redis** - Serviço de cache configurado no EasyPanel
   - Nome do serviço: `servidor_fastapi-redis`
   - Porta: `6379`
   - Senha: `14c652679ebd921579d6`

## 🚀 Configuração no EasyPanel

### 1. Configurar o Serviço PostgreSQL

No EasyPanel, crie um serviço PostgreSQL com as seguintes configurações:

```json
{
  "type": "postgresql",
  "data": {
    "name": "servidor_fastapi-postgres",
    "image": "postgres:15-alpine",
    "env": "POSTGRES_DB=servidor\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=d30bfb311dd156dad365"
  }
}
```

### 2. Configurar o Serviço Redis

```json
{
  "type": "redis",
  "data": {
    "name": "servidor_fastapi-redis",
    "image": "redis:7-alpine",
    "env": "REDIS_PASSWORD=14c652679ebd921579d6"
  }
}
```

### 3. Configurar a Aplicação

```json
{
  "type": "app",
  "data": {
    "name": "instagram-api",
    "build": {
      "type": "dockerfile",
      "dockerfilePath": "./Dockerfile"
    },
    "env": "DATABASE_URL=postgresql://postgres:d30bfb311dd156dad365@servidor_fastapi-postgres:5432/servidor\nREDIS_HOST=servidor_fastapi-redis\nREDIS_PORT=6379\nREDIS_PASSWORD=14c652679ebd921579d6",
    "ports": [
      {
        "host": 80,
        "container": 8000
      }
    ]
  }
}
```

## 🔧 Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no EasyPanel:

```bash
# Banco de Dados
DATABASE_URL=postgresql://postgres:d30bfb311dd156dad365@servidor_fastapi-postgres:5432/servidor

# Redis
REDIS_HOST=servidor_fastapi-redis
REDIS_PORT=6379
REDIS_PASSWORD=14c652679ebd921579d6

# Chave de Criptografia (será gerada automaticamente se não fornecida)
ENCRYPTION_KEY=

# Instagram Session IDs (opcional)
INSTAGRAM_SESSION_ID_1=
INSTAGRAM_SESSION_ID_2=

# Configurações da API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO
```

## 📝 Ordem de Inicialização

1. **PostgreSQL** - Deve ser iniciado primeiro
2. **Redis** - Pode ser iniciado em paralelo
3. **Aplicação** - Será iniciada automaticamente após os serviços de banco

## 🔍 Verificação

Após a inicialização, verifique:

1. **Logs da aplicação** - Deve mostrar:
   ```
   ✅ Banco de dados disponível na tentativa X
   ✅ Tabelas criadas com sucesso!
   ✅ Tabela instagram_accounts confirmada!
   ```

2. **Endpoint de teste** - Acesse:
   ```
   http://seu-dominio/api/v1/accounts
   ```

3. **Documentação da API** - Acesse:
   ```
   http://seu-dominio/docs
   ```

## 🛠️ Solução de Problemas

### Erro: "relation 'instagram_accounts' does not exist"

**Solução**: A aplicação agora cria as tabelas automaticamente na inicialização. Se o erro persistir:

#### Opção 1: Reiniciar a Aplicação
1. No EasyPanel, pare a aplicação
2. Aguarde 10 segundos
3. Inicie a aplicação novamente
4. Verifique os logs para confirmar a criação das tabelas

#### Opção 2: Executar Script Manual (se disponível)
Se você tiver acesso ao terminal do container:

```bash
# Acesse o terminal do container no EasyPanel
python force_create_tables.py
```

#### Opção 3: Verificar Configuração do Banco
1. Verifique se o PostgreSQL está rodando
2. Verifique se as credenciais estão corretas
3. Verifique se o banco de dados 'servidor' existe
4. Verifique se o usuário tem permissões para criar tabelas

#### Opção 4: Reconstruir o Container
1. No EasyPanel, delete a aplicação
2. Reconstrua a aplicação com as configurações corretas
3. Certifique-se de que o PostgreSQL está rodando antes de iniciar a aplicação

### Erro: "connect() got an unexpected keyword argument 'sslmode'"

**Solução**: Este erro foi corrigido. O parâmetro `sslmode` agora é tratado corretamente.

### Erro de conexão com banco de dados

**Solução**: 
1. Verifique se o nome do serviço PostgreSQL está correto: `servidor_fastapi-postgres`
2. Verifique se as credenciais estão corretas
3. Aguarde alguns segundos para o banco inicializar completamente
4. Verifique se o banco de dados 'servidor' existe

### Logs Importantes a Verificar

Procure por estas mensagens nos logs:

**✅ Sucesso:**
```
✅ Banco de dados disponível na tentativa X
✅ Tabelas criadas com sucesso!
✅ Tabela instagram_accounts confirmada!
```

**❌ Problemas:**
```
❌ Banco de dados não ficou disponível
❌ Erro ao criar tabelas
⚠️ Falha na inicialização do banco de dados
```

## 🔧 Scripts Disponíveis

### `init_db.py`
- Executado automaticamente na inicialização
- Aguarda o banco ficar disponível
- Cria as tabelas automaticamente

### `force_create_tables.py`
- Script manual para forçar criação de tabelas
- Remove tabelas existentes e recria
- Útil para resolver problemas de schema

### `test_db_connection.py`
- Testa a conexão com o banco de dados
- Verifica se as credenciais estão corretas

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs da aplicação** no EasyPanel
2. **Execute o script de teste**: `python test_db_connection.py`
3. **Verifique se todos os serviços estão rodando**
4. **Confirme a ordem de inicialização**: PostgreSQL → Redis → Aplicação
5. **Verifique as variáveis de ambiente** estão corretas

### Comandos Úteis para Debug

```bash
# Testar conexão com banco
python test_db_connection.py

# Forçar criação de tabelas
python force_create_tables.py

# Verificar logs da aplicação
docker logs <container_name>
``` 