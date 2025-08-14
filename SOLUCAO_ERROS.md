# 🔧 Solução para Erros de Deploy

## ❌ Problemas Identificados

### 1. Erro de Chave Fernet
```
ValueError: Fernet key must be 32 url-safe base64-encoded bytes.
```

### 2. Erro de Dependência PostgreSQL
```
ModuleNotFoundError: No module named 'psycopg2'
```

## ✅ Soluções Implementadas

### 🔑 Chave Fernet (RESOLVIDO)
- ✅ Sistema agora gera chaves automaticamente
- ✅ Validação automática do formato da chave
- ✅ Tratamento de erro robusto

### 📦 Dependências PostgreSQL (RESOLVIDO)
- ✅ Adicionado `psycopg2-binary==2.9.9` ao `requirements.txt`
- ✅ Dockerfile já tem `libpq-dev` instalado

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

## ⚠️ Importante

1. **Copie a chave gerada** e adicione ao seu `.env`:
   ```
   ENCRYPTION_KEY=sua_chave_gerada_aqui
   ```

2. **Mantenha a chave segura** - ela é necessária para descriptografar dados

3. **Use a mesma chave** em todos os deploys para manter compatibilidade

## 🆘 Se ainda houver problemas

1. **Verifique se o Docker está rodando**
2. **Verifique se as portas 8000, 5432, 6379 estão livres**
3. **Verifique se o arquivo `.env` existe e está configurado**
4. **Execute `docker system prune -a` para limpar cache**

## 📞 Suporte

Se os problemas persistirem, verifique:
- Logs completos: `docker-compose logs api`
- Status dos containers: `docker-compose ps`
- Configuração do `.env` 