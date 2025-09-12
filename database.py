# ATUAL/database.py - VERSÃO COMPLETA E FINAL

import sqlite3
import bcrypt

DATABASE_NAME = "agente.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'ativo',
            razao_social TEXT,
            cnpj TEXT,
            email TEXT,
            telefone TEXT,
            responsavel TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client_configs (
            user_id INTEGER PRIMARY KEY,
            wordpress_url TEXT,
            instagram_user TEXT,
            instagram_pass TEXT,
            report_email TEXT,
            enable_remix_task BOOLEAN DEFAULT 0,
            remix_niche_keywords TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS published_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            post_id INTEGER NOT NULL,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, post_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            message TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT,
            link TEXT,
            score REAL,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, post_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instagram_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            followers INTEGER,
            following INTEGER,
            media_count INTEGER,
            collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, collection_date),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remix_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            is_used BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(username, password, is_admin=False, **kwargs):
    conn = get_db_connection()
    try:
        password_bytes = password.encode('utf-8')
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin, razao_social, cnpj, email, telefone, responsavel) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (username, hashed_password_str, is_admin, kwargs.get('razao_social'), kwargs.get('cnpj'), kwargs.get('email'), kwargs.get('telefone'), kwargs.get('responsavel'))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return user

def check_password(password, hashed_password_from_db):
    password_bytes = password.encode('utf-8')
    hashed_password_bytes = hashed_password_from_db.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def get_all_clients():
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM users WHERE is_admin = 0 ORDER BY id').fetchall()
    conn.close()
    return clients

def update_user_status(user_id, new_status):
    conn = get_db_connection()
    conn.execute('UPDATE users SET status = ? WHERE id = ?', (new_status, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_client_config(user_id, wordpress_url, instagram_user, instagram_pass, report_email, enable_remix_task, remix_niche_keywords):
    conn = get_db_connection()
    conn.execute(
        "INSERT OR REPLACE INTO client_configs (user_id, wordpress_url, instagram_user, instagram_pass, report_email, enable_remix_task, remix_niche_keywords) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, wordpress_url, instagram_user, instagram_pass, report_email, enable_remix_task, remix_niche_keywords)
    )
    conn.commit()
    conn.close()

def get_client_config(user_id):
    conn = get_db_connection()
    config = conn.execute('SELECT * FROM client_configs WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return config

def get_all_active_client_configs():
    conn = get_db_connection()
    query = """
        SELECT u.id, u.username, c.wordpress_url, c.instagram_user, c.instagram_pass, c.report_email, c.enable_remix_task, c.remix_niche_keywords
        FROM users u
        JOIN client_configs c ON u.id = c.user_id
        WHERE u.status = 'ativo'
    """
    clients = conn.execute(query).fetchall()
    conn.close()
    return clients

def log_event(event_type, message):
    conn = get_db_connection()
    conn.execute("INSERT INTO event_logs (event_type, message) VALUES (?, ?)", (event_type, message))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM event_logs ORDER BY timestamp DESC').fetchall()
    conn.close()
    return logs

def add_news_metric(user_id, post_id, title, link, score):
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO news_metrics (user_id, post_id, title, link, score) VALUES (?, ?, ?, ?, ?)",
        (user_id, post_id, title, link, score)
    )
    conn.commit()
    conn.close()

def get_all_news_metrics():
    conn = get_db_connection()
    metrics = conn.execute('SELECT * FROM news_metrics ORDER BY analysis_date DESC').fetchall()
    conn.close()
    return metrics

def add_published_post(user_id, post_id):
    conn = get_db_connection()
    conn.execute("INSERT OR IGNORE INTO published_posts (user_id, post_id) VALUES (?, ?)", (user_id, post_id))
    conn.commit()
    conn.close()

def get_published_post_ids(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT post_id FROM published_posts WHERE user_id = ?", (user_id,))
    ids = [row['post_id'] for row in cursor.fetchall()]
    conn.close()
    return ids

def get_logs_by_username(username):
    conn = get_db_connection()
    logs = conn.execute(
        "SELECT * FROM event_logs WHERE message LIKE ? ORDER BY timestamp DESC LIMIT 20", 
        (f'%{username}%',)
    ).fetchall()
    conn.close()
    return logs

def get_news_metrics_by_user(user_id):
    conn = get_db_connection()
    metrics = conn.execute(
        "SELECT * FROM news_metrics WHERE user_id = ? ORDER BY analysis_date DESC", 
        (user_id,)
    ).fetchall()
    conn.close()
    return metrics

def get_posts_per_client():
    conn = get_db_connection()
    query = """
        SELECT u.username, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN published_posts p ON u.id = p.user_id
        WHERE u.is_admin = 0
        GROUP BY u.id
        ORDER BY u.username
    """
    clients_activity = conn.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in clients_activity]

def get_all_published_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM published_posts').fetchall()
    conn.close()
    return posts

def get_error_logs():
    conn = get_db_connection()
    errors = conn.execute("SELECT * FROM event_logs WHERE event_type LIKE 'Erro%'").fetchall()
    conn.close()
    return errors

def get_agent_start_logs():
    conn = get_db_connection()
    runs = conn.execute("SELECT * FROM event_logs WHERE event_type = 'Início do Agente'").fetchall()
    conn.close()
    return runs

def add_remix_topics(topics):
    conn = get_db_connection()
    cursor = conn.cursor()
    for topic in topics:
        cursor.execute("INSERT INTO remix_topics (topic) VALUES (?)", (topic,))
    conn.commit()
    conn.close()

def get_unused_remix_topic():
    conn = get_db_connection()
    topic = conn.execute("SELECT * FROM remix_topics WHERE is_used = 0 ORDER BY RANDOM() LIMIT 1").fetchone()
    if topic:
        conn.execute("UPDATE remix_topics SET is_used = 1 WHERE id = ?", (topic['id'],))
        conn.commit()
    conn.close()
    return topic['topic'] if topic else None

def get_success_logs_for_client(username):
    conn = get_db_connection()
    query = "SELECT * FROM event_logs WHERE event_type = 'Publicação Instagram' AND message LIKE ?"
    logs = conn.execute(query, (f'%para {username}.%',)).fetchall()
    conn.close()
    return logs

def get_error_logs_for_client(username):
    conn = get_db_connection()
    query = "SELECT * FROM event_logs WHERE event_type = 'Erro de Publicação' AND message LIKE ?"
    logs = conn.execute(query, (f'%para {username}.%',)).fetchall()
    conn.close()
    return logs