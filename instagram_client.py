# ATUAL/instagram_client.py

from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import time

def login(username, password):
    """Faz login no Instagram e retorna o objeto do cliente."""
    try:
        cl = Client()
        # Adiciona um timeout para evitar que o login fique travado indefinidamente
        cl.login_timeout = 15
        cl.login(username, password)
        return cl
    except LoginRequired:
        print(f"[ERRO INSTAGRAM] Login necessário, mas falhou para {username}. Verifique as credenciais ou a autenticação de dois fatores.")
        return None
    except Exception as e:
        print(f"[ERRO INSTAGRAM] Falha inesperada no login para {username}: {e}")
        return None

def post_to_instagram(cl, noticia):
    """Posta uma notícia no Instagram (atualmente como placeholder)."""
    try:
        # Lógica de postagem (exemplo: postar uma imagem com legenda)
        # caption = f"{noticia['title']}\n\nSaiba mais em nosso site!\n\n#noticia #news"
        # cl.photo_upload("caminho/para/imagem.jpg", caption)
        
        print(f"[SIMULAÇÃO INSTAGRAM] Postando '{noticia['title']}'")
        time.sleep(2) # Simula o tempo de upload
        return True
    except Exception as e:
        print(f"[ERRO INSTAGRAM] Falha ao postar: {e}")
        return False

def get_user_stats(username, password):
    """Busca estatísticas de um usuário do Instagram."""
    cl = login(username, password)
    if not cl:
        return None
    try:
        user_info = cl.user_info_by_username(username)
        return {
            'followers': user_info.follower_count,
            'following': user_info.following_count,
            'media_count': user_info.media_count
        }
    except Exception as e:
        print(f"[ERRO INSTAGRAM] Falha ao buscar estatísticas para {username}: {e}")
        return None