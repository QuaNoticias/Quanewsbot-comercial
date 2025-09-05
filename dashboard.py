# dashboard.py - VERSÃO 4.0 (ESTÁVEL)

from flask import Flask, render_template, request, redirect, url_for, session, flash
import database as db

dashboard_app = Flask(__name__)
dashboard_app.config['SECRET_KEY'] = 'a_chave_secreta_da_v1_que_funciona'

# --- ROTAS DE AUTENTICAÇÃO ---
@dashboard_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user(username)
        
        if user and db.check_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
            
    return render_template('login.html')

@dashboard_app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com segurança.', 'info')
    return redirect(url_for('login'))

# --- ROTA PRINCIPAL ---
@dashboard_app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

# --- ROTA DO PAINEL ---
@dashboard_app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_logs = db.get_execution_logs(session['user_id'], limit=100)
    user_metrics = db.get_all_news_metrics(session['user_id'])
    
    return render_template('dashboard_content.html', logs=user_logs, metrics=user_metrics)

# --- Bloco de Inicialização ---
if __name__ == '__main__':
    print("Iniciando o Painel Web (Versão Estável)...")
    dashboard_app.run(debug=True, port=5001)