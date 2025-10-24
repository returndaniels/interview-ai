from openpyxl import load_workbook
from fastapi import UploadFile
from ..utils import sanitize_sql_name, get_sql_type
from ..database import get_db_connection, get_db_cursor, close_db_connection

import pandas as pd
import io

def get_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SHOW TABLES")
    all_tables = [table[0] for table in cursor.fetchall()]
    
    # Filtra apenas tabelas com prefixo datasheet_
    datasheet_tables = [t for t in all_tables if t.startswith('datasheet_')]
    
    cursor.close()
    connection.close()
    return datasheet_tables

def read_excel_in_chunks(file, batch_size=1000):
    """Lê um arquivo Excel em chunks de DataFrames."""
    wb = load_workbook(file, read_only=True)
    ws = wb.active
    rows = []
    headers = [cell.value for cell in next(ws.rows)]  # primeira linha
    for i, row in enumerate(ws.iter_rows(values_only=True)):
        if i == 0:
            continue  # já lemos o cabeçalho
        rows.append(row)
        if len(rows) == batch_size:
            yield pd.DataFrame(rows, columns=headers)
            rows = []
    if rows:
        yield pd.DataFrame(rows, columns=headers)


def create_table_from_dataframe(cursor, table_name, df):
    """ Cria uma tabela no banco de dados com base no DataFrame fornecido."""
    columns = df.columns
    types = df.dtypes
    sanitized_columns = [sanitize_sql_name(col) for col in columns]
    col_defs = ", ".join([f"`{col}` {get_sql_type(dtype)}" for col, dtype in zip(sanitized_columns, types)])
    create_table_query = f"CREATE TABLE IF NOT EXISTS `datasheet_{table_name}` ({col_defs});"
    cursor.execute(create_table_query)


async def import_excel_to_database(upload_file: UploadFile, table_name: str):
    """
    Importa um arquivo Excel (UploadFile do FastAPI) para o banco de dados MariaDB.
    
    Args:
        upload_file: Objeto UploadFile do FastAPI contendo o arquivo Excel
        table_name: Nome da tabela a ser criada
    
    Returns:
        dict: Informações sobre a importação
    """
    connection = None
    cursor = None
    
    try:
        # Lê o conteúdo do arquivo em memória
        contents = await upload_file.read()
        file_like = io.BytesIO(contents)
        
        # Conecta ao banco
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        total_rows = 0
        first_chunk = True
        
        # Processa o arquivo em chunks
        for chunk_df in read_excel_in_chunks(file_like):
            # Cria a tabela apenas no primeiro chunk
            if first_chunk:
                create_table_from_dataframe(cursor, table_name, chunk_df)
                connection.commit()
                first_chunk = False
            
            # Insere os dados
            sanitized_columns = [sanitize_sql_name(col) for col in chunk_df.columns]
            placeholders = ", ".join(["%s"] * len(sanitized_columns))
            columns_str = ", ".join([f"`{col}`" for col in sanitized_columns])
            prefixed_table_name = table_name if table_name.startswith('datasheet_') else f"datasheet_{table_name}"
            
            insert_query = f"INSERT INTO `{prefixed_table_name}` ({columns_str}) VALUES ({placeholders})"
            
            # Converte DataFrame para lista de tuplas
            data = [tuple(row) for row in chunk_df.values]
            cursor.executemany(insert_query, data)
            connection.commit()
            
            total_rows += len(chunk_df)

        _dict = {
            "success": True,
            "table_name": f"{prefixed_table_name}",
            "rows_imported": total_rows,
            "filename": upload_file.filename
        }
        message = f"Importação concluída: {total_rows} linhas inseridas na tabela '{prefixed_table_name}'"
        
        return _dict, message
        
    except Exception as e:
        if connection:
            connection.rollback()
        raise Exception(f"Erro ao importar Excel para banco: {str(e)}")
        
    finally:
        close_db_connection(connection, cursor)
