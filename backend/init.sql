-- Script de inicialização do banco de dados
-- Este arquivo só é executado se o volume do MariaDB estiver vazio

CREATE DATABASE IF NOT EXISTS interview_ai;

-- Garante que o usuário tem todas as permissões
GRANT ALL PRIVILEGES ON interview_ai.* TO 'user'@'%';
FLUSH PRIVILEGES;

USE interview_ai;

-- Tabelas do sistema podem ser criadas aqui se necessário
-- Por exemplo, uma tabela de logs:
-- CREATE TABLE IF NOT EXISTS system_logs (
--     id INT AUTO_INCREMENT PRIMARY KEY,
--     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
--     level VARCHAR(20),
--     message TEXT
-- );
