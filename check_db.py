# check_db.py
import sqlite3
from config import DATABASE_FILE

def inspect_users():
    print(f"--- Inspecionando o banco de dados: {DATABASE_FILE} ---")
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print("\nVerificando a tabela 'users'...")
        cursor.execute("SELECT id, username, is_admin, status FROM users")
        users = cursor.fetchall()
        
        if not users:
            print("ERRO: A tabela 'users' está vazia! Nenhum usuário encontrado.")
            print("Por favor, rode o script 'python3 setup.py' para criar o administrador.")
            return

        print("\nUsuários encontrados:")
        print("-" * 40)
        print(f"{'ID':<5} | {'Username':<20} | {'É Admin?':<10}")
        print("-" * 40)
        for user in users:
            # O valor de is_admin é 1 para True e 0 para False
            is_admin_text = "Sim" if user['is_admin'] == 1 else "Não"
            print(f"{user['id']:<5} | {user['username']:<20} | {is_admin_text:<10}")
        print("-" * 40)

    except sqlite3.OperationalError as e:
        print(f"\nERRO FATAL: Não foi possível ler a tabela 'users'. O banco de dados pode estar corrompido ou a tabela não existe.")
        print(f"Detalhe do erro: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
        print("\n--- Inspeção concluída. ---")

if __name__ == '__main__':
    inspect_users()