# admin_panel.py - VERSÃO 5.2 (Cadastro de Cliente CORRIGIDO)

from flask import Flask, render_template, request, redirect, url_for, flash, session
import database as db

admin_app = Flask(__name__)
admin_app.config['SECRET_KEY'] = 'uma_nova_chave_secreta_para_o_painel_de_admin'

# --- ROTAS DE AUTENTICAÇÃO DO ADMIN ---
@admin_app.route('/')
def index():
    return redirect(url_for('login'))

@admin_app.route('/login', methods=['GET', 'POST'])
def login():
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_user(username)

        if user and user['is_admin'] and db.check_password(password, user['password_hash']):
            session['admin_id'] = user['id']
            session['admin_username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais de administrador inválidas.', 'danger')

    return render_template('login.html')

# --- ROTA PRINCIPAL DO PAINEL DE ADMIN ---
@admin_app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # #############################################################
    # ### CORREÇÃO ESTÁ AQUI ###
    # #############################################################
    if request.method == 'POST':
        # Lógica para ADICIONAR um novo cliente
        razao_social = request.form.get('razao_social')
        cnpj = request.form.get('cnpj')
        email = request.form.get('email')
        telefone = request.form.get('telefone')
        responsavel = request.form.get('responsavel')
        username = request.form.get('username')
        password = request.form.get('password')

        if db.add_user(username, password, is_admin=False, razao_social=razao_social, cnpj=cnpj, email=email, telefone=telefone, responsavel=responsavel):
            flash(f"Cliente '{razao_social}' criado com sucesso!", 'success')
        else:
            flash(f"Erro: O nome de usuário '{username}' já existe.", 'danger')
        
        return redirect(url_for('dashboard')) # Redireciona para limpar o formulário

    # Lógica para exibir a página (método GET)
    clients = db.get_all_clients()
    return render_template('admin_dashboard.html', clients=clients)

# --- ROTAS DE AÇÕES (BLOQUEAR/DELETAR) ---
@admin_app.route('/toggle_status/<int:user_id>')
def toggle_status(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Lógica para buscar o status atual e inverter
    clients = db.get_all_clients()
    client_to_toggle = next((c for c in clients if c['id'] == user_id), None)
    if client_to_toggle:
        new_status = 'bloqueado' if client_to_toggle['status'] == 'ativo' else 'ativo'
        db.update_user_status(user_id, new_status)
        flash(f"Status do cliente alterado para '{new_status}'.", 'info')
    return redirect(url_for('dashboard'))

@admin_app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    db.delete_user(user_id)
    flash("Cliente deletado com sucesso.", 'warning')
    return redirect(url_for('dashboard'))

# --- ROTA DE LOGOUT ---
@admin_app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com segurança.', 'info')
    return redirect(url_for('login'))

# --- Bloco de Inicialização ---
if __name__ == '__main__':
    print("--- Iniciando o Painel do Administrador ---")
    print("Acesse em: http://127.0.0.1:5001")
    admin_app.run(debug=True, port=5001)