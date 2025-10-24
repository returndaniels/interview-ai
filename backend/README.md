# 🤖 Interview AI Backend

Backend FastAPI para importação e análise inteligente de datasheets XLSX/XLS com IA.

## 📋 Índice

- [Características](#-características)
- [Arquitetura](#-arquitetura)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Segurança](#-segurança)
- [Troubleshooting](#-troubleshooting)

## ✨ Características

- 📊 **Import de Excel**: Suporte a arquivos XLSX e XLS com processamento em chunks
- 🤖 **IA Integrada**: Queries SQL geradas automaticamente via OpenAI GPT-4
- 🔍 **Multi-tabelas**: Suporte a JOINs automáticos entre múltiplas tabelas
- 💬 **Chat Inteligente**: WebSocket para interação em tempo real
- 🔒 **Segurança**: Validação de queries, acesso restrito a tabelas `datasheet_*`
- 🚀 **Performance**: Processamento assíncrono e chunked para grandes arquivos
- 🐳 **Docker**: Ambiente completo com FastAPI + MariaDB

## 🏗️ Arquitetura

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── database.py          # Conexão MariaDB
│   ├── utils.py             # Funções auxiliares
│   └── controllers/
│       ├── __init__.py
│       ├── datasheets.py    # Import de Excel
│       └── openai.py        # IA e geração de SQL
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── init.sql                 # Script de inicialização DB
├── init-db.sh              # Helper para criar banco
└── .env                    # Variáveis de ambiente
```

## 📦 Requisitos

- Docker & Docker Compose
- Python 3.11+ (para desenvolvimento local)
- OpenAI API Key

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/returndaniels/interview-ai.git
cd interview-ai/backend
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` com suas credenciais:

```env
# Database
MARIADB_ROOT_PASSWORD=your_secure_password
MARIADB_USER=user
MARIADB_PASSWORD=your_db_password
DATABASE_NAME=interview_ai

# OpenAI
OPENAI_API_KEY=sk-proj-...your-key...
```

### 3. Inicie os containers

```bash
docker-compose up -d --build
```

### 4. Inicialize o banco de dados

```bash
chmod +x init-db.sh
./init-db.sh
```

### 5. Verifique a saúde dos serviços

```bash
docker ps  # Deve mostrar (healthy) para ambos containers
```

## 💻 Uso

### Acessar a Aplicação

- **API**: http://localhost:8000
- **Docs Interativa (Swagger)**: http://localhost:8000/docs
- **Docs Alternativa (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Importar um Datasheet

```bash
curl -X POST "http://localhost:8000/upload/excel" \
  -F "file=@vendas.xlsx" \
  -F "table_name=vendas"
```

### Fazer uma Pergunta (HTTP)

```bash
curl -X POST "http://localhost:8000/query?question=Quantas%20vendas%20temos%20no%20total?"
```

### Conectar via WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/query');

ws.onopen = () => {
  ws.send(JSON.stringify({
    question: "Qual o produto mais vendido?"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type, data);
};
```

## 📡 API Endpoints

### Core

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Informações da API |
| GET | `/health` | Health check (DB status) |

### Datasheets

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/upload/excel` | Upload de arquivo Excel |
| GET | `/tables` | Lista tabelas disponíveis |
| GET | `/tables/{name}` | Detalhes de uma tabela |

### Queries com IA

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/query` | Query via linguagem natural (polling) |
| WS | `/ws/query` | Query via WebSocket (real-time) |

### Exemplo de Resposta

```json
{
  "question": "Quantas vendas por categoria?",
  "sql_query": "SELECT categoria, COUNT(*) as total FROM `datasheet_vendas` GROUP BY categoria",
  "sql_explanation": "Esta query conta o número de vendas agrupadas por categoria",
  "tables_used": ["datasheet_vendas"],
  "results_count": 5,
  "humanized_response": "Encontrei 5 categorias...",
  "raw_results": [...]
}
```

## 🔒 Segurança

### Restrições de Tabelas

O sistema **APENAS** acessa tabelas com prefixo `datasheet_`:

- ✅ `datasheet_vendas` → **Permitido**
- ✅ `datasheet_produtos` → **Permitido**
- ❌ `users` → **Bloqueado**
- ❌ `sessions` → **Bloqueado**

### Validação de Queries

- ✅ Apenas comandos `SELECT`
- ❌ `INSERT`, `UPDATE`, `DELETE`, `DROP` bloqueados
- ✅ Validação via regex de nomes de tabelas
- ✅ Prevenção de SQL injection

### Camadas de Proteção

1. **API Endpoints**: Filtra lista de tabelas
2. **SQL Validator**: Valida sintaxe e comandos
3. **Regex Check**: Verifica prefixo `datasheet_`
4. **AI Prompt**: Instrui IA a usar apenas tabelas permitidas

## 🔧 Troubleshooting

### Problema: "Unknown database 'interview_ai'"

**Causa:** Volume do MariaDB já existia antes da configuração.

**Solução rápida:**
```bash
./init-db.sh
```

**Solução completa (APAGA DADOS):**
```bash
docker-compose down -v
docker-compose up -d --build
```

### Problema: Container unhealthy

**Verificar logs:**
```bash
docker logs interview-ai-backend --tail 50
docker logs interview-ai-mariadb --tail 50
```

**Reiniciar serviços:**
```bash
docker-compose restart
```

### Problema: Imports incorretos / ModuleNotFoundError

**Solução:**
```bash
docker-compose down
docker-compose up -d --build
```

### Problema: Permissão negada em uploads/

**Solução:**
```bash
sudo chown -R $USER:$USER uploads/
```

## 🛠️ Desenvolvimento

### Desenvolvimento Local (sem Docker)

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Ver Logs em Tempo Real

```bash
docker-compose logs -f backend
```

### Acessar Container

```bash
docker exec -it interview-ai-backend bash
```

### Executar Testes

```bash
docker exec interview-ai-backend pytest
```

## 📊 Comandos Úteis

```bash
# Parar containers
docker-compose down

# Parar e remover volumes (APAGA DADOS)
docker-compose down -v

# Rebuild sem cache
docker-compose build --no-cache

# Ver status
docker-compose ps

# Ver uso de recursos
docker stats

# Backup do banco
docker exec interview-ai-mariadb mysqldump -u root -pmariadbrootPW interview_ai > backup.sql

# Restaurar backup
docker exec -i interview-ai-mariadb mysql -u root -pmariadbrootPW interview_ai < backup.sql
```

## 📚 Documentação Adicional

- [CHAT_GUIDE.md](CHAT_GUIDE.md) - Guia de uso do chat
- [SECURITY_UPDATE.md](SECURITY_UPDATE.md) - Detalhes da segurança
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Guia de testes
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Resumo técnico

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Add nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT.

## 🙋 Suporte

Para reportar bugs ou solicitar features, abra uma [issue](https://github.com/returndaniels/interview-ai/issues).

---

**Desenvolvido com ❤️ usando FastAPI, OpenAI GPT-4 e MariaDB**
