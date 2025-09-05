# setup.py - VERSÃO 3.0 (Cria Admin para Sistema Multi-Usuário)

import database
import getpass
import os

DB_FILE = "agente.db"

def main():
    print("--- SCRIPT DE INSTALAÇÃO DO ADMINISTRADOR (V3.0) ---")

    if os.path.exists(DB_FILE):
        # Apaga sem perguntar para garantir que estamos recomeçando
        os.remove(DB_FILE)
        print(f"AVISO: O banco de dados '{DB_FILE}' antigo foi removido para garantir a nova estrutura.")

    print("\n[PASSO 1/2] Criando tabelas com estrutura multi-usuário...")
    database.create_tables()
    
    print("\n[PASSO 2/2] Criando sua conta de Administrador...")
    admin_username = input("  - Escolha um nome de usuário para você: ")
    admin_password = getpass.getpass("  - Digite sua senha: ")

    try:
        # Usa a função add_user com o parâmetro is_admin=True
        database.add_user(username=admin_username, password=admin_password, is_admin=True)
        print(f"\n--- SUCESSO! Administrador '{admin_username}' criado. ---")
        print("Você já pode iniciar o painel de administração com 'python3 admin_panel.py'.")
    except Exception as e:
        print(f"\nERRO: Não foi possível criar o administrador. Motivo: {e}")

if __name__ == '__main__':
    main()