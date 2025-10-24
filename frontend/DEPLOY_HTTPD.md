# Deploy no Apache httpd (Amazon Linux / RHEL / CentOS)

## 📋 Sistema Detectado
- **Apache httpd** (não apache2)
- Diretório padrão: `/var/www/html`
- Configurações em: `/etc/httpd/conf.d/`

## 🚀 Deploy Completo

### 1. Build do Frontend

No seu computador local:

```bash
cd /home/daniel/interview-ai/frontend
npm run build
```

### 2. Copiar Build para o Servidor

Você tem 2 opções:

**Opção A: Copiar via SCP (do seu computador local)**
```bash
# Compactar
cd /home/daniel/interview-ai/frontend
tar -czf dist.tar.gz dist/

# Enviar para servidor (substitua sua_chave.pem e usuário)
scp -i sua_chave.pem dist.tar.gz ec2-user@52.52.87.55:/tmp/

# No servidor, descompactar
ssh -i sua_chave.pem ec2-user@52.52.87.55
cd /tmp
tar -xzf dist.tar.gz
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html
```

**Opção B: Build direto no servidor** (se tiver Node.js instalado)
```bash
# No servidor
cd /home/daniel/interview-ai/frontend
npm install
npm run build
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html
```

### 3. Copiar Configuração do Apache

```bash
# No servidor
sudo cp /home/daniel/interview-ai/frontend/httpd-config.conf /etc/httpd/conf.d/interview-ai.conf
```

### 4. Habilitar Módulos Necessários

Verifique se os módulos estão habilitados:

```bash
# Verificar módulos
httpd -M | grep -E 'rewrite|proxy|headers'

# Se não aparecerem, edite:
sudo vi /etc/httpd/conf.modules.d/00-base.conf
```

Certifique-se que estas linhas estão **descomentadas** (sem #):

```apache
LoadModule rewrite_module modules/mod_rewrite.so
LoadModule proxy_module modules/mod_proxy.so
LoadModule proxy_http_module modules/mod_proxy_http.so
LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so
LoadModule headers_module modules/mod_headers.so
LoadModule expires_module modules/mod_expires.so
LoadModule deflate_module modules/mod_deflate.so
```

### 5. Configurar SELinux (Importante!)

O SELinux pode bloquear o proxy. Configure:

```bash
# Permitir httpd fazer conexões de rede
sudo setsebool -P httpd_can_network_connect 1

# Permitir httpd fazer relay
sudo setsebool -P httpd_can_network_relay 1

# Verificar
getsebool -a | grep httpd
```

### 6. Configurar Firewall

```bash
# Verificar status
sudo firewall-cmd --state

# Se estiver rodando, adicionar regra:
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload

# Verificar
sudo firewall-cmd --list-all
```

### 7. Testar Configuração e Reiniciar

```bash
# Testar sintaxe
sudo httpd -t

# Se aparecer "Syntax OK":
sudo systemctl restart httpd

# Verificar status
sudo systemctl status httpd

# Habilitar para iniciar no boot
sudo systemctl enable httpd
```

### 8. Garantir Backend Rodando

```bash
cd /home/daniel/interview-ai/backend
docker-compose up -d

# Verificar
docker-compose ps
curl http://localhost:8000/health
```

### 9. Testar Aplicação

```bash
# Teste local no servidor
curl http://localhost/
curl http://localhost/api/health

# Teste do seu navegador
# http://52.52.87.55/
# http://52.52.87.55/api/health
```

## 🔍 Troubleshooting

### Erro 403 Forbidden

```bash
# Verificar permissões
ls -la /var/www/html/

# Corrigir
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html

# Verificar SELinux
sudo ausearch -m avc -ts recent
```

### Erro 502 Bad Gateway (API não responde)

```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Se não responder, iniciar Docker
cd /home/daniel/interview-ai/backend
docker-compose up -d

# Verificar SELinux
sudo setsebool -P httpd_can_network_connect 1
```

### WebSocket não conecta

```bash
# Verificar se módulo está carregado
httpd -M | grep proxy_wstunnel

# Se não aparecer, habilitar
sudo vi /etc/httpd/conf.modules.d/00-proxy.conf
# Descomentar: LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so

sudo systemctl restart httpd
```

### Verificar Logs

```bash
# Logs de erro
sudo tail -f /var/log/httpd/interview-ai-error.log

# Logs de acesso
sudo tail -f /var/log/httpd/interview-ai-access.log

# Logs gerais do httpd
sudo tail -f /var/log/httpd/error_log
```

### Página em branco

```bash
# Verificar se arquivos foram copiados
ls -la /var/www/html/

# Deve ter index.html e pasta assets/
# Se não tiver, copiar novamente o dist/
```

## 📝 Checklist Rápido

- [ ] `.env.production` configurado com IP 52.52.87.55
- [ ] `npm run build` executado
- [ ] Arquivos copiados para `/var/www/html/`
- [ ] Permissões ajustadas (apache:apache)
- [ ] Config copiada para `/etc/httpd/conf.d/interview-ai.conf`
- [ ] Módulos habilitados (rewrite, proxy, proxy_wstunnel)
- [ ] SELinux configurado (`httpd_can_network_connect`)
- [ ] Firewall configurado (porta 80)
- [ ] Configuração testada (`httpd -t`)
- [ ] httpd reiniciado
- [ ] Backend Docker rodando
- [ ] Testado: `http://52.52.87.55/`
- [ ] Testado: `http://52.52.87.55/api/health`

## 🎯 Comandos Resumidos

```bash
# Deploy completo (executar no servidor)
cd /home/daniel/interview-ai/frontend
npm run build
sudo rm -rf /var/www/html/*
sudo cp -r dist/* /var/www/html/
sudo chown -R apache:apache /var/www/html
sudo chmod -R 755 /var/www/html
sudo cp httpd-config.conf /etc/httpd/conf.d/interview-ai.conf
sudo setsebool -P httpd_can_network_connect 1
sudo httpd -t && sudo systemctl restart httpd
cd /home/daniel/interview-ai/backend
docker-compose up -d
```

## 🌐 Acesso Final

- **Frontend**: http://52.52.87.55/
- **API**: http://52.52.87.55/api/health
- **Docs**: http://52.52.87.55/api/docs

✅ Sistema pronto para uso!
