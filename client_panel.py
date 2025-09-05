# client_panel.py - VERSÃO 2.1 (FINAL, COM FORMATAÇÃO DE DATA)

from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import database as db

client_app = Flask(__name__)
client_app.config['SECRET_KEY'] = 'uma_outra_chave_secreta_para_o_painel_do_cliente'

# --- ROTA DE LOGIN DO CLIENTE ---
@client_app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db.get_user(username)

        if user and user['status'] == 'ativo' and not user['is_admin'] and db.check_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas ou usuário inativo.', 'danger')

    return render_template('login.html')

# --- ROTA DO PAINEL DO CLIENTE ---
@client_app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    config = db.get_client_config(user_id)
    
    # --- LÓGICA DE FORMATAÇÃO DE DADOS ---
    
    # Formata os logs
    all_logs = db.get_all_logs()
    formatted_logs = []
    for log in all_logs:
        log_dict = dict(log)
        try:
            dt_obj = datetime.strptime(log_dict['timestamp'], '%Y-%m-%d %H:%M:%S')
            log_dict['timestamp_formatted'] = dt_obj.strftime('%d/%m/%Y %H:%M:%S')
        except (ValueError, TypeError, KeyError):
            log_dict['timestamp_formatted'] = log_dict.get('timestamp', 'Data inválida')
        formatted_logs.append(log_dict)

    # Formata as métricas
    all_metrics = db.get_all_news_metrics()
    published_ids = db.get_published_post_ids()
    
    metrics_with_status = []
    for metric in all_metrics:
        metric_dict = dict(metric)
        if metric_dict.get('post_id') in published_ids:
            metric_dict['published_status'] = 'Sim'
        else:
            metric_dict['published_status'] = 'Não'
        
        try:
            dt_obj = datetime.strptime(metric_dict['analysis_timestamp'], '%Y-%m-%d %H:%M:%S')
            metric_dict['analysis_timestamp_formatted'] = dt_obj.strftime('%d/%m/%Y %H:%M:%S')
        except (ValueError, TypeError, KeyError):
            metric_dict['analysis_timestamp_formatted'] = metric_dict.get('analysis_timestamp', 'Data inválida')
            
        metrics_with_status.append(metric_dict)
    
    return render_template('client_dashboard.html', config=config, logs=formatted_logs, metrics=metrics_with_status)


# --- ROTA PARA SALVAR CONFIGURAÇÕES ---
@client_app.route('/save_config', methods=['POST'])
def save_config():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    wordpress_url = request.form.get('wordpress_url')
    instagram_user = request.form.get('instagram_user')
    instagram_pass = request.form.get('instagram_pass')

    if instagram_pass:
        db.save_client_config(user_id, wordpress_url, instagram_user, instagram_pass)
        flash('Configurações salvas com sucesso!', 'success')
    else:
        flash('Configurações salvas (senha não foi alterada).', 'info')

    return redirect(url_for('dashboard'))

# --- ROTA DE LOGOUT ---
@client_app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado com segurança.', 'info')
    return redirect(url_for('login'))

# --- Bloco de Inicialização ---
if __name__ == '__main__':
    db.create_tables() 
    print("--- Iniciando o Painel do Cliente ---")
    print("Acesse em: http://127.0.0.1:5002")
    client_app.run(debug=True, port=5002)