# wordpress_client.py - VERSÃO 4.0 (Multi-Cliente)

import requests
from datetime import datetime
from bs4 import BeautifulSoup

def get_latest_news(wordpress_url):
    """Busca as 5 notícias mais recentes de um site WordPress via API REST."""
    # Constrói a URL da API a partir da URL base do cliente
    api_url = f"{wordpress_url.rstrip('/')}/wp-json/wp/v2/posts?per_page=5&_embed"
    
    try:
        response = requests.get(api_url, timeout=15)
        response.raise_for_status()
        posts = response.json()
        
        noticias = []
        for post in posts:
            # Extrai o texto puro do conteúdo HTML para contar palavras
            soup = BeautifulSoup(post['content']['rendered'], 'html.parser')
            text_content = soup.get_text()
            word_count = len(text_content.split())

            # Encontra a URL da imagem destacada
            image_url = None
            if 'wp:featuredmedia' in post['_embedded']:
                image_url = post['_embedded']['wp:featuredmedia'][0]['source_url']

            noticias.append({
                'id': post['id'],
                'title': post['title']['rendered'],
                'link': post['link'],
                'date': post['date'],
                'word_count': word_count,
                'image_url': image_url
            })
        return noticias
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao conectar com a API do WordPress: {e}")
        return []
    except Exception as e:
        print(f"[ERRO] Falha ao processar notícias do WordPress: {e}")
        return []

def calculate_engagement_scores(noticias):
    """Calcula um score de engajamento para cada notícia."""
    for noticia in noticias:
        # Fator 1: Tamanho do conteúdo (mais palavras = maior score)
        score_palavras = noticia.get('word_count', 0) / 100.0

        # Fator 2: Recência (notícias mais novas ganham bônus)
        post_date = datetime.fromisoformat(noticia['date'])
        dias_atras = (datetime.now() - post_date).days
        score_recencia = max(0, 10 - dias_atras) # Bônus para notícias dos últimos 10 dias

        # Score final
        noticia['score'] = score_palavras + score_recencia
    return noticias