# database.py - VERSÃO 5.2 (FINAL)

import sqlite3
import bcrypt
from config import DATABASE_FILE

# --- FUNÇÕES DE CONEXÃO ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# --- FUNÇÕES DE CRIAÇÃO DE TABELAS ---
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários (Admin e Clientes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0,
            razao_social TEXT,
            cnpj TEXT,
            email TEXT,
            telefone TEXT,
            responsavel TEXT,
            status TEXT NOT NULL DEFAULT 'ativo'
        )
    ''')

    # Tabela de Configurações dos Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            wordpress_url TEXT,
            instagram_user TEXT,
            instagram_pass TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Tabela de Logs de Execução
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            details TEXT
        )
    ''')

    # Tabela de Métricas de Notícias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER UNIQUE,
            title TEXT,
            link TEXT,
            score REAL,
            analysis_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de Publicações Realizadas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER UNIQUE,
            publish_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Banco de dados (Versão 5.2) verificado/criado com sucesso.")

# --- FUNÇÕES DE USUÁRIO ---
def add_user(username, password, is_admin=False, razao_social=None, cnpj=None, email=None, telefone=None, responsavel=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin, razao_social, cnpj, email, telefone, responsavel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, hashed_password, is_admin, razao_social, cnpj, email, telefone, responsavel)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_clients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_admin = 0 ORDER BY id DESC")
    clients = cursor.fetchall()
    conn.close()
    return clients

def update_user_status(user_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = ? WHERE id = ?", (new_status, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM client_configs WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# --- FUNÇÕES DE CONFIGURAÇÃO DO CLIENTE ---
def get_client_config(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM client_configs WHERE user_id = ?", (user_id,))
    config = cursor.fetchone()
    conn.close()
    return config

def save_client_config(user_id, wordpress_url, instagram_user, instagram_pass):
    """
    Insere uma nova configuração de cliente ou atualiza uma existente.
    Usa a sintaxe 'INSERT OR REPLACE' que é atômica e segura.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # O 'INSERT OR REPLACE' faz tudo em um só passo:
    # 1. Tenta inserir.
    # 2. Se a restrição UNIQUE (user_id) falhar, ele apaga o registro antigo e insere o novo.
    cursor.execute(
        """INSERT OR REPLACE INTO client_configs 
           (user_id, wordpress_url, instagram_user, instagram_pass) 
           VALUES (?, ?, ?, ?)""",
        (user_id, wordpress_url, instagram_user, instagram_pass)
    )
    
    conn.commit()
    conn.close()

# #############################################################
# ### NOVA FUNÇÃO ADICIONADA AQUI ###
# #############################################################
def get_all_active_client_configs():
    """Busca as configurações de todos os clientes que estão com status 'ativo'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # Junta a tabela de usuários com a de configurações
    cursor.execute('''
        SELECT 
            u.username,
            c.wordpress_url,
            c.instagram_user,
            c.instagram_pass
        FROM users u
        JOIN client_configs c ON u.id = c.user_id
        WHERE u.status = 'ativo' AND u.is_admin = 0
    ''')
    configs = cursor.fetchall()
    conn.close()
    return configs

# --- FUNÇÕES DE LOGS E MÉTRICAS ---
def log_event(event_type, details):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO execution_logs (event_type, details) VALUES (?, ?)", (event_type, details))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM execution_logs ORDER BY timestamp DESC LIMIT 100")
    logs = cursor.fetchall()
    conn.close()
    return logs

def get_all_news_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    # AQUI ESTÁ A MÁGICA: Renomeamos 'score' para 'engagement_score' na consulta
    cursor.execute("""
        SELECT 
            id, 
            post_id, 
            title, 
            link, 
            score AS engagement_score, 
            analysis_timestamp 
        FROM news_metrics 
        ORDER BY analysis_timestamp DESC 
        LIMIT 100
    """)
    metrics = cursor.fetchall()
    conn.close()
    return metrics

def add_news_metric(post_id, title, link, score):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO news_metrics (post_id, title, link, score) VALUES (?, ?, ?, ?)",
        (post_id, title, link, score)
    )
    conn.commit()
    conn.close()

def add_published_post(post_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO published_posts (post_id) VALUES (?)", (post_id,))
    conn.commit()
    conn.close()

def get_published_post_ids():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT post_id FROM published_posts")
    ids = [row['post_id'] for row in cursor.fetchall()]
    conn.close()
    return ids