from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import jwt
from ..database import get_db_connection, get_db_cursor, close_db_connection
import os

# Configurações JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 dias


def hash_password(password: str) -> str:
    """Hash de senha usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verifica e decodifica um token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


def create_users_table():
    """Cria a tabela de usuários se não existir"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_username (username)
            )
        """)
        connection.commit()
        
    finally:
        close_db_connection(connection, cursor)


def register_user(username: str, password: str) -> dict:
    """
    Registra um novo usuário
    
    Returns:
        dict com success, message, token (se sucesso) ou error
    """
    connection = None
    cursor = None
    
    try:
        # Validações
        if not username or not password:
            return {
                "success": False,
                "error": "Username e senha são obrigatórios"
            }
        
        # Username deve ser uma única palavra
        if ' ' in username or len(username.split()) > 1:
            return {
                "success": False,
                "error": "Username deve ser uma única palavra sem espaços"
            }
        
        if len(username) < 3:
            return {
                "success": False,
                "error": "Username deve ter pelo menos 3 caracteres"
            }
        
        if len(password) < 6:
            return {
                "success": False,
                "error": "Senha deve ter pelo menos 6 caracteres"
            }
        
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        # Verifica se usuário já existe
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return {
                "success": False,
                "error": "Username já está em uso"
            }
        
        # Hash da senha
        password_hash = hash_password(password)
        
        # Insere usuário
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        connection.commit()
        
        # Cria token
        access_token = create_access_token(data={"sub": username})
        
        return {
            "success": True,
            "message": "Usuário criado com sucesso",
            "token": access_token,
            "username": username
        }
        
    except Exception as e:
        if connection:
            connection.rollback()
        return {
            "success": False,
            "error": f"Erro ao registrar usuário: {str(e)}"
        }
        
    finally:
        close_db_connection(connection, cursor)


def login_user(username: str, password: str) -> dict:
    """
    Autentica um usuário
    
    Returns:
        dict com success, token (se sucesso) ou error
    """
    connection = None
    cursor = None
    
    try:
        if not username or not password:
            return {
                "success": False,
                "error": "Username e senha são obrigatórios"
            }
        
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        # Busca usuário
        cursor.execute(
            "SELECT username, password_hash FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()
        
        if not user:
            return {
                "success": False,
                "error": "Username ou senha incorretos"
            }
        
        # Verifica senha
        if not verify_password(password, user['password_hash']):
            return {
                "success": False,
                "error": "Username ou senha incorretos"
            }
        
        # Cria token
        access_token = create_access_token(data={"sub": user['username']})
        
        return {
            "success": True,
            "message": "Login realizado com sucesso",
            "token": access_token,
            "username": user['username']
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro ao fazer login: {str(e)}"
        }
        
    finally:
        close_db_connection(connection, cursor)


def get_current_user(token: str) -> Optional[str]:
    """
    Retorna o username do usuário autenticado pelo token
    
    Returns:
        username ou None se token inválido
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


# Inicializa a tabela de usuários ao importar o módulo
try:
    create_users_table()
except:
    pass  # Tabela será criada na primeira requisição
