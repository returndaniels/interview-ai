# Interview AI Backend

Backend FastAPI para importação de datasheets XLSX e XLS.

## Estrutura do Projeto

```
backend/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .env.example
└── main.py
```

## Configuração

1. **Copie o arquivo de ambiente:**
   ```bash
   cp .env.example .env
   ```

2. **Edite o `.env` com suas credenciais:**
   ```
   MARIADB_ROOT_PASSWORD=your_secure_password
   MARIADB_USER=interview_user
   MARIADB_PASSWORD=your_secure_password
   ```

## Executar com Docker Compose

### Desenvolvimento

```bash
# Buildar e iniciar os containers
docker-compose up --build

# Ou em modo detached (background)
docker-compose up -d --build

# Inicializar o banco de dados (primeira vez ou após limpar volumes)
./init-db.sh

# Ver logs
docker-compose logs -f backend

# Parar os containers
docker-compose down

# Parar e remover volumes (cuidado: apaga dados do banco)
docker-compose down -v
```

### 🔧 Troubleshooting

**Problema: "Unknown database 'interview_ai'"**

Isso acontece quando o volume do MariaDB já existia antes da configuração. O MariaDB executa scripts em `/docker-entrypoint-initdb.d/` **APENAS na primeira inicialização** (quando o volume `/var/lib/mysql` está vazio).

**Por que isso acontece?**
1. Volume persistente mantém dados entre restarts
2. Scripts de inicialização só rodam em volumes vazios
3. Se você rodou `docker-compose up` antes de configurar o `MARIADB_DATABASE`, o volume foi criado sem o banco

**Solução 1 (Recomendada - Script helper):**
```bash
./init-db.sh
```

**Solução 2 (Limpar volumes e recriar - APAGA TODOS OS DADOS):**
```bash
docker-compose down -v  # Remove containers e volumes
docker-compose up -d --build  # Agora o init.sql será executado
```

**Solução 3 (Manual):**
```bash
docker exec interview-ai-mariadb mariadb -u root -pmariadbrootPW -e "CREATE DATABASE IF NOT EXISTS interview_ai; GRANT ALL PRIVILEGES ON interview_ai.* TO 'user'@'%'; FLUSH PRIVILEGES;"
```

### Acessar a API

- **API**: http://localhost:8000
- **Documentação Interativa (Swagger)**: http://localhost:8000/docs
- **Documentação Alternativa (ReDoc)**: http://localhost:8000/redoc

## Principais Recomendações Implementadas

### 1. **Hot Reload no Desenvolvimento**
   - Volume mapeado: `./:/app` permite editar código sem rebuild
   - Flag `--reload` no uvicorn

### 2. **Healthchecks**
   - Backend: `/health` endpoint
   - MariaDB: healthcheck nativo
   - Melhora orquestração e monitoramento

### 3. **Dependências Otimizadas**
   - `uvicorn[standard]`: Performance melhorada
   - `openpyxl`: Para arquivos .xlsx
   - `xlrd`: Para arquivos .xls legados
   - `pandas`: Processamento eficiente de dados

### 4. **Volumes Persistentes**
   - `mariadb_data`: Dados do banco
   - `uploads_data`: Arquivos enviados
   - Dados preservados entre restarts

### 5. **Rede Interna**
   - Comunicação segura entre backend e banco
   - Backend acessa banco via nome do serviço: `mariadb:3306`

### 6. **Variáveis de Ambiente**
   - Configurações sensíveis isoladas no `.env`
   - Database URL automática para SQLAlchemy

## Endpoints Disponíveis

- `GET /` - Informações da API
- `GET /health` - Health check
- `POST /upload/excel` - Upload de arquivo Excel
- `GET /files` - Lista arquivos enviados

## Próximos Passos

1. Implementar modelos SQLAlchemy para persistência
2. Adicionar autenticação (JWT)
3. Criar endpoints para consulta de dados importados
4. Adicionar validação de esquema dos datasheets
5. Implementar testes automatizados

## Desenvolvimento Local (sem Docker)

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn main:app --reload
```

## Comandos Úteis

```bash
# Ver containers rodando
docker-compose ps

# Acessar shell do container backend
docker-compose exec backend bash

# Acessar MariaDB
docker-compose exec mariadb mysql -u interview_user -p

# Rebuild apenas o backend
docker-compose up -d --build backend

# Ver uso de recursos
docker stats
```
