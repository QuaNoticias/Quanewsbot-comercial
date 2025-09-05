# instagram_client.py - VERSÃO 4.0 (Multi-Cliente)

from instagrapi import Client
from instagrapi.exceptions import LoginRequired
import os
import requests

SESSION_FILE_TEMPLATE = "session_{username}.json"

def login(username, password):
    """Realiza o login no Instagram e salva a sessão."""
    session_file = SESSION_FILE_TEMPLATE.format(username=username)
    cl = Client()
    
    if os.path.exists(session_file):
        cl.load_settings(session_file)
        try:
            cl.login(username, password)
            cl.get_timeline_feed() # Verifica se a sessão é válida
            print(f"[INSTAGRAM] Sessão para '{username}' carregada e válida.")
        except LoginRequired:
            print(f"[INSTAGRAM] Sessão para '{username}' expirou. Realizando novo login...")
            return perform_fresh_login(cl, username, password, session_file)
        except Exception as e:
            print(f"[INSTAGRAM] Erro inesperado com a sessão salva para '{username}': {e}. Realizando novo login...")
            return perform_fresh_login(cl, username, password, session_file)
    else:
        print(f"[INSTAGRAM] Nenhuma sessão encontrada para '{username}'. Realizando primeiro login...")
        return perform_fresh_login(cl, username, password, session_file)
        
    return cl

def perform_fresh_login(cl, username, password, session_file):
    """Executa um login do zero e salva a sessão."""
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        print(f"[INSTAGRAM] Login para '{username}' realizado com sucesso e sessão salva.")
        return cl
    except Exception as e:
        print(f"[ERRO INSTAGRAM] Falha no login para o usuário '{username}': {e}")
        return None

def post_to_instagram(cl, noticia):
    """Publica uma notícia no Instagram, baixando a imagem primeiro."""
    if not noticia.get('image_url'):
        print(f"[ERRO] Notícia '{noticia['title']}' não tem imagem destacada. Pulando.")
        return False

    try:
        # Baixar a imagem
        image_url = noticia['image_url']
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        
        temp_image_path = "temp_image.jpg"
        with open(temp_image_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        # Criar a legenda
        hashtags = "#noticias #matogrosso #cuiaba #news" # Hashtags genéricas
        caption = f"{noticia['title']}\n\nLeia a matéria completa no nosso site (link na bio)!\n\n{hashtags}"
        
        # Publicar a foto
        cl.photo_upload(temp_image_path, caption)
        
        # Limpar a imagem temporária
        os.remove(temp_image_path)
        
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao publicar no Instagram: {e}")
        if os.path.exists("temp_image.jpg"):
            os.remove("temp_image.jpg") # Garante a limpeza em caso de erro
        return False