import asyncio
import sys
import os

# Adiciona o diretório app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.controllers.openai import generate_answer

async def test_query():
    print("=" * 80)
    print("TESTANDO QUERY: 'O que temos na base de dados?'")
    print("=" * 80)
    
    question = "O que temos na base de dados?"
    
    # Callback para mostrar progresso
    async def progress_callback(event_type: str, data: dict):
        print(f"\n[PROGRESS] {event_type}: {data}")
    
    # Executa a query
    result = await generate_answer(question, progress_callback=progress_callback)
    
    print("\n" + "=" * 80)
    print("RESULTADO FINAL:")
    print("=" * 80)
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}")
    print(f"Error Type: {result['error_type']}")
    print(f"\nQuestion: {result['question']}")
    print(f"\nSQL Query: {result['sql_query']}")
    print(f"\nSQL Explanation: {result['sql_explanation']}")
    print(f"\nTables Used: {result['tables_used']}")
    print(f"\nResults Count: {result['results_count']}")
    print(f"\nAvailable Tables: {result['available_tables']}")
    print(f"\nHumanized Response:")
    print(result['humanized_response'])
    print(f"\nRaw Results (first 5):")
    for i, row in enumerate(result['raw_results'][:5], 1):
        print(f"  {i}. {row}")
    
    print("\n" + "=" * 80)
    print(f"DEBUG - sql_query type: {type(result['sql_query'])}")
    print(f"DEBUG - sql_query value: '{result['sql_query']}'")
    print(f"DEBUG - sql_query is None: {result['sql_query'] is None}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_query())
