# ATUAL/config.py - VERSÃO COMPLETA E CORRIGIDA

# --- CONFIGURAÇÕES DE AGENDAMENTO ---
# Horários em que a tarefa de publicação de notícias será executada
PUBLISH_TIMES = ["09:53", "14:00", "16:42"]

# Horários em que a tarefa de envio de relatório por email será executada
EMAIL_REPORT_TIMES = ["09:53"]

# Horários em que a nova tarefa de Remix será executada
REMIX_TASK_TIMES = ["14:10", "16:28"]

# Fuso horário para todas as tarefas
TIMEZONE = "America/Cuiaba"

# --- CONFIGURAÇÕES DE COMPORTAMENTO ---
# Pausa mínima e máxima (em minutos) entre as publicações no Instagram
PAUSE_MIN_MINUTES = 5
PAUSE_MAX_MINUTES = 15


# --- CONFIGURAÇÕES DE EMAIL DO ADMINISTRADOR ---
# Usado para enviar os relatórios para os clientes
# IMPORTANTE: Use uma senha de aplicativo do Gmail, não a sua senha normal
EMAIL_SENDER = "llconsultoriahora@gmail.com"
EMAIL_PASSWORD = "zuda xkhb msfp xief"

# --- CONFIGURAÇÕES DO SERVIDOR DE EMAIL (SMTP) ---
# Estas variáveis estavam faltando e causando o erro
EMAIL_HOST = "llconsultoriahora@gmail.com"
EMAIL_PORT = 587
EMAIL_SUBJECT = "lconsultoriahora@gmail.com"