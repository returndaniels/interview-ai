# Interview AI - Guia de Instalação Completa

Este guia cobre a instalação e execução completa do sistema.

## 📋 Pré-requisitos

### Backend
- Docker e Docker Compose
- Python 3.11+ (para desenvolvimento local sem Docker)

### Frontend
- Node.js 18+ e npm (desenvolvimento)
- Apache 2.4+ (produção)

## 🚀 Instalação Rápida

### Backend (Docker - Recomendado)

```bash
# Na raiz do projeto
cp .env.example .env
nano .env  # Adicione sua OPENAI_API_KEY

# Subir backend + MariaDB
docker compose up -d

# Verificar
curl http://localhost:8000/health
docker compose ps
```

Serviços disponíveis:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MariaDB**: localhost:3306

### Frontend 

**Desenvolvimento:**

```bash
cd frontend
npm install
cp .env.example .env

# Rodar com hot-reload
npm run dev
```

Frontend em: http://localhost:3000

**Produção (Apache):**

```bash
# Build
cd frontend
npm run build

# Deploy
sudo cp -r dist/* /var/www/interview-ai/frontend/
```

Veja [frontend/DEPLOY_APACHE.md](frontend/DEPLOY_APACHE.md) para configuração completa do Apache.


## 📦 Estrutura do Projeto

```
interview-ai/
├── backend/                     # API FastAPI
│   ├── app/
│   │   ├── controllers/
│   │   │   ├── datasheets.py   # Import Excel
│   │   │   ├── openai.py       # Chat IA
│   │   │   └── tables.py       # Paginação
│   │   ├── main.py             # FastAPI app
│   │   ├── database.py         # MariaDB
│   │   └── utils.py
│   ├── tests/
│   ├── docker-compose.yml      # Backend + MariaDB
│   └── Dockerfile
│
├── frontend/                    # Vue.js SPA
│   ├── src/
│   │   ├── api/client.js
│   │   ├── components/DatasheetTable.vue
│   │   ├── views/
│   │   │   ├── ChatView.vue
│   │   │   └── DatasheetsView.vue
│   │   └── router/
│   ├── DEPLOY_APACHE.md        # Guia de deploy
│   └── package.json
│
└── docker-compose.yml          # Backend + MariaDB (raiz)
```

## 🔧 Configuração Detalhada

### Backend (.env na raiz)

```env
# Database
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=interview_ai
MYSQL_USER=user
MYSQL_PASSWORD=password

# OpenAI
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Frontend (.env em frontend/)

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

Para produção com Apache:
```env
VITE_API_URL=https://api.seudominio.com
VITE_WS_URL=wss://api.seudominio.com
```

## 🧪 Testando o Sistema

### 1. Testar Backend

```bash

# Executar testes
docker compose exec backend pytest tests/ -v

# Testar endpoints manualmente
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/tables
```

### 2. Testar Frontend

Acesse http://localhost:3000 e:
1. Vá para "Datasheets"
2. Faça upload de um arquivo Excel
3. Navegue pelas abas
4. Teste filtros e paginação
5. Vá para "Chat"
6. Faça perguntas sobre os dados

## 📊 Fluxo de Uso Completo

### Upload de Datasheet

1. **Frontend**: DatasheetsView → Botão "Upload"
2. Selecione arquivo .xlsx ou .xls
3. **Backend**: `POST /upload/excel`
4. Arquivo é processado em chunks
5. Tabela criada com prefixo `datasheet_`
6. **Frontend**: Lista de tabelas atualizada

### Visualização de Dados

1. **Frontend**: Clique em aba do datasheet
2. **useQuery** dispara requisição
3. **Backend**: `GET /tables/{table_name}/data?page=1&page_size=50`
4. Controller `get_table_data_paginated()` processa
5. Retorna dados + paginação + colunas
6. **Frontend**: Renderiza tabela com PrimeVue

### Chat com IA

1. **Frontend**: ChatView conecta WebSocket
2. Usuário digita pergunta
3. **WebSocket**: Envia `{"question": "..."}`
4. **Backend**: 
   - Carrega tabelas
   - Gera contexto
   - OpenAI gera SQL
   - Executa query
   - Humaniza resultado
5. **Frontend**: Recebe eventos de progresso + resposta final

## 🔍 Endpoints da API

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Info da API |
| GET | `/health` | Health check |
| GET | `/tables` | Lista datasheets |
| GET | `/tables/{name}/data` | Dados paginados |
| POST | `/upload/excel` | Upload Excel |
| POST | `/query` | Query HTTP |
| WS | `/ws/query` | Chat WebSocket |

## 🛠️ Desenvolvimento

### Docker Compose - Comandos Úteis

```bash
# Na raiz do projeto (levanta tudo)
docker compose up -d              # Inicia todos os serviços
docker compose down               # Para todos os serviços
docker compose down -v            # Para e remove volumes
docker compose logs -f            # Logs em tempo real
docker compose logs -f frontend   # Logs apenas do frontend
docker compose logs -f backend    # Logs apenas do backend
docker compose restart frontend   # Reinicia frontend
docker compose ps                 # Status dos containers

# Reconstruir imagens
docker compose up -d --build

# Acessar containers
docker compose exec frontend sh
docker compose exec backend bash
```

### Backend

```bash
# Dentro do container
docker compose exec backend bash

# Ou localmente
cd backend

# Logs em tempo real
docker compose logs -f backend

# Parar tudo
docker compose down
```

### Frontend

```bash
# Desenvolvimento com hot-reload
cd frontend
npm run dev

# Ou com Docker
docker compose up -d

# Build para produção
npm run build

# Preview do build
npm run preview

# Adicionar dependência
npm install <package>

# Produção com Docker + Nginx
docker compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Backend não sobe
```bash
# Verificar logs
docker compose logs backend mariadb

# Recriar containers
docker compose down -v
docker compose up -d --build
```

### Erro de conexão com banco
```bash
# Verificar se MariaDB está healthy
docker compose ps

# Testar conexão manual
docker compose exec mariadb mysql -u user -p interview_ai
```

### Frontend não conecta com backend
- Verifique se backend está em http://localhost:8000
- Confirme CORS está habilitado no backend
- Verifique proxy no vite.config.js
- Abra DevTools → Network para ver requisições

### WebSocket não conecta
- Backend deve estar rodando
- Verifique VITE_WS_URL no .env
- Teste: `wscat -c ws://localhost:8000/ws/query`

## 📚 Documentação

- **Backend**: `/backend/README.md`
- **Frontend**: `/frontend/README.md`
- **Testes**: `/backend/TESTING_GUIDE.md`
- **Chat**: `/backend/CHAT_GUIDE.md`

## 🚀 Deploy em Produção

### Backend
```bash
# Build otimizado
docker compose -f docker-compose.prod.yml up -d

# Ou use Kubernetes/AWS ECS
```

### Frontend
```bash
# Build
cd frontend
npm run build

# Servir com Nginx/Apache
# Ou deploy em Vercel/Netlify
```

## 💡 Dicas

1. **Performance**: Use page_size adequado (50-100)
2. **Cache**: TanStack Query cacheia automaticamente
3. **Debounce**: Search tem delay de 500ms
4. **WebSocket**: Reconexão automática após 3s
5. **Segurança**: Apenas tabelas `datasheet_*` são acessíveis

## 📝 Próximos Passos

- [ ] Adicionar autenticação (JWT)
- [ ] Implementar roles e permissões
- [ ] Dashboard com gráficos
- [ ] Export de dados (CSV, PDF)
- [ ] Histórico de queries
- [ ] Cache Redis para queries frequentes
- [ ] Rate limiting
- [ ] Monitoring (Prometheus/Grafana)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Add nova feature'`)
4. Push para branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Projeto Interview AI - Sistema de análise de datasheets com IA
