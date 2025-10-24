#!/usr/bin/env python3
"""
Script para limpar as tabelas de datasheets do banco de dados
"""
import sys
import os

# Adiciona o diretório app ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db_connection, get_db_cursor

def clean_datasheet_tables():
    """Remove todas as tabelas com prefixo datasheet_"""
    connection = None
    cursor = None
    
    try:
        connection = get_db_connection()
        cursor = get_db_cursor(connection)
        
        # Lista todas as tabelas
        cursor.execute("SHOW TABLES LIKE 'datasheet_%'")
        tables = cursor.fetchall()
        
        if not tables:
            print("✓ Nenhuma tabela de datasheet encontrada")
            return
        
        print(f"Encontradas {len(tables)} tabelas de datasheet:")
        for table in tables:
            table_name = list(table.values())[0]
            print(f"  - {table_name}")
        
        # Confirma
        response = input("\nDeseja remover todas essas tabelas? (s/N): ")
        if response.lower() != 's':
            print("Operação cancelada")
            return
        
        # Remove as tabelas
        dropped = 0
        for table in tables:
            table_name = list(table.values())[0]
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            print(f"✓ Removida: {table_name}")
            dropped += 1
        
        connection.commit()
        print(f"\n✓ {dropped} tabela(s) removida(s) com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro ao limpar tabelas: {e}")
        if connection:
            connection.rollback()
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == "__main__":
    clean_datasheet_tables()
