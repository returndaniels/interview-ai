from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .controllers import import_excel_to_database, get_tables, generate_answer, get_table_data_paginated, register_user, login_user, get_current_user
from .utils import sanitize_sql_name
from .database import get_db_connection, get_db_cursor
from pydantic import BaseModel
import os
import json

app = FastAPI(
    title="Interview AI - Datasheet Importer",
    description="API para importação de datasheets XLSX e XLS",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretório para uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Security
security = HTTPBearer()

# Modelos Pydantic
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str


# Dependency para autenticação
async def get_current_user_dep(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency que valida o token e retorna o usuário"""
    token = credentials.credentials
    username = get_current_user(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return username


@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "Interview AI - Datasheet Importer API",
        "status": "running",
        "docs": "/docs"
    }


@app.post("/auth/register")
async def register(request: RegisterRequest):
    """
    Registra um novo usuário
    
    Args:
        username: Nome de usuário único (uma única palavra)
        password: Senha (mínimo 6 caracteres)
    
    Returns:
        {
            "success": true,
            "message": "Usuário criado com sucesso",
            "token": "jwt_token",
            "username": "username"
        }
    """
    result = register_user(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@app.post("/auth/login")
async def login(request: LoginRequest):
    """
    Autentica um usuário
    
    Args:
        username: Nome de usuário
        password: Senha
    
    Returns:
        {
            "success": true,
            "message": "Login realizado com sucesso",
            "token": "jwt_token",
            "username": "username"
        }
    """
    result = login_user(request.username, request.password)
    
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result


@app.get("/auth/me")
async def get_me(current_user: str = Depends(get_current_user_dep)):
    """
    Retorna informações do usuário autenticado
    """
    return {
        "username": current_user
    }


@app.get("/health")
async def health_check():
    """Health check endpoint para Docker"""
    try:
        # Testa conexão com o banco
        connection = get_db_connection()
        connection.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status
    }


@app.post("/upload/excel")
async def upload_excel(
    file: UploadFile = File(...),
    table_name: str = None,
    current_user: str = Depends(get_current_user_dep)
):
    """
    Upload e importação de arquivos Excel (XLSX ou XLS) para o banco de dados
    
    Args:
        file: Arquivo Excel (.xlsx ou .xls)
        table_name: Nome da tabela (opcional, usa o nome do arquivo se não fornecido)
    """
    # Validar extensão do arquivo
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=400,
            detail="Formato de arquivo inválido. Use .xlsx ou .xls"
        )
    
    try:
        # Await na função assíncrona e passa o UploadFile completo
        result = await import_excel_to_database(file, table_name)
        
        return {
            "success": True,
            "message": f"Tabela '{result['table_name']}' importada com sucesso!",
            "table_name": result['table_name'],
            "rows_imported": result.get('rows_imported', 0)
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}"
        )


@app.get("/tables")
async def list_tables(current_user: str = Depends(get_current_user_dep)):
    """Lista todas as tabelas de datasheets (prefixo datasheet_)"""
    try:
        datasheet_tables = get_tables()
        
        return {
            "tables": datasheet_tables,
            "count": len(datasheet_tables)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar tabelas: {str(e)}"
        )


@app.get("/tables/{table_name}/data")
async def get_table_data(
    table_name: str,
    page: int = 1,
    page_size: int = 50,
    search: str = None,
    sort_by: str = None,
    sort_order: str = "asc",
    current_user: str = Depends(get_current_user_dep)
):
    """
    Retorna os dados de uma tabela com paginação e filtros
    
    Args:
        table_name: Nome da tabela (deve começar com datasheet_)
        page: Número da página (inicia em 1)
        page_size: Quantidade de registros por página (máximo 100)
        search: Termo de busca (busca em todas as colunas de texto)
        sort_by: Nome da coluna para ordenação
        sort_order: Ordem de classificação (asc ou desc)
    
    Returns:
        {
            "table_name": "datasheet_vendas",
            "data": [...],
            "pagination": {
                "page": 1,
                "page_size": 50,
                "total_records": 1000,
                "total_pages": 20
            },
            "columns": ["id", "nome", "valor"]
        }
    """
    
    # Usa o controller para buscar os dados
    success, result = get_table_data_paginated(
        table_name=table_name,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Se houve erro, lança HTTPException apropriada
    if not success:
        error_type = result.get("error_type", "internal")
        error_msg = result.get("error", "Erro desconhecido")
        
        # Define status code baseado no tipo de erro
        status_code_map = {
            "validation": 403,   # Forbidden (acesso negado)
            "not_found": 404,    # Not Found
            "database": 500,     # Internal Server Error
        }
        
        status_code = status_code_map.get(error_type, 500)
        raise HTTPException(status_code=status_code, detail=error_msg)
    
    # Retorna resultado de sucesso
    return result


@app.post("/query")
async def query_multi_table(
    question: str,
    current_user: str = Depends(get_current_user_dep)
):
    """
    Gera e executa uma query SQL baseada na pergunta do usuário
    Suporta MÚLTIPLAS TABELAS e JOINs automáticos
    
    Args:
        question: Pergunta em linguagem natural
    
    Returns:
        {
            "question": "pergunta original",
            "sql_query": "SELECT ...",
            "sql_explanation": "explicação da query",
            "tables_used": ["table1", "table2"],
            "results_count": 10,
            "humanized_response": "resposta em linguagem natural",
            "raw_results": [...] (primeiras 100 linhas)
        }
    """
    try:        
        # Processa a pergunta usando a função do controller
        result = await generate_answer(question)
        
        # Se houve erro, lança HTTPException apropriada
        if not result["success"]:
            error_type = result["error_type"]
            error_msg = result["error"]
            
            # Define status code baseado no tipo de erro
            status_code_map = {
                "validation": 400,  # Bad Request
                "execution": 500,   # Internal Server Error
                "database": 503,    # Service Unavailable
                "internal": 500     # Internal Server Error
            }
            
            status_code = status_code_map.get(error_type, 500)
            raise HTTPException(status_code=status_code, detail=error_msg)
        
        # Retorna resultado de sucesso (sem o campo "success" e "error")
        return {
            "question": result["question"],
            "sql_query": result["sql_query"],
            "sql_explanation": result["sql_explanation"],
            "tables_used": result["tables_used"],
            "results_count": result["results_count"],
            "humanized_response": result["humanized_response"],
            "raw_results": result["raw_results"],
            "available_tables": result["available_tables"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar pergunta: {str(e)}"
        )


@app.websocket("/ws/query")
async def query_multi_websocket(websocket: WebSocket):
    """
    WebSocket para queries SQL com suporte a MÚLTIPLAS TABELAS e JOINs
    
    Autenticação: Envie o token no primeiro mensagem como:
    {
        "token": "jwt_token",
        "question": "sua pergunta"
    }
    
    O cliente envia:
    {
        "question": "Qual a média de vendas por categoria?"
    }
    
    O servidor responde com:
    - type: "connected" -> conexão estabelecida
    - type: "loading_tables" -> carregando tabelas
    - type: "tables_loaded" -> tabelas carregadas
    - type: "building_context" -> construindo contexto
    - type: "generating_sql" -> gerando query SQL
    - type: "sql_generated" -> query SQL gerada
    - type: "executing_sql" -> executando query
    - type: "sql_executed" -> query executada
    - type: "humanizing" -> gerando resposta humanizada
    - type: "response" -> resposta final
    - type: "end" -> fim do processamento
    - type: "error" -> erro no processamento
    """
    await websocket.accept()
    
    authenticated = False
    current_user = None
    
    try:
        # Envia confirmação de conexão
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado! Envie sua pergunta com o token de autenticação."
        })
        
        # Loop de perguntas
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Verifica autenticação na primeira mensagem ou se token fornecido
            if not authenticated or "token" in message_data:
                token = message_data.get("token", "")
                if not token:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Token de autenticação não fornecido"
                    })
                    continue
                
                username = get_current_user(token)
                if not username:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Token inválido ou expirado"
                    })
                    await websocket.close()
                    return
                
                authenticated = True
                current_user = username
            
            question = message_data.get("question", "")
            
            if not question:
                await websocket.send_json({
                    "type": "error",
                    "message": "Pergunta não fornecida"
                })
                continue
            
            # Callback para enviar eventos de progresso
            async def progress_callback(event_type: str, data: dict):
                await websocket.send_json({
                    "type": event_type,
                    **data
                })
            
            # Usa generate_answer com callback de progresso
            result = await generate_answer(question, progress_callback=progress_callback)
            
            # Se houve erro
            if not result["success"]:
                await websocket.send_json({
                    "type": "error",
                    "error_type": result["error_type"],
                    "message": result["error"],
                    "sql_query": result["sql_query"]
                })
                await websocket.send_json({
                    "type": "end"
                })
                continue
            
            # Sucesso - envia resposta final
            # DEBUG: Log para verificar se sql_query está presente
            print(f"DEBUG - sql_query value: {result['sql_query']}")
            print(f"DEBUG - Full result: {result}")
            
            await websocket.send_json({
                "type": "response",
                "question": result["question"],
                "sql_query": result["sql_query"],
                "sql_explanation": result["sql_explanation"],
                "tables_used": result["tables_used"],
                "results_count": result["results_count"],
                "humanized_response": result["humanized_response"],
                "available_tables": result["available_tables"]
            })
            
            # Finaliza
            await websocket.send_json({
                "type": "end"
            })
    
    except WebSocketDisconnect:
        print("Cliente desconectado do query chat multi-tabela")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "error_type": "internal",
                "message": f"Erro interno: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
