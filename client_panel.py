# client_panel.py - VERSÃO 3.0 COM ABAS E GRÁFICOS

from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
from datetime import timedelta
import database as db
from datetime import datetime
from pytz import timezone 

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]CLIENTE/'
app.permanent_session_lifetime = timedelta(minutes=60)

# Rota de Login (APENAS PARA CLIENTE)
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.get_user(username)

        if user and db.check_password(password, user['password_hash']) and not user['is_admin']:
            session.permanent = True
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciais inválidas ou usuário não é um cliente.', 'danger')
            return redirect(url_for('login'))
    
    # Redireciona para o dashboard se já estiver logado
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    return render_template('login_cliente.html') # Usando um template de login separado para evitar conflitos

# Filtro de data (sem alterações)
@app.template_filter('localtz')
def local_time_filter(utc_dt_str):
    if not utc_dt_str: return ""
    try:
        utc_dt = datetime.strptime(utc_dt_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
        utc_dt = timezone('UTC').localize(utc_dt)
        local_tz = timezone('America/Cuiaba')
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime('%d/%m/%Y %H:%M:%S')
    except (ValueError, TypeError):
        return utc_dt_str

# Rota principal do Painel do Cliente (muito mais simples agora)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Apenas renderiza o "esqueleto" da página. Os dados virão da API.
    return render_template('client_dashboard.html')

# Rota para Salvar Configurações (sem alterações)
# Rota para Salvar Configurações
@app.route('/save_config', methods=['POST'])
def save_config():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Coleta os dados antigos
    wordpress_url = request.form.get('wordpress_url')
    instagram_user = request.form.get('instagram_user')
    instagram_pass = request.form.get('instagram_pass')
    report_email = request.form.get('report_email')

    # --- CORREÇÃO ESTÁ AQUI ---
    # Coleta os dados dos novos campos
    enable_remix_task = 'enable_remix_task' in request.form
    remix_niche_keywords = request.form.get('remix_niche_keywords', '')
    
    # Chama a função no banco de dados com TODOS os argumentos
    db.save_client_config(
        user_id, 
        wordpress_url, 
        instagram_user, 
        instagram_pass, 
        report_email,
        enable_remix_task,
        remix_niche_keywords
    )
    # --- FIM DA CORREÇÃO ---

    db.log_event('Configurações Salvas', f'Cliente {session["username"]} salvou suas configurações.')
    flash('Suas configurações foram salvas com sucesso!', 'success')
    
    return redirect (url_for('dashboard'))

# Rota de Logout (sem alterações)
@app.route('/logout')
def logout():
    session.clear()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))

# --- NOVA API PARA ALIMENTAR O PAINEL DO CLIENTE ---
@app.route('/api/client_panel_data')
def client_panel_data_api():
    if 'user_id' not in session:
        return jsonify({"error": "Não autorizado"}), 401

    user_id = session['user_id']
    username = session['username']

    # Dados para a aba "Desempenho"
    all_client_logs = db.get_logs_by_username(username)
    excluded_event_types = ['Novo Cliente Cadastrado', 'Coleta de Stats']
    performance_logs = [dict(log) for log in all_client_logs if log['event_type'] not in excluded_event_types]
    
    # Dados para a aba "Resultados"
    growth_data = db.get_user_instagram_growth(user_id)
    summary = db.get_user_performance_summary(user_id)

    # Dados para a aba "Configurações"
    config = db.get_client_config(user_id)

    # Monta a resposta completa
    response = {
        'performance': {
            'logs': performance_logs
        },
        'results': {
            'summary_cards': summary,
            'growth_chart': {
                'labels': [row['collection_date'] for row in growth_data],
                'data': [row['followers_count'] for row in growth_data]
            }
        },
        'config': dict(config) if config else {}
    }
    return jsonify(response)

if __name__ == '__main__':
    print("--- Iniciando o Painel do CLIENTE (v3.0) ---")
    print("Acesse em: http://127.0.0.1:5004")
    app.run(port=5004, debug=True)