# Interview AI - Frontend

Interface web para o sistema de análise de datasheets com IA.

## 🚀 Tecnologias

- **Vue 3** - Framework JavaScript progressivo
- **Vite** - Build tool e dev server
- **Vue Router** - Roteamento SPA
- **TanStack Query (Vue Query)** - Gerenciamento de estado assíncrono
- **PrimeVue** - Biblioteca de componentes UI
- **Axios** - Cliente HTTP
- **WebSocket** - Comunicação em tempo real

## 📋 Funcionalidades

### Chat com IA
- Interface de chat em tempo real via WebSocket
- Perguntas em linguagem natural sobre os datasheets
- Visualização de SQL gerado e explicações
- Feedback de progresso em tempo real

### Gerenciamento de Datasheets
- Visualização de múltiplos datasheets em abas
- Tabelas com paginação
- Busca/filtro em tempo real
- Ordenação por colunas
- Upload de novos arquivos Excel (.xlsx, .xls)
- Lazy loading - cada aba carrega dados apenas quando acessada

## 🛠️ Instalação

### Pré-requisitos

- Node.js 18+ e npm/yarn
- Backend rodando em http://localhost:8000

### Configuração

1. **Instalar dependências**:
```bash
npm install
```

2. **Configurar variáveis de ambiente**:
```bash
cp .env.example .env
```

Edite o `.env` se necessário:
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

3. **Rodar em desenvolvimento**:
```bash
npm run dev
```

A aplicação estará disponível em http://localhost:3000

4. **Build para produção**:
```bash
npm run build
```

Os arquivos serão gerados em `dist/`

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js          # Cliente API e funções HTTP
│   ├── components/
│   │   └── DatasheetTable.vue # Componente de tabela com paginação
│   ├── views/
│   │   ├── ChatView.vue       # Página do chat
│   │   └── DatasheetsView.vue # Página de datasheets
│   ├── router/
│   │   └── index.js           # Configuração de rotas
│   ├── App.vue                # Componente raiz
│   ├── main.js                # Entry point
│   └── style.css              # Estilos globais
├── index.html
├── vite.config.js
└── package.json
```

## 🎨 Componentes Principais

### ChatView
- Conexão WebSocket persistente
- Reconexão automática
- Histórico de mensagens
- Eventos de progresso (loading_tables, generating_sql, etc.)
- Formatação de markdown em mensagens

### DatasheetsView
- Lista de tabelas via TanStack Query
- Navegação por abas (TabView)
- Upload de arquivos com validação
- Invalidação de cache após upload

### DatasheetTable
- useQuery individual por tabela
- Paginação customizada
- Busca com debounce (500ms)
- Ordenação por coluna
- Formatação de valores (números, datas, booleanos)
- keepPreviousData para transições suaves

## 🔌 API Integration

O frontend se comunica com o backend através de:

### REST Endpoints
- `GET /tables` - Lista tabelas
- `GET /tables/{table_name}/data` - Dados paginados
- `POST /upload/excel` - Upload de arquivos
- `POST /query` - Query HTTP (não usado, preferimos WebSocket)

### WebSocket
- `WS /ws/query` - Chat em tempo real
  - Eventos: connected, loading_tables, generating_sql, response, error, end

## 🎯 Uso

### Chat
1. Acesse a página "Chat"
2. Aguarde conexão WebSocket
3. Digite perguntas como:
   - "Quantas vendas tivemos no último mês?"
   - "Qual o produto mais vendido?"
   - "Mostre a média de preço por categoria"
4. Receba resposta humanizada + SQL + explicação

### Datasheets
1. Acesse "Datasheets"
2. Clique em "Upload Datasheet" para adicionar arquivos
3. Navegue entre abas (cada aba = uma tabela)
4. Use busca para filtrar registros
5. Clique em cabeçalhos para ordenar
6. Use paginação para navegar

## 🔧 Configuração do Vite

O proxy está configurado para redirecionar:
- `/api/*` → `http://localhost:8000`
- `/ws/*` → `ws://localhost:8000`

Isso evita problemas de CORS em desenvolvimento.

## 📦 Dependências Principais

```json
{
  "vue": "^3.4.0",
  "vue-router": "^4.2.5",
  "@tanstack/vue-query": "^5.17.0",
  "primevue": "^3.46.0",
  "axios": "^1.6.0"
}
```

## 🐛 Troubleshooting

### WebSocket não conecta
- Verifique se o backend está rodando
- Confirme a URL no `.env` (VITE_WS_URL)
- Verifique console do navegador para erros

### Tabelas não carregam
- Backend deve estar acessível
- Verifique se há datasheets importados
- Abra Network tab para ver requisições

### Upload falha
- Apenas .xlsx e .xls são aceitos
- Tamanho máximo definido pelo backend
- Verifique CORS no backend

## 📝 Notas de Desenvolvimento

- **TanStack Query** gerencia cache automaticamente
- Queries são invalidadas após upload bem-sucedido
- `keepPreviousData: true` mantém dados antigos durante loading
- Debounce de 500ms no search evita requisições excessivas
- WebSocket reconecta automaticamente após desconexão

## 🚀 Deploy

### Desenvolvimento (Node.js)

```bash
npm run build
npm run preview
```

### Produção (Apache)

Veja instruções completas em [DEPLOY_APACHE.md](./DEPLOY_APACHE.md)

Resumo:
1. Build: `npm run build`
2. Copiar `dist/*` para `/var/www/interview-ai/frontend/`
3. Configurar VirtualHost do Apache
4. Habilitar módulos: rewrite, proxy, proxy_http, proxy_wstunnel
5. Configurar proxy para API e WebSocket

## 📄 Licença

Este projeto faz parte do Interview AI system.
