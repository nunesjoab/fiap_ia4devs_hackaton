import os
import json
import urllib3
import logging
import requests
from urlextract import URLExtract

# Constantes com chaves e endpoints utilizados

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ENDPOINT_ANALYZE_URL = os.environ.get('ENDPOINT_ANALYZE_URL')
ENDPOINT_ANALYZE_SUBSCRIPTION_KEY = os.environ.get('ENDPOINT_ANALYZE_SUBSCRIPTION_KEY')

# Constantes com as mensagem retornadas para o usuário no Telegram
MENSAGEM_INICIO = 'Essa é a aplicação de analise de diagramas de engenharia de software.'
MENSAGEM_AGUARDANDO_IMAGEM = 'Envie uma imagem do diagrama (seja por anexo ou link) que retornarei um relatório com as melhorias de segurança recomendadas. Envie uma imagem por vez.'
MENSAGEM_RESULTADO_ANALISE = 'Analíse concluida. O resultado da analíse se encontra nesse link: '
MENSAGEM_ERRO_GENERICO = 'Ocorreu um erro ao processar a imagem.'
MENSAGEM_ERRO_REPORT_LINK_VAZIO = 'Ocorreu um erro ao processar a imagem: Relatório inválido'
MENSAGEM_ERRO_AO_EXTRAIR_IMAGEM = 'Ocorreu um erro ao extrair a imagem enviada pelo usuário.'
MENSAGEM_MIDIA_NAO_SUPORTADA = 'Tipo de mídia não suportada. Envie um anexo ou link contendo uma imagem.'

def send_message(chat_id, message):
    reply = {
        "chat_id": chat_id,
        "text": message
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    encoded_data = json.dumps(reply).encode('utf-8')
    http.request('POST', url, body=encoded_data, headers={'Content-Type': 'application/json'})
    
    print(f"*** Reply : {encoded_data}")


# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

    
def process_message_new(message_data):

    chat_id = message_data['message']['chat']['id']

    if "photo" in message_data["message"]:
        print('Photo found on message')
        photos = message_data["message"]["photo"]
        largest_photo = photos[-1]  # Get the last (largest) photo object
        file_id = largest_photo["file_id"]

        get_file_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        print(get_file_url)
        response = requests.get(get_file_url).json()

        if response["ok"]:
            file_path = response["result"]["file_path"]
            download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            print(f"*** photo download url: {download_url}")
            image_url = download_url
    elif "text" in message_data['message']:
        image_url = message_data['message']['text']
    else:
        logger.warning(MENSAGEM_MIDIA_NAO_SUPORTADA)
        send_message(chat_id, MENSAGEM_MIDIA_NAO_SUPORTADA)

    try:
        if image_url:
            response = call_analyze_endpoint(image_url)
            if response:
                print(response)
                send_message(chat_id, MENSAGEM_RESULTADO_ANALISE + response)
            else:
                print('Response empty')
                logger.error(MENSAGEM_ERRO_REPORT_LINK_VAZIO)
                send_message(chat_id, MENSAGEM_ERRO_REPORT_LINK_VAZIO)
        else:
            logger.error(MENSAGEM_ERRO_AO_EXTRAIR_IMAGEM)
            send_message(chat_id, MENSAGEM_ERRO_AO_EXTRAIR_IMAGEM)
    except Exception as e:
        send_message(chat_id, MENSAGEM_ERRO_GENERICO)

def send_message(chat_id, message):
    reply = {
        "chat_id": chat_id,
        "text": message
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    encoded_data = json.dumps(reply).encode('utf-8')
    http.request('POST', url, body=encoded_data, headers={'Content-Type': 'application/json'})
    
    print(f"*** Reply : {encoded_data}")

def call_analyze_endpoint(image_url):

    if image_url:
        print('Enviando imagem para analise')
        # Envia a URL da imagem para a aplicação de análise

        headers = {
            'Ocp-apim-subscription-key': ENDPOINT_ANALYZE_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            "fileUrl": image_url
        }
        
        # Make the POST request to the API

        body = json.dumps(payload)
        http = urllib3.PoolManager()
        response = http.request('POST', ENDPOINT_ANALYZE_URL, body=body, headers=headers)
        
        if response.status == 200:
            print('Analise concluida')
            data = response.data.decode('utf-8')
            json_data = json.loads(data)
            report_link = json_data['report']
            return report_link
        else:
            print('Falha na analise')
    else:
        print('Imagem para analise vazia')
        
def log_and_throw_exception(message):
    logger.error(message)
    raise Exception(message)

def lambda_handler(event, context):
    print('Lambda ativado')
    body = json.loads(event['body'])
    
    chat_id = body['message']['chat']['id']
    print(f"*** chat id: {chat_id}")

    if "text" in body['message']:
        message_text = body['message']['text']
        print(f"*** message text: {message_text}")

    print('Iniciando processamento da mensagem')

    print(json.dumps(body))
    process_message_new(body)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Fim do processamento')
    }

