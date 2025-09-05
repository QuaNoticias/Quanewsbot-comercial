# teste_import.py

print("Iniciando o teste de importação...")

try:
    import database
    print("SUCESSO: O módulo 'database' foi importado corretamente.")
    
    # Vamos tentar usar uma função dele para ter certeza
    database.get_db_connection()
    print("SUCESSO: A função 'get_db_connection' foi chamada.")
    
except ModuleNotFoundError:
    print("FALHA CATASTRÓFICA: ModuleNotFoundError. O Python não consegue encontrar 'database.py'.")
except Exception as e:
    print(f"FALHA INESPERADA: Ocorreu um erro durante a importação ou uso: {e}")

print("Teste de importação concluído.")