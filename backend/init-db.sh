#!/bin/bash
# Script de inicialização do banco de dados

echo "Aguardando MariaDB iniciar..."
sleep 10

echo "Criando database se não existir..."
docker exec interview-ai-mariadb mariadb -u root -p${MARIADB_ROOT_PASSWORD} -e "CREATE DATABASE IF NOT EXISTS ${DATABASE_NAME};"

echo "Concedendo permissões ao usuário..."
docker exec interview-ai-mariadb mariadb -u root -p${MARIADB_ROOT_PASSWORD} -e "GRANT ALL PRIVILEGES ON ${DATABASE_NAME}.* TO '${MARIADB_USER}'@'%'; FLUSH PRIVILEGES;"

echo "✅ Banco de dados inicializado com sucesso!"
