# Deploy Frontend com Apache

Este guia mostra como fazer build e servir o frontend com Apache.

## 🏗️ Build para Produção

### 1. Instalar dependências

```bash
cd frontend
npm install
```

### 2. Configurar variáveis de ambiente

Crie o arquivo `.env` ou `.env.production`:

```env
# URL da API em produção
VITE_API_URL=https://api.seudominio.com
VITE_WS_URL=wss://api.seudominio.com
```

### 3. Build

```bash
npm run build
```

Isso irá gerar os arquivos estáticos em `dist/`

## 🌐 Configuração do Apache

### Opção 1: VirtualHost dedicado

Crie `/etc/apache2/sites-available/interview-ai.conf`:

```apache
<VirtualHost *:80>
    ServerName seudominio.com
    ServerAlias www.seudominio.com
    
    DocumentRoot /var/www/interview-ai/frontend
    
    <Directory /var/www/interview-ai/frontend>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # Habilita rewrite para SPA
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # Proxy para API
    ProxyPreserveHost On
    ProxyPass /api http://localhost:8000
    ProxyPassReverse /api http://localhost:8000
    
    # WebSocket proxy
    RewriteEngine on
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/ws/(.*) ws://localhost:8000/ws/$1 [P,L]
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/interview-ai-error.log
    CustomLog ${APACHE_LOG_DIR}/interview-ai-access.log combined
    
    # Compressão
    <IfModule mod_deflate.c>
        AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript application/json
    </IfModule>
    
    # Cache para assets
    <IfModule mod_expires.c>
        ExpiresActive On
        ExpiresByType image/jpg "access plus 1 year"
        ExpiresByType image/jpeg "access plus 1 year"
        ExpiresByType image/gif "access plus 1 year"
        ExpiresByType image/png "access plus 1 year"
        ExpiresByType image/svg+xml "access plus 1 year"
        ExpiresByType text/css "access plus 1 month"
        ExpiresByType application/javascript "access plus 1 month"
        ExpiresByType application/x-font-woff "access plus 1 year"
    </IfModule>
</VirtualHost>
```

### Opção 2: Subdiretório

Se você quer servir em `seudominio.com/interview-ai/`:

```apache
Alias /interview-ai /var/www/interview-ai/frontend

<Directory /var/www/interview-ai/frontend>
    Options -Indexes +FollowSymLinks
    AllowOverride All
    Require all granted
    
    RewriteEngine On
    RewriteBase /interview-ai/
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /interview-ai/index.html [L]
</Directory>

# Proxy para API
ProxyPass /interview-ai/api http://localhost:8000
ProxyPassReverse /interview-ai/api http://localhost:8000
```

**Importante**: Se usar subdiretório, atualize `vite.config.js`:

```javascript
export default defineConfig({
  base: '/interview-ai/',
  // ... resto da config
})
```

## 📦 Deploy

### 1. Copiar arquivos

```bash
# Build
cd frontend
npm run build

# Copiar para Apache
sudo mkdir -p /var/www/interview-ai
sudo cp -r dist/* /var/www/interview-ai/frontend/

# Ajustar permissões
sudo chown -R www-data:www-data /var/www/interview-ai
sudo chmod -R 755 /var/www/interview-ai
```

### 2. Habilitar módulos necessários

```bash
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod expires
sudo a2enmod deflate
```

### 3. Habilitar site

```bash
sudo a2ensite interview-ai.conf
sudo systemctl reload apache2
```

### 4. Verificar configuração

```bash
sudo apache2ctl configtest
```

## 🔒 HTTPS com SSL/TLS

### Usando Let's Encrypt (Certbot)

```bash
# Instalar certbot
sudo apt install certbot python3-certbot-apache

# Obter certificado
sudo certbot --apache -d seudominio.com -d www.seudominio.com

# Renovação automática já está configurada
```

O Certbot irá criar automaticamente:
- Redirect HTTP → HTTPS
- Configuração SSL no VirtualHost :443

### Atualizar .env para HTTPS

```env
VITE_API_URL=https://api.seudominio.com
VITE_WS_URL=wss://api.seudominio.com
```

## 🔄 Script de Deploy Automático

Crie `frontend/deploy.sh`:

```bash
#!/bin/bash

echo "🏗️  Building frontend..."
npm run build

echo "📦 Deploying to Apache..."
sudo rm -rf /var/www/interview-ai/frontend/*
sudo cp -r dist/* /var/www/interview-ai/frontend/

echo "🔧 Fixing permissions..."
sudo chown -R www-data:www-data /var/www/interview-ai
sudo chmod -R 755 /var/www/interview-ai

echo "♻️  Reloading Apache..."
sudo systemctl reload apache2

echo "✅ Deploy complete!"
echo "🌐 Access: http://seudominio.com"
```

Torne executável:

```bash
chmod +x frontend/deploy.sh
```

Use:

```bash
./frontend/deploy.sh
```

## 🧪 Testar Localmente

Antes de fazer deploy, teste o build:

```bash
cd frontend
npm run build
npm run preview
```

Acesse http://localhost:4173

## 📊 Monitoramento

### Logs do Apache

```bash
# Erros
sudo tail -f /var/log/apache2/interview-ai-error.log

# Acessos
sudo tail -f /var/log/apache2/interview-ai-access.log
```

### Verificar se está funcionando

```bash
curl -I http://seudominio.com
curl http://seudominio.com/api/health
```

## 🐛 Troubleshooting

### Página em branco após deploy
- Verifique console do navegador
- Confirme que `VITE_API_URL` está correto no build
- Verifique permissões dos arquivos

### API não responde
- Confirme que backend está rodando (`systemctl status backend` ou Docker)
- Teste proxy: `curl http://localhost/api/health`
- Verifique logs do Apache

### WebSocket não conecta
- Módulo `proxy_wstunnel` deve estar habilitado
- Verifique regra de rewrite para WebSocket
- Teste com: `wscat -c ws://seudominio.com/ws/query`

### Erro 404 ao recarregar página
- RewriteEngine deve estar habilitado
- Verifique AllowOverride All
- Confirme que mod_rewrite está ativo

## 📝 Checklist de Deploy

- [ ] Build realizado com `.env.production` correto
- [ ] Arquivos copiados para `/var/www/interview-ai/frontend/`
- [ ] Permissões ajustadas (www-data:www-data)
- [ ] VirtualHost configurado
- [ ] Módulos Apache habilitados
- [ ] Site habilitado (a2ensite)
- [ ] Apache recarregado
- [ ] SSL configurado (se produção)
- [ ] Backend está rodando
- [ ] Proxy API funcionando
- [ ] WebSocket funcionando
- [ ] Testado em navegador

## 🚀 Atualização

Para atualizar a aplicação:

```bash
cd frontend
git pull  # se estiver usando git
npm install  # se houver novas dependências
npm run build
./deploy.sh  # ou copie manualmente
```

## 💡 Dicas

1. **Cache**: Após deploy, pode ser necessário fazer hard refresh (Ctrl+Shift+R)
2. **CDN**: Considere usar CloudFlare para assets estáticos
3. **Backup**: Mantenha backup da pasta `/var/www/interview-ai`
4. **CI/CD**: Considere automatizar com GitHub Actions ou GitLab CI
5. **Monitoramento**: Use ferramentas como PM2, Uptime Robot ou New Relic

## 📚 Referências

- [Apache mod_rewrite](https://httpd.apache.org/docs/current/mod/mod_rewrite.html)
- [Apache mod_proxy](https://httpd.apache.org/docs/current/mod/mod_proxy.html)
- [Vite Build](https://vitejs.dev/guide/build.html)
- [Let's Encrypt](https://letsencrypt.org/getting-started/)
