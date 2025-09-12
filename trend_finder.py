# Salve como ATUAL/trend_finder.py - VERSÃO FINAL (CURL)

import subprocess  # Biblioteca para executar comandos do sistema
import json

def get_brazil_trending_topics():
    """
    Busca os trending topics do Brasil usando o comando 'curl' do sistema.
    Esta é a abordagem mais robusta para contornar problemas de rede e SSL.
    """
    # Este é o comando que vamos executar no terminal, como se fosse digitado manualmente.
    # O argumento '-k' ou '--insecure' diz ao curl para ignorar erros de SSL.
    command = [
        'curl',
        '-k',  # Ignora a verificação SSL (equivalente ao verify=False)
        'https://api.thefreepress.app/v1/trends?woeid=23424768'
    ]
        
    try:
        # Executa o comando e captura a saída
        result = subprocess.run(command, capture_output=True, text=True, check=True)
            
        # A saída do comando é um texto (string), então precisamos convertê-lo para JSON
        data = json.loads(result.stdout)
            
        # Extrai os nomes das tendências
        trending_topics = [trend['name'].replace('#', '') for trend in data['trends']]
            
        print(f"[TRENDS] Tópicos encontrados via cURL: {trending_topics}")
        return trending_topics

    except subprocess.CalledProcessError as e:
        print(f"[ERRO cURL] O comando falhou com o código de erro {e.returncode}.")
        print(f"Erro: {e.stderr}")
        return []
    except Exception as e:
        print(f"[ERRO GERAL] Falha ao processar a saída do cURL: {e}")
        return []

# Exemplo de como usar (para testar o arquivo diretamente)
if __name__ == '__main__':
    topicos = get_brazil_trending_topics()
    if topicos:
        print("\n--- Top Tópicos do Brasil (via cURL) ---")
        for i, topico in enumerate(topicos):
            print(f"{i+1}. {topico}")