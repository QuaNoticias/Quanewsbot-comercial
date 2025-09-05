# agente.py - VERSÃO 4.0 (Multi-Cliente)

import schedule
import time
import random
from datetime import datetime
from pytz import timezone

import database as db
import wordpress_client
import instagram_client
import email_client
from config import (
    PUBLISH_TIMES, EMAIL_REPORT_TIMES, TIMEZONE,
    PAUSE_MIN_MINUTES, PAUSE_MAX_MINUTES,
    EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT
)

def run_analysis_and_publish_task():
    """
    Tarefa principal que roda para cada cliente ativo.
    Busca notícias, calcula scores, e publica as melhores no Instagram.
    """
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE ANÁLISE E PUBLICAÇÃO - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # 1. Buscar todos os clientes ativos e suas configurações
    active_clients = db.get_all_active_client_configs()
    if not active_clients:
        print("[INFO] Nenhum cliente ativo com configuração encontrada. Tarefa encerrada.")
        db.log_event("Tarefa de Publicação", "Nenhum cliente ativo encontrado.")
        return

    print(f"[INFO] Encontrados {len(active_clients)} clientes ativos para processar.")

    # 2. Loop para executar a tarefa para cada cliente
    for client in active_clients:
        print(f"\n--- Processando cliente: {client['username']} ---")
        db.log_event("Processamento de Cliente", f"Iniciando para o cliente {client['username']}.")

        try:
            # 3. Coletar e analisar notícias do WordPress do cliente
            print(f"[WORDPRESS] Coletando notícias de: {client['wordpress_url']}")
            noticias = wordpress_client.get_latest_news(client['wordpress_url'])
            if not noticias:
                print("[AVISO] Nenhuma notícia encontrada no WordPress. Pulando para o próximo cliente.")
                db.log_event("Coleta WordPress", f"Nenhuma notícia encontrada para {client['username']}.")
                continue

            # 4. Calcular scores e selecionar as TOP 3 não publicadas
            noticias_com_score = wordpress_client.calculate_engagement_scores(noticias)
            ids_ja_publicados = db.get_published_post_ids()
            
            top_3_noticias = sorted(
                [n for n in noticias_com_score if n['id'] not in ids_ja_publicados],
                key=lambda x: x['score'],
                reverse=True
            )[:3]

            if not top_3_noticias:
                print("[INFO] Nenhuma notícia nova para publicar. Todas as melhores já foram postadas.")
                db.log_event("Seleção de Conteúdo", f"Nenhuma notícia nova para publicar para {client['username']}.")
                continue

            print(f"[INFO] TOP 3 notícias selecionadas para {client['username']}:")
            for i, noticia in enumerate(top_3_noticias):
                print(f"  {i+1}. {noticia['title']} (Score: {noticia['score']:.2f})")
                db.add_news_metric(noticia['id'], noticia['title'], noticia['link'], noticia['score'])

            # 5. Publicar no Instagram do cliente
            insta_api = instagram_client.login(client['instagram_user'], client['instagram_pass'])
            if not insta_api:
                print(f"[ERRO INSTAGRAM] Falha no login para o usuário {client['instagram_user']}. Pulando publicação.")
                db.log_event("Erro de Publicação", f"Falha no login do Instagram para {client['username']}.")
                continue

            for noticia in top_3_noticias:
                print(f"\n[INSTAGRAM] Tentando publicar: '{noticia['title']}'")
                success = instagram_client.post_to_instagram(insta_api, noticia)
                
                if success:
                    db.add_published_post(noticia['id'])
                    print(f"[SUCESSO] Notícia '{noticia['title']}' publicada para {client['username']}!")
                    db.log_event("Publicação Instagram", f"Sucesso ao publicar '{noticia['title']}' para {client['username']}.")
                    
                    # Pausa aleatória para simular comportamento humano
                    pause_duration = random.randint(PAUSE_MIN_MINUTES * 60, PAUSE_MAX_MINUTES * 60)
                    print(f"[INFO] Pausando por {pause_duration // 60} minutos e {pause_duration % 60} segundos...")
                    time.sleep(pause_duration)
                else:
                    print(f"[ERRO] Falha ao publicar a notícia '{noticia['title']}' para {client['username']}.")
                    db.log_event("Erro de Publicação", f"Falha ao publicar '{noticia['title']}' para {client['username']}.")

        except Exception as e:
            print(f"[ERRO GERAL] Ocorreu um erro inesperado ao processar o cliente {client['username']}: {e}")
            db.log_event("Erro Crítico", f"Erro no processamento do cliente {client['username']}: {str(e)}")

    print("\n" + "="*50)
    print("FIM DA TAREFA DE ANÁLISE E PUBLICAÇÃO")
    print("="*50)


def send_email_report_task():
    """Envia o relatório diário por email com as TOP 3 notícias gerais."""
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE ENVIO DE RELATÓRIO - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    all_metrics = db.get_all_news_metrics()
    if not all_metrics:
        print("[INFO] Nenhuma métrica de notícia para gerar relatório.")
        db.log_event("Relatório por Email", "Nenhuma métrica encontrada para gerar relatório.")
        return

    # --- CORREÇÃO APLICADA AQUI ---
    # Filtra a lista para incluir apenas notícias que realmente têm um 'score'.
    # Isso evita o erro se algum dado no banco estiver incompleto.
    noticias_com_score = [news for news in all_metrics if 'score' in news and news['score'] is not None]

    if not noticias_com_score:
        print("[INFO] Nenhuma notícia com score válido encontrada para o relatório.")
        db.log_event("Relatório por Email", "Nenhuma métrica com score válido encontrada.")
        return

    # Pega as 3 melhores notícias do dia (ou as últimas analisadas)
    top_3_geral = sorted(noticias_com_score, key=lambda x: x['score'], reverse=True)[:3]
    
    email_client.send_report(
        sender=EMAIL_SENDER,
        password=EMAIL_PASSWORD,
        recipient=EMAIL_RECIPIENT,
        top_news=top_3_geral
    )
    db.log_event("Relatório por Email", f"Relatório enviado para {EMAIL_RECIPIENT}.")


def main():
    """Função principal que agenda e executa as tarefas."""
    print("="*50)
    print("Agente Inteligente Multi-Cliente iniciado.")
    print(f"Fuso horário configurado para: {TIMEZONE}")
    print("Agendando tarefas...")
    
    # Limpa agendamentos antigos
    schedule.clear()

    # Agenda as tarefas de publicação
    for t in PUBLISH_TIMES:
        schedule.every().day.at(t, TIMEZONE).do(run_analysis_and_publish_task)
        print(f"- Tarefa de Publicação agendada para as {t}")

    # Agenda as tarefas de envio de email
    for t in EMAIL_REPORT_TIMES:
        schedule.every().day.at(t, TIMEZONE).do(send_email_report_task)
        print(f"- Tarefa de Relatório por Email agendada para as {t}")

    print("Agendamento concluído. O agente está em modo de espera.")
    print("="*50)

    # Executa uma vez para teste imediato
    # run_analysis_and_publish_task()
    # send_email_report_task()

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()