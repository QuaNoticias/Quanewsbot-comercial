# ATUAL/wordpress_client.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_latest_news(wordpress_url):
    """Busca as notícias mais recentes de um site WordPress."""
    try:
        # Adiciona /wp-json/wp/v2/posts para acessar a API REST do WordPress
        api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts?per_page=10"
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        
        noticias = []
        for post in response.json():
            # Limpa o HTML do título
            soup = BeautifulSoup(post['title']['rendered'], 'html.parser')
            clean_title = soup.get_text()

            noticias.append({
                'id': post['id'],
                'title': clean_title,
                'link': post['link'],
                'date': post['date_gmt'] + "Z" # Adiciona Z para indicar UTC
            })
        return noticias
    except requests.exceptions.RequestException as e:
        print(f"[ERRO WORDPRESS] Falha ao conectar com {wordpress_url}: {e}")
        return []
    except Exception as e:
        print(f"[ERRO WORDPRESS] Falha ao processar notícias de {wordpress_url}: {e}")
        return []

def calculate_engagement_scores(noticias):
    """
    Calcula um 'score' para cada notícia.
    Atualmente, a lógica é simples: notícias mais recentes têm score maior.
    """
    noticias_com_score = []
    now = datetime.utcnow()

    for noticia in noticias:
        try:
            post_date = datetime.strptime(noticia['date'], '%Y-%m-%dT%H:%M:%SZ')
            age = now - post_date
            
            # Lógica de Score: Inverte a idade da notícia (em horas)
            # Notícias mais novas (idade menor) recebem score maior.
            # Adiciona 1 para evitar divisão por zero.
            score = 100 / (age.total_seconds() / 3600 + 1)
            
            noticia['score'] = score
            noticias_com_score.append(noticia)
        except Exception:
            # Se a data for inválida, atribui score 0
            noticia['score'] = 0
            noticias_com_score.append(noticia)