# Deploy - Backend e Frontend na mesma máquina (sem domínio público)

## 📋 Cenário
- Backend: Docker rodando em `localhost:8000`
- Frontend: Servido pelo Apache
- Mesma máquina, sem domínio público (usando IP)

## 🔧 Configuração

### 1. Atualizar `.env.production` do Frontend

Edite `/home/daniel/interview-ai/frontend/.env.production`:

```bash
# Substitua SEU_IP pelo IP público do servidor (ex: 192.168.1.100)
VITE_API_URL=/api
VITE_WS_URL=ws://SEU_IP/ws
```

**Descobrir seu IP público:**
```bash
# IP local da rede
hostname -I | awk '{print $1}'

# Ou
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Exemplo:**
```bash
VITE_API_URL=/api
VITE_WS_URL=ws://192.168.1.100/ws
```

### 2. Build do Frontend

```bash
cd /home/daniel/interview-ai/frontend
npm run build
```

### 3. Copiar para Apache

```bash
# Criar diretório
sudo mkdir -p /var/www/interview-ai/frontend

# Copiar build
sudo cp -r dist/* /var/www/interview-ai/frontend/

# Permissões
sudo chown -R www-data:www-data /var/www/interview-ai
sudo chmod -R 755 /var/www/interview-ai
```

### 4. Configurar Apache

```bash
# Copiar configuração de exemplo
sudo cp /home/daniel/interview-ai/frontend/apache-config-example.conf /etc/apache2/sites-available/interview-ai.conf

# Editar e adicionar o IP ou domínio
sudo nano /etc/apache2/sites-available/interview-ai.conf
```

**Descomentar e configurar a linha:**
```apache
ServerName 192.168.1.100  # Seu IP aqui
```

### 5. Habilitar módulos e site

```bash
# Módulos necessários
sudo a2enmod rewrite
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod headers
sudo a2enmod expires
sudo a2enmod deflate

# Habilitar site
sudo a2ensite interview-ai.conf

# Desabilitar site padrão (opcional)
sudo a2dissite 000-default.conf

# Testar configuração
sudo apache2ctl configtest

# Reiniciar Apache
sudo systemctl restart apache2
```

### 6. Garantir que Backend está rodando

```bash
cd /home/daniel/interview-ai/backend
docker-compose up -d

# Verificar
docker-compose ps
curl http://localhost:8000/health
```

### 7. Testar

Acesse no navegador:
- `http://SEU_IP/` - Frontend
- `http://SEU_IP/api/health` - API

## 🔍 Como Funciona

```
Navegador (Cliente)
    ↓
http://192.168.1.100/ → Apache (porta 80)
    ↓
Serve arquivos estáticos do frontend
    
Navegador faz request para:
http://192.168.1.100/api → Apache Proxy → http://127.0.0.1:8000 (Backend Docker)
ws://192.168.1.100/ws → Apache Proxy → ws://127.0.0.1:8000/ws (WebSocket)
```

**Por que não usar localhost:8000 diretamente?**
- `localhost` no navegador aponta para a máquina do CLIENTE (seu computador)
- O backend está no SERVIDOR (AWS, VPS, etc)
- Apache faz proxy: cliente → Apache (IP público) → backend (localhost do servidor)

## 🐛 Troubleshooting

### Erro: API não responde

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Verificar logs do Apache
sudo tail -f /var/log/apache2/interview-ai-error.log

# Verificar se proxy está funcionando
curl http://SEU_IP/api/health
```

### Erro: WebSocket não conecta

```bash
# Verificar módulo proxy_wstunnel
sudo apache2ctl -M | grep proxy_wstunnel

# Se não aparecer, habilitar:
sudo a2enmod proxy_wstunnel
sudo systemctl restart apache2
```

### Erro: 403 Forbidden

```bash
# Verificar permissões
ls -la /var/www/interview-ai/frontend/

# Corrigir
sudo chown -R www-data:www-data /var/www/interview-ai
sudo chmod -R 755 /var/www/interview-ai
```

### Erro: Página em branco

```bash
# Abrir console do navegador (F12)
# Verificar se há erros de CORS ou 404

# Recompilar com .env correto
cd /home/daniel/interview-ai/frontend
cat .env.production  # Verificar se está correto
npm run build
sudo cp -r dist/* /var/www/interview-ai/frontend/
```

### WebSocket usa http:// ao invés de ws://

Edite `.env.production` e certifique-se que tem `ws://` (não `http://`):
```bash
VITE_WS_URL=ws://192.168.1.100/ws  # ✅ Correto
VITE_WS_URL=http://192.168.1.100/ws  # ❌ Errado
```

## 🚀 Script de Deploy Rápido

Crie `/home/daniel/interview-ai/frontend/deploy-local.sh`:

```bash
#!/bin/bash

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🏗️  Building frontend...${NC}"
npm run build

echo -e "${BLUE}📦 Deploying to Apache...${NC}"
sudo rm -rf /var/www/interview-ai/frontend/*
sudo cp -r dist/* /var/www/interview-ai/frontend/

echo -e "${BLUE}🔧 Fixing permissions...${NC}"
sudo chown -R www-data:www-data /var/www/interview-ai
sudo chmod -R 755 /var/www/interview-ai

echo -e "${BLUE}♻️  Reloading Apache...${NC}"
sudo systemctl reload apache2

echo -e "${GREEN}✅ Deploy complete!${NC}"
echo -e "${GREEN}🌐 Access: http://$(hostname -I | awk '{print $1}')${NC}"
```

Tornar executável e usar:
```bash
chmod +x deploy-local.sh
./deploy-local.sh
```

## 📝 Checklist Rápido

- [ ] `.env.production` configurado com IP correto
- [ ] `npm run build` executado
- [ ] Arquivos copiados para `/var/www/interview-ai/frontend/`
- [ ] Apache configurado (`interview-ai.conf`)
- [ ] Módulos habilitados (`proxy`, `proxy_http`, `proxy_wstunnel`)
- [ ] Site habilitado (`a2ensite interview-ai.conf`)
- [ ] Apache reiniciado
- [ ] Backend Docker rodando (`docker-compose ps`)
- [ ] Testado: `http://SEU_IP/`
- [ ] Testado: `http://SEU_IP/api/health`
- [ ] Chat WebSocket funcionando

## 💡 Próximos Passos (Opcional)

1. **Domínio**: Registre um domínio e aponte para seu IP
2. **SSL**: Configure HTTPS com Let's Encrypt
3. **Firewall**: Configure UFW para permitir apenas portas 80, 443, 22
4. **Monitoramento**: Configure logs e alertas

```bash
# Exemplo firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```
