#!/usr/bin/env python3
"""
Script para limpar TODAS as tabelas de datasheets (sem confirmação)
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, get_db_cursor

def clean_all_datasheets():
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        # Lista e remove todas as tabelas datasheet_*
        cursor.execute("SHOW TABLES LIKE 'datasheet_%'")
        tables = cursor.fetchall()
        
        if not tables:
            print("✓ Banco já está limpo")
            return
        
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            print(f"✓ Removida: {table_name}")
        
        connection.commit()
        print(f"\n✓ Total: {len(tables)} tabela(s) removida(s)")
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    clean_all_datasheets()
