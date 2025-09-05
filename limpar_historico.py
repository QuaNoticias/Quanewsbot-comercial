# limpar_historico.py
import sqlite3
from config import DATABASE_FILE

def limpar_tabela_publicados():
    """Apaga todos os registros da tabela 'published_posts'."""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        print("Conectado ao banco de dados...")
        
        # Apaga todos os dados da tabela
        cursor.execute("DELETE FROM published_posts")
        
        # Confirma a operação
        conn.commit()
        
        # Verifica quantos registros foram apagados
        changes = conn.total_changes
        print(f"Operação concluída. {changes} registros foram removidos da tabela 'published_posts'.")
        print("O histórico de publicações foi limpo com sucesso!")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

if __name__ == "__main__":
    print("--- INICIANDO LIMPEZA DO HISTÓRICO DE PUBLICAÇÕES ---")
    # Pede confirmação para evitar acidentes
    confirmacao = input("Você tem certeza que deseja apagar TODO o histórico de posts publicados? (s/n): ")
    if confirmacao.lower() == 's':
        limpar_tabela_publicados()
    else:
        print("Operação cancelada pelo usuário.")