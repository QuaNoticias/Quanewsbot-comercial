# email_client.py - VERSÃO MELHORADA

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

# Importações do arquivo de configuração
from config import EMAIL_HOST, EMAIL_PORT, EMAIL_SUBJECT

def send_report(sender, password, recipient, top_news, client_name=None):
    """Envia um email com as top notícias."""
    
    # Personaliza o assunto do email
    subject_name = f" para {client_name}" if client_name else ""
    subject = f"NewsBot - Seu Relatório Diário de Notícias{subject_name}"
    
    # Monta o corpo do email
    body = "Olá!\n\nEstas foram as notícias com maior potencial de engajamento analisadas hoje:\n\n"
    for i, news in enumerate(top_news):
        body += f"{i+1}. {news['title']} (Score: {news['score']:.2f})\n"
        body += f"   Link: {news['link']}\n\n"
    body += "Atenciosamente,\nEquipe NewsBot"

    # Configura a mensagem
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Conecta e envia
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
        server.quit()
        print(f"[EMAIL] Relatório enviado com sucesso para {recipient}!")
    except Exception as e:
        print(f"[ERRO EMAIL] Falha ao enviar relatório para {recipient}: {e}")