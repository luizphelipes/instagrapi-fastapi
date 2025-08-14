# 🔧 Solução para Erros de Deploy

## ❌ Problemas Identificados

### 1. Erro de Chave Fernet
```
ValueError: Fernet key must be 32 url-safe base64-encoded bytes.
```

### 2. Erro de Driver PostgreSQL
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
```

## ✅ Soluções Implementadas

### 🔑 Chave Fernet (RESOLVIDO)
- ✅ Sistema agora gera chaves automaticamente
- ✅ Validação automática do formato da chave
- ✅ Tratamento de erro robusto

### 📦 Driver PostgreSQL (RESOLVIDO)
- ✅ Removido `psycopg2-binary` do requirements.txt
- ✅ Mantido apenas `asyncpg` para conexões assíncronas
- ✅ Configuração correta do engine SQLAlchemy
- ✅ Forçado uso do driver async com `future=True`

## 🚀 Como Aplicar as Correções

### Opção 1: Reconstruir Container (RECOMENDADO)

#### No Windows:
```bash
# Execute o script batch
rebuild.bat
```

#### No Linux/Mac:
```bash
# Torne o script executável
chmod +x rebuild.sh

# Execute o script
./rebuild.sh
```

### Opção 2: Comandos Manuais

```bash
# 1. Para os containers
docker-compose down

# 2. Remove containers e imagens antigas
docker-compose down --rmi all

# 3. Reconstrói sem cache
docker-compose build --no-cache

# 4. Inicia os serviços
docker-compose up -d

# 5. Verifica logs
docker-compose logs -f api
```

### Opção 3: EasyPanel (Se estiver usando)

1. **Acesse o EasyPanel**
2. **Vá para o projeto**
3. **Clique em "Rebuild" ou "Recreate"**
4. **Aguarde a reconstrução completa**

## 🔍 Verificação

Após a reconstrução, você deve ver:

```
✅ Chave gerada automaticamente
✅ Sistema iniciando sem erros
✅ API rodando na porta 8000
```

## 📋 Logs Esperados

```
INFO:     Uvicorn running on http://0.0.0.0:8000
🔑 Nova chave gerada: [chave_gerada]
💡 Adicione esta chave ao seu arquivo .env como ENCRYPTION_KEY=
INFO:     Application startup complete
```

## 🧪 Teste de Conexão

Para testar se a conexão com o banco está funcionando:

```bash
# Execute o script de teste
python test_db_connection.py
```

Você deve ver:
```
✅ Engine criado com sucesso
✅ Conexão bem-sucedida!
📋 Versão do PostgreSQL: [versão]
✅ Engine fechado com sucesso
🎉 Teste concluído com sucesso!
```

## ⚠️ Importante

1. **Copie a chave gerada** e adicione ao seu `.env`:
   ```
   ENCRYPTION_KEY=sua_chave_gerada_aqui
   ```

2. **Mantenha a chave segura** - ela é necessária para descriptografar dados

3. **Use a mesma chave** em todos os deploys para manter compatibilidade

4. **Não use psycopg2** - estamos usando asyncpg para conexões assíncronas

## 🔧 Mudanças Técnicas

### Requirements.txt
```diff
- psycopg2-binary==2.9.9
+ asyncpg==0.29.0  # Já estava presente
```

### Database.py
```python
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    # Força o uso do driver asyncpg
    future=True,
    # Especifica explicitamente o driver
    connect_args={
        "server_settings": {
            "application_name": "instagram_api"
        }
    }
)
```

## 🆘 Se ainda houver problemas

1. **Verifique se o Docker está rodando**
2. **Verifique se as portas 8000, 5432, 6379 estão livres**
3. **Verifique se o arquivo `.env` existe e está configurado**
4. **Execute `docker system prune -a` para limpar cache**
5. **Teste a conexão com: `python test_db_connection.py`**

## 📞 Suporte

Se os problemas persistirem, verifique:
- Logs completos: `docker-compose logs api`
- Status dos containers: `docker-compose ps`
- Configuração do `.env`
- Teste de conexão: `python test_db_connection.py` 