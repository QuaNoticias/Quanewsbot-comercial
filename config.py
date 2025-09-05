# config.py - VERSÃO 5.0 (FINAL E COMPLETA)

# --- Configurações do Banco de Dados ---
DATABASE_FILE = "agente.db"

# --- Configurações do Agente ---
# Fuso horário para as publicações. Ex: 'America/Sao_Paulo', 'America/Cuiaba'
TIMEZONE = "America/Cuiaba"

# Horários para o agente rodar a tarefa de publicação (formato 24h)
PUBLISH_TIMES = ["09:35", "12:30", "18:30", "20:30"]

# Horários para o agente enviar o relatório por email
EMAIL_REPORT_TIMES = ["14:00", "22:00"]

# Intervalo de pausa (em minutos) entre as publicações no Instagram
PAUSE_MIN_MINUTES = 10
PAUSE_MAX_MINUTES = 20

# --- Configurações de Email para Relatórios ---
# (Lembre-se de usar uma "Senha de App" gerada no Google)
EMAIL_SENDER = "llconsultorihora@gmail.com"
EMAIL_PASSWORD = "zuda xkhb msfp xief"
EMAIL_RECIPIENT = "llconsultoriahora@gmail.com"

# --- Chave Secreta para Segurança dos Painéis ---
# (Não precisa alterar, é gerada aleatoriamente)
FLASK_SECRET_KEY = b'\x9e\x8f\x1a\xec\x0f\x8b\x9a\x0c\x1e\xbf\x9c\x8d\x0f\x1e\x8a\x9d'