from openai import OpenAI
from dotenv import load_dotenv
from ..database import get_db_connection
import os 
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def validate_sql_query(query: str) -> tuple[bool, str]:
    """
    Valida se a query SQL é segura (somente SELECT em tabelas datasheet_)
    
    Args:
        query: Query SQL a ser validada
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Remove comentários e espaços extras
    clean_query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL)
    clean_query = clean_query.strip().upper()
    
    # Lista de comandos proibidos
    forbidden_commands = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE',
        'EXEC', 'EXECUTE', 'CALL', 'LOAD', 'INTO OUTFILE',
        'INTO DUMPFILE', 'LOAD_FILE', 'SYSTEM'
    ]
    
    # Verifica se contém comandos proibidos
    for forbidden in forbidden_commands:
        if forbidden in clean_query:
            return False, f"Query contém comando proibido: {forbidden}"
    
    # Deve começar com SELECT
    if not clean_query.startswith('SELECT'):
        return False, "Query deve começar com SELECT"
    
    # Remove ponto-e-vírgula final antes de validar
    clean_query_no_semicolon = clean_query.rstrip(';').strip()
    
    # Verifica se tem múltiplos statements (mais de um ;)
    if ';' in clean_query_no_semicolon:
        return False, "Múltiplas queries não são permitidas"
    
    # SEGURANÇA: Verifica se só acessa tabelas com prefixo datasheet_
    # Extrai nomes de tabelas da query (após FROM e JOIN)
    table_pattern = r'(?:FROM|JOIN)\s+`?(\w+)`?'
    tables_in_query = re.findall(table_pattern, clean_query, re.IGNORECASE)
    
    for table in tables_in_query:
        if not table.lower().startswith('datasheet_'):
            return False, f"Acesso negado à tabela '{table}'. Apenas tabelas com prefixo 'datasheet_' são permitidas."
    
    return True, ""


async def generate_sql_query(user_question: str, database_context: dict) -> dict:
    """
    Gera uma query SQL SELECT baseada na pergunta do usuário
    Suporta múltiplas tabelas e JOINs
    
    Args:
        user_question: Pergunta do usuário
        database_context: Contexto do banco (todas as tabelas, colunas, previews)
    
    Returns:
        dict: {
            "query": "SELECT ...",
            "explanation": "Explicação da query",
            "tables_used": ["table1", "table2"],
            "error": None ou mensagem de erro
        }
    """
    tables_info = database_context.get('tables', {})
    
    # Prepara contexto de todas as tabelas
    tables_description = ""
    for table_name, info in tables_info.items():
        columns = info.get('columns', [])
        total_rows = info.get('total_rows', 0)
        preview = info.get('preview', [])
        
        tables_description += f"""
Tabela: `{table_name}`
- Colunas: {', '.join([f'`{col}`' for col in columns])}
- Total de linhas: {total_rows}
- Preview: {preview[:2]}

"""
    
    # Prompt para gerar SQL
    system_prompt = f"""Você é um especialista em SQL que gera queries SELECT seguras para MySQL/MariaDB.

IMPORTANTE - SEGURANÇA:
- Gere APENAS queries SELECT
- NUNCA use INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ou qualquer comando que modifique dados
- NUNCA use procedimentos armazenados, EXEC, CALL ou funções que alterem estado
- ACESSE APENAS tabelas com prefixo 'datasheet_' - NUNCA acesse outras tabelas do banco
- Todas as tabelas disponíveis começam com 'datasheet_' - use apenas estas
- GERE APENAS UMA ÚNICA QUERY - NUNCA múltiplas queries separadas por ponto e vírgula

TABELAS DISPONÍVEIS (todas começam com 'datasheet_'):
{tables_description}

INSTRUÇÕES:
- Use APENAS as tabelas listadas acima (todas com prefixo datasheet_)
- Gere APENAS UMA query SQL - se precisar consultar múltiplas tabelas sem relacionamento, use UNION ALL
- Use JOINs quando necessário para cruzar dados de múltiplas tabelas com relacionamento
- Identifique automaticamente as colunas de relacionamento para JOINs
- Use aliases de tabela (t1, t2, etc) para melhor legibilidade
- Use funções de agregação quando apropriado (COUNT, SUM, AVG, MAX, MIN)
- Use GROUP BY, ORDER BY, HAVING quando necessário
- Use LIMIT para prevenir retornos muito grandes (máximo 1000 linhas)
- Retorne APENAS a query SQL, sem explicações adicionais no corpo da query
- Use backticks (`) para nomes de tabelas e colunas
- Para visualizar dados de múltiplas tabelas independentes, use UNION ALL com uma coluna indicando a tabela
"""

    user_prompt = f"""Gere uma query SQL SELECT para responder a seguinte pergunta:

"{user_question}"

IMPORTANTE:
- Retorne APENAS UMA ÚNICA QUERY SQL - nunca múltiplas queries separadas
- Se precisar consultar múltiplas tabelas sem relacionamento, use UNION ALL
- Não use markdown, não use ```sql```, não adicione explicações na query
- A query deve ser executável diretamente no MySQL/MariaDB
- Se precisar cruzar tabelas, identifique as colunas de relacionamento e use JOIN apropriado
- Se não souber qual coluna usar para JOIN, tente identificar colunas com nomes semelhantes ou use CROSS JOIN se apropriado
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,  # Baixa temperatura para respostas mais determinísticas
            max_tokens=800
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Remove markdown se presente
        sql_query = re.sub(r'^```sql\s*', '', sql_query)
        sql_query = re.sub(r'^```\s*', '', sql_query)
        sql_query = re.sub(r'\s*```$', '', sql_query)
        sql_query = sql_query.strip()
        
        # Valida a query
        is_valid, error_msg = validate_sql_query(sql_query)
        
        if not is_valid:
            return {
                "sql_query": sql_query,
                "explanation": None,
                "tables_used": [],
                "error": f"Query inválida ou insegura: {error_msg}"
            }
        
        # Identifica tabelas usadas na query
        tables_used = []
        for table_name in tables_info.keys():
            if f"`{table_name}`" in sql_query or f" {table_name} " in sql_query.upper():
                tables_used.append(table_name)
        
        # Gera explicação da query
        explanation_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você explica queries SQL de forma simples e clara, mencionando as tabelas envolvidas e o que está sendo calculado."},
                {"role": "user", "content": f"Explique em 1-2 frases o que esta query faz:\n{sql_query}"}
            ],
            temperature=0.5,
            max_tokens=200
        )
        
        explanation = explanation_response.choices[0].message.content.strip()
        
        return {
            "query": sql_query,
            "explanation": explanation,
            "tables_used": tables_used,
            "error": None
        }
        
    except Exception as e:
        return {
            "query": None,
            "explanation": None,
            "tables_used": [],
            "error": f"Erro ao gerar query: {str(e)}"
        }


async def humanize_query_results(user_question: str, sql_query: str, results: list, database_context: dict = None) -> str:
    """
    Transforma os resultados da query SQL em uma resposta humanizada
    
    Args:
        user_question: Pergunta original do usuário
        sql_query: Query SQL executada
        results: Resultados da query (lista de dicts)
        database_context: Contexto do banco (opcional)
    
    Returns:
        str: Resposta humanizada
    """
    # Prepara contexto dos resultados
    result_summary = f"""
Query executada: {sql_query}
Número de resultados: {len(results)}

Resultados (máximo 100 primeiras linhas):
{results[:100]}
"""

    system_prompt = """Você é um assistente especializado em análise de dados que transforma resultados de queries SQL em respostas claras e humanizadas.

DIRETRIZES:
- Seja claro e objetivo
- Use linguagem natural e acessível
- Destaque insights importantes
- Se houver muitos resultados, resuma os principais pontos
- Use formatação markdown quando apropriado (tabelas, listas, etc)
- Seja preciso com números e estatísticas
- Se a query envolver múltiplas tabelas (JOINs), explique o contexto do cruzamento de dados
"""

    user_prompt = f"""Pergunta original do usuário: "{user_question}"

{result_summary}

Por favor, transforme esses resultados em uma resposta clara e humanizada para o usuário.
Se os resultados formarem uma tabela pequena (até 20 linhas), mostre em formato de tabela markdown.
Se forem estatísticas ou agregações, apresente de forma narrativa com destaques."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        # Fallback: retorna resultados formatados de forma básica
        return f"Encontrei {len(results)} resultado(s):\n\n{results[:10]}"


async def generate_answer(question: str, progress_callback=None) -> dict:
    """
    Processa uma pergunta do usuário e gera resposta com base nos dados
    Busca automaticamente todas as tabelas datasheet_ disponíveis
    
    Args:
        question: Pergunta do usuário em linguagem natural
        progress_callback: Função async opcional para enviar eventos de progresso
                          Recebe (event_type: str, data: dict)
    
    Returns:
        dict: {
            "success": bool,
            "error": str | None,
            "error_type": str | None,  # "validation", "execution", "database"
            "question": str,
            "sql_query": str | None,
            "sql_explanation": str | None,
            "tables_used": list,
            "results_count": int,
            "humanized_response": str | None,
            "raw_results": list,
            "available_tables": list
        }
    """
    connection = None
    cursor = None
    
    async def emit_progress(event_type: str, data: dict):
        """Helper para emitir eventos de progresso se callback fornecido"""
        if progress_callback:
            await progress_callback(event_type, data)
    
    try:
        await emit_progress("loading_tables", {"message": "Carregando tabelas disponíveis..."})
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Busca TODAS as tabelas disponíveis
        cursor.execute("SHOW TABLES")
        all_tables = [table[list(table.keys())[0]] for table in cursor.fetchall()]
            
        # FILTRO DE SEGURANÇA: Apenas tabelas com prefixo datasheet_
        datasheet_tables = [t for t in all_tables if t.startswith('datasheet_')]
        
        if not datasheet_tables:
            return {
                "success": False,
                "error": "Nenhuma tabela de datasheet encontrada. Importe arquivos Excel primeiro.",
                "error_type": "database",
                "question": question,
                "sql_query": None,
                "sql_explanation": None,
                "tables_used": [],
                "results_count": 0,
                "humanized_response": None,
                "raw_results": [],
                "available_tables": []
            }
        
        await emit_progress("tables_loaded", {
            "available_tables": datasheet_tables,
            "count": len(datasheet_tables)
        })
        
        # Prepara contexto de TODAS as tabelas de datasheet
        await emit_progress("building_context", {"message": "Analisando estrutura das tabelas..."})
        database_context = {"tables": {}}

        for table_name in datasheet_tables:
            try:
                # Busca estrutura da tabela
                cursor.execute(f"DESCRIBE `{table_name}`")
                columns = [col['Field'] for col in cursor.fetchall()]
                
                # Conta linhas
                cursor.execute(f"SELECT COUNT(*) as count FROM `{table_name}`")
                total_rows = cursor.fetchone()['count']
                
                # Preview dos dados
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT 3")
                preview_data = cursor.fetchall()
                
                database_context["tables"][table_name] = {
                    "columns": columns,
                    "total_rows": total_rows,
                    "preview": preview_data
                }
            except Exception as e:
                # Se falhar em uma tabela específica, continua com as outras
                print(f"Aviso: Erro ao carregar tabela {table_name}: {str(e)}")
                continue
        
        # Verifica se conseguiu carregar pelo menos uma tabela
        if not database_context["tables"]:
            return {
                "success": False,
                "error": "Nenhuma tabela disponível para consulta",
                "error_type": "database",
                "question": question,
                "sql_query": None,
                "sql_explanation": None,
                "tables_used": [],
                "results_count": 0,
                "humanized_response": None,
                "raw_results": [],
                "available_tables": datasheet_tables
            }
        
        # Gera a query SQL usando IA
        await emit_progress("generating_sql", {"message": "Gerando query SQL com IA..."})
        sql_result = await generate_sql_query(question, database_context)
        
        if sql_result['error']:
            return {
                "success": False,
                "error": sql_result['error'],
                "error_type": "validation",
                "question": question,
                "sql_query": sql_result.get('query'),
                "sql_explanation": None,
                "tables_used": [],
                "results_count": 0,
                "humanized_response": None,
                "raw_results": [],
                "available_tables": datasheet_tables
            }
        
        sql_query = sql_result['query']
        sql_explanation = sql_result['explanation']
        tables_used = sql_result['tables_used']
        
        await emit_progress("sql_generated", {
            "sql_query": sql_query,
            "explanation": sql_explanation,
            "tables_used": tables_used
        })
        
        # Executa a query
        await emit_progress("executing_sql", {"message": "Executando query no banco de dados..."})
        try:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            await emit_progress("sql_executed", {
                "results_count": len(results),
                "preview": results[:5]
            })
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro ao executar query SQL: {str(e)}",
                "error_type": "execution",
                "question": question,
                "sql_query": sql_query,
                "sql_explanation": sql_explanation,
                "tables_used": tables_used,
                "results_count": 0,
                "humanized_response": None,
                "raw_results": [],
                "available_tables": datasheet_tables
            }
        
        # Humaniza os resultados
        await emit_progress("humanizing", {"message": "Gerando resposta humanizada..."})
        humanized = await humanize_query_results(
            user_question=question,
            sql_query=sql_query,
            results=results,
            database_context=database_context
        )
        
        return {
            "success": True,
            "error": None,
            "error_type": None,
            "question": question,
            "sql_query": sql_query,
            "sql_explanation": sql_explanation,
            "tables_used": tables_used,
            "results_count": len(results),
            "humanized_response": humanized,
            "raw_results": results[:100],
            "available_tables": datasheet_tables
        }
        
    except Exception as e:
        # Erro inesperado/genérico
        return {
            "success": False,
            "error": f"Erro interno ao processar pergunta: {str(e)}",
            "error_type": "internal",
            "question": question,
            "sql_query": None,
            "sql_explanation": None,
            "tables_used": [],
            "results_count": 0,
            "humanized_response": None,
            "raw_results": [],
            "available_tables": []
        }
    
    finally:
        # Garante que a conexão seja fechada
        if cursor:
            cursor.close()
        if connection:
            connection.close()