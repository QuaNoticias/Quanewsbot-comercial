# ATUAL/create_admin.py - VERSÃO SEGURA E INTERATIVA

import database as db
import getpass  # Importa a biblioteca para esconder a senha

print("--- Criação de Usuário Administrador ---")
print("Por favor, insira as credenciais para o novo administrador.")

# Pede o nome de usuário
username = input("Nome de usuário: ")

# Pede a senha de forma segura (não mostra o que é digitado)
password = getpass.getpass("Senha: ")
password_confirm = getpass.getpass("Confirme a senha: ")

# Verifica se as senhas coincidem
if password != password_confirm:
    print("\n[ERRO] As senhas não coincidem. Operação cancelada.")
    exit() # Encerra o script

# Tenta adicionar o usuário ao banco de dados
success = db.add_user(
    username=username,
    password=password,
    is_admin=True, # Define este usuário como administrador
    razao_social="Administrador do Sistema",
    email=f"{username}@sistema.com"
)

if success:
    print(f"\n[SUCESSO] Usuário administrador '{username}' criado.")
    print("Você já pode fazer login no painel de administrador.")
else:
    print(f"\n[AVISO] O usuário administrador '{username}' já existe no banco de dados.")

print("\nEste script pode ser apagado após o uso.")