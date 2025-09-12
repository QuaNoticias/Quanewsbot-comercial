# ATUAL/admin_panel.py - VERSÃO COMPLETA E FINAL

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import timedelta
import logging
import database as db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.permanent_session_lifetime = timedelta(minutes=30)

db.create_tables()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user(username)

        if user and db.check_password(password, user['password_hash']) and user['is_admin']:
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais de administrador inválidas.', 'danger')
            return redirect(url_for('login'))
    return render_template('login_admin.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or not db.get_user(session['username'])['is_admin']:
        return redirect(url_for('login'))
    
    clients = db.get_all_clients()
    return render_template('admin_dashboard.html', clients=clients)

@app.route('/add_client', methods=['POST'])
def add_client():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = request.form['username']
    password = request.form['password']
    razao_social = request.form['razao_social']
    cnpj = request.form['cnpj']
    email = request.form['email']
    telefone = request.form['telefone']
    responsavel = request.form['responsavel']

    if db.add_user(username, password, is_admin=False, razao_social=razao_social, cnpj=cnpj, email=email, telefone=telefone, responsavel=responsavel):
        db.log_event('Novo Cliente Cadastrado', message=f'Admin {session["username"]} cadastrou o cliente {username}.')
        flash(f'Cliente "{username}" cadastrado com sucesso!', 'success')
    else:
        flash(f'Erro: Nome de usuário "{username}" já existe.', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/update_client_status/<int:user_id>')
def update_client_status_route(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.get_user_by_id(user_id)
    if user:
        new_status = 'inativo' if user['status'] == 'ativo' else 'ativo'
        db.update_user_status(user_id, new_status)
        db.log_event('Status Alterado', message=f'Status do cliente ID {user_id} alterado para {new_status}.')
        flash(f'Status do cliente alterado para {new_status}.', 'info')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_client', methods=['POST'])
def delete_client_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = request.json.get('user_id')
    db.delete_user(user_id)
    db.log_event('Cliente Deletado', message=f'Cliente com ID {user_id} foi deletado.')
    return {'success': True, 'message': 'Cliente deletado com sucesso.'}

@app.route('/metrics_dashboard')
def metrics_dashboard():
    if 'user_id' not in session or not db.get_user(session['username'])['is_admin']:
        return redirect(url_for('login'))
    return render_template('metrics_dashboard.html')

@app.route('/api/dashboard_charts')
def api_dashboard_charts():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401
        
    agent_runs = db.get_agent_start_logs()
    error_logs = db.get_error_logs()
    success_posts = db.get_all_published_posts()
    
    response_data = {
        'agent_health': {
            'labels': ['Execuções do Agente', 'Publicações com Sucesso', 'Erros Críticos'],
            'data': [len(agent_runs), len(success_posts), len(error_logs)]
        }
    }
    return jsonify(response_data)

@app.route('/add_topics', methods=['POST'])
def add_topics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    topics_raw = request.form.get('topics')
    if topics_raw:
        topics_list = [topic.strip() for topic in topics_raw.splitlines() if topic.strip()]
        db.add_remix_topics(topics_list)
        flash(f'{len(topics_list)} tópicos adicionados com sucesso!', 'success')

    return redirect(url_for('admin_dashboard'))

@app.route('/client_dashboard/<int:user_id>')
def client_dashboard(user_id):
    if 'user_id' not in session or not db.get_user(session['username'])['is_admin']:
        return redirect(url_for('login'))

    cliente = db.get_user_by_id(user_id)
    
    if not cliente:
        flash('Cliente não encontrado.', 'danger')
        return redirect(url_for('admin_dashboard'))

    return render_template('client_dashboard_admin_view.html', cliente=cliente)

@app.route('/api/client_dashboard_charts/<int:user_id>')
def api_client_dashboard_charts(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 401

    client = db.get_user_by_id(user_id)
    if not client:
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    username = client['username']

    success_logs = db.get_success_logs_for_client(username)
    error_logs = db.get_error_logs_for_client(username)
    
    response_data = {
        'agent_performance': {
            'labels': ['Publicações com Sucesso', 'Falhas na Publicação'],
            'data': [len(success_logs), len(error_logs)]
        }
    }
    return jsonify(response_data)

if __name__ == '__main__':
    print("--- Iniciando o Painel do ADMINISTRADOR (VERSÃO ATUAL) ---")
    print("Acesse em: http://127.0.0.1:5003")
    app.run(port=5003, debug=True)