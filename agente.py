# ATUAL/agente.py - VERSÃO COMPLETA E ATUALIZADA (PLANO Z)

import schedule
import time
import random
from datetime import datetime
from pytz import timezone
import threading

import database as db
import wordpress_client
import instagram_client
import email_client
from config import (
    PUBLISH_TIMES, EMAIL_REPORT_TIMES, REMIX_TASK_TIMES, TIMEZONE,
    PAUSE_MIN_MINUTES, PAUSE_MAX_MINUTES,
    EMAIL_SENDER, EMAIL_PASSWORD
)

def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()

def run_analysis_and_publish_task():
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE ANÁLISE E PUBLICAÇÃO - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    active_clients = db.get_all_active_client_configs()
    if not active_clients:
        db.log_event("Tarefa de Publicação", "Nenhum cliente ativo encontrado.")
        return

    for client in active_clients:
        print(f"\n--- Processando cliente: {client['username']} (ID: {client['id']}) ---")
        db.log_event("Processamento de Cliente", f"Iniciando para o cliente {client['username']}.")

        try:
            print(f"[WORDPRESS] Coletando notícias de: {client['wordpress_url']}")
            noticias = wordpress_client.get_latest_news(client['wordpress_url'])
            if not noticias:
                db.log_event("Coleta WordPress", f"Nenhuma notícia encontrada para {client['username']}.")
                continue

            noticias_com_score = wordpress_client.calculate_engagement_scores(noticias)
            top_3_noticias = sorted(noticias_com_score, key=lambda x: x['score'], reverse=True)[:3]

            print(f"[INFO] TOP 3 notícias selecionadas para {client['username']}:")
            for i, noticia in enumerate(top_3_noticias):
                print(f"  {i+1}. {noticia['title']} (Score: {noticia['score']:.2f})")
                db.add_news_metric(client['id'], noticia['id'], noticia['title'], noticia['link'], noticia['score'])

            insta_api = instagram_client.login(client['instagram_user'], client['instagram_pass'])
            if not insta_api:
                db.log_event("Erro de Publicação", f"Falha no login do Instagram para {client['username']}.")
                continue

            for noticia in top_3_noticias:
                ids_ja_publicados = db.get_published_post_ids(client['id'])
                if noticia['id'] in ids_ja_publicados:
                    continue

                print(f"\n[INSTAGRAM] Tentando publicar: '{noticia['title']}'")
                success = instagram_client.post_to_instagram(insta_api, noticia)
                
                if success:
                    db.add_published_post(client['id'], noticia['id'])
                    db.log_event("Publicação Instagram", f"Sucesso ao publicar '{noticia['title']}' para {client['username']}.")
                    
                    pause_duration = random.randint(PAUSE_MIN_MINUTES * 60, PAUSE_MAX_MINUTES * 60)
                    minutes, seconds = divmod(pause_duration, 60)
                    print(f"[INFO] Pausando por {minutes} minutos e {seconds} segundos...")
                    time.sleep(pause_duration)
                else:
                    db.log_event("Erro de Publicação", f"Falha ao publicar '{noticia['title']}' para {client['username']}.")
                    time.sleep(60)

        except Exception as e:
            db.log_event("Erro Crítico", f"Erro no processamento do cliente {client['username']}: {str(e)}")

    print("\n" + "="*50)
    print("FIM DA TAREFA DE ANÁLISE E PUBLICAÇÃO")
    print("="*50)

def send_email_report_task():
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE ENVIO DE RELATÓRIO - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    active_clients = db.get_all_active_client_configs()
    clients_with_email = [client for client in active_clients if client['report_email']]

    if not clients_with_email:
        db.log_event("Relatório por Email", "Nenhum cliente configurado para receber relatórios.")
        return

    for client in clients_with_email:
        try:
            client_metrics = db.get_news_metrics_by_user(client['id'])
            if not client_metrics:
                continue
            
            top_3_client = sorted(client_metrics, key=lambda x: x['score'], reverse=True)[:3]
            
            email_client.send_report(
                sender=EMAIL_SENDER,
                password=EMAIL_PASSWORD,
                recipient=client['report_email'],
                top_news=top_3_client
            )
            db.log_event("Relatório por Email", f"Relatório enviado para {client['username']} em {client['report_email']}.")
        except Exception as e:
            db.log_event("Erro Crítico", f"Falha ao enviar relatório para {client['username']}: {str(e)}")

def collect_instagram_stats_task():
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE COLETA DE ESTATÍSTICAS - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    active_clients = db.get_all_active_client_configs()
    for client in active_clients:
        try:
            print(f"[STATS] Coletando estatísticas para {client['username']}")
            stats = instagram_client.get_user_stats(client['instagram_user'], client['instagram_pass'])
            if stats:
                db.save_instagram_stats(client['id'], stats['followers'], stats['following'], stats['media_count'])
                db.log_event("Coleta de Estatísticas", f"Sucesso ao coletar estatísticas para {client['username']}.")
            else:
                db.log_event("Erro de Estatísticas", f"Falha ao coletar estatísticas para {client['username']}.")
        except Exception as e:
            db.log_event("Erro Crítico", f"Falha na coleta de stats para {client['username']}: {str(e)}")

# NOVA FUNÇÃO PARA O PLANO Z
def run_remix_task():
    """
    Busca um tópico da lista manual e tenta criar um remix para cada cliente habilitado.
    """
    print("\n" + "="*50)
    print(f"INICIANDO TAREFA DE REMIX - {datetime.now(timezone(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    # 1. Pega um tópico da nossa lista manual que ainda não foi usado
    topic = db.get_unused_remix_topic()
    if not topic:
        print("[REMIX] Nenhum tópico novo na lista para processar. Tarefa encerrada.")
        db.log_event("Tarefa de Remix", "Nenhum tópico novo encontrado na lista.")
        return
    
    print(f"[REMIX] Tópico do dia selecionado: '{topic}'")

    # 2. Busca todos os clientes que ativaram a tarefa de remix
    active_clients = db.get_all_active_client_configs()
    remix_clients = [c for c in active_clients if c['enable_remix_task']]

    if not remix_clients:
        print("[REMIX] Nenhum cliente habilitou a tarefa de remix.")
        db.log_event("Tarefa de Remix", "Nenhum cliente com a tarefa habilitada.")
        return

    # 3. Processa cada cliente
    for client in remix_clients:
        try:
            print(f"\n--- Processando remix para: {client['username']} ---")
            
            # Combina o tópico do dia com as palavras-chave do nicho do cliente
            search_query = f"{topic} {client['remix_niche_keywords']}"
            print(f"[REMIX] Buscando Reels com a query: '{search_query}'")

            # Lógica para buscar, baixar e repostar o remix
            # (Esta parte ainda precisa ser implementada no instagram_client.py)
            # Por enquanto, vamos apenas simular
            print("[REMIX] Lógica de busca e repostagem de remix ainda não implementada.")
            # Exemplo futuro:
            # success = instagram_client.find_and_remix_reel(client['instagram_user'], client['instagram_pass'], search_query)
            # if success:
            #     db.log_event("Tarefa de Remix", f"Sucesso ao criar remix sobre '{topic}' para {client['username']}.")
            # else:
            #     db.log_event("Erro de Remix", f"Falha ao criar remix sobre '{topic}' para {client['username']}.")

        except Exception as e:
            db.log_event("Erro Crítico", f"Falha na tarefa de remix para {client['username']}: {str(e)}")

    print("\n" + "="*50)
    print("FIM DA TAREFA DE REMIX")
    print("="*50)


def main():
    print("="*50)
    print("Agente Inteligente Multi-Cliente iniciado.")
    print(f"Fuso horário configurado para: {TIMEZONE}")
    print("Agendando tarefas...")
    
    schedule.clear()

    for t in PUBLISH_TIMES:
        schedule.every().day.at(t, TIMEZONE).do(run_threaded, run_analysis_and_publish_task)
        print(f"- Tarefa de Publicação agendada para as {t}")

    for t in EMAIL_REPORT_TIMES:
        schedule.every().day.at(t, TIMEZONE).do(run_threaded, send_email_report_task)
        print(f"- Tarefa de Relatório por Email agendada para as {t}")

    # Agendamento da nova tarefa de remix
    for t in REMIX_TASK_TIMES:
        schedule.every().day.at(t, TIMEZONE).do(run_threaded, run_remix_task)
        print(f"- Tarefa de Remix agendada para as {t}")

    # Agendamento da coleta de estatísticas (uma vez por dia)
    schedule.every().day.at("23:55", TIMEZONE).do(run_threaded, collect_instagram_stats_task)
    print("- Tarefa de Coleta de Estatísticas agendada para as 23:55")

    print("Agendamento concluído. O agente está em modo de espera.")
    print("="*50)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()