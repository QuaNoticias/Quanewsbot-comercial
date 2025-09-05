# email_client.py - VERSÃO 4.0 (Multi-Cliente)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_report(sender, password, recipient, top_news):
    """Envia um relatório em HTML por email."""
    
    # --- Configurações do Servidor SMTP do Gmail ---
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587

    # --- Montagem do Corpo do Email em HTML ---
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; color: #333; }}
            .container {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; max-width: 600px; margin: auto; }}
            .header {{ background-color: #f2f2f2; padding: 10px; text-align: center; border-radius: 8px 8px 0 0; }}
            h1 {{ color: #0056b3; }}
            .news-item {{ border-bottom: 1px solid #eee; padding: 10px 0; }}
            .news-item:last-child {{ border-bottom: none; }}
            .news-title {{ font-weight: bold; font-size: 1.1em; }}
            .news-link {{ color: #0056b3; text-decoration: none; font-size: 0.9em; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 0.8em; color: #888; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Relatório Diário - Top 3 Notícias</h1>
            </div>
            {''.join([
                f'''
                <div class="news-item">
                    <p class="news-title">{news['title']}</p>
                    <p>Score de Engajamento: {news['score']:.2f}</p>
                    <a href="{news['link']}" class="news-link">Ler matéria completa</a>
                </div>
                ''' for news in top_news
            ])}
            <div class="footer">
                <p>Este é um relatório automático gerado pelo NewsBot.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # --- Envio do Email ---
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(sender, password)
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = "NewsBot - Relatório de Engajamento das Notícias"
        msg.attach(MIMEText(html_body, 'html'))
        
        server.send_message(msg)
        server.quit()
        
        print(f"[SUCESSO] Relatório por email enviado para {recipient}.")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao enviar email: {e}")
        return False