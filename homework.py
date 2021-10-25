import logging

import os

import requests
from dotenv import load_dotenv
from telegram import Bot
import time

load_dotenv()

secret_practicum_token = os.getenv('PRACTICUM_TOKEN')
secret_telegram_token = os.getenv('TELEGRAM_TOKEN')
secret_chat_id = os.getenv('CHAT_ID')

PRACTICUM_TOKEN = secret_practicum_token
TELEGRAM_TOKEN = secret_telegram_token
CHAT_ID = secret_chat_id

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='main.log',
    filemode='w'
)
logger = logging.getLogger(__name__)
logger.addHandler(
    logging.StreamHandler()
)

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}


def IsRequiredVariables():
    """Эта функция проверяет обязательные переменнные."""
    try:
        if PRACTICUM_TOKEN is not None and TELEGRAM_TOKEN is not None:
            if CHAT_ID is not None and RETRY_TIME is not None:
                if ENDPOINT is not None:
                    return 0
        logger.critical("Your required varieble is None")
    except NameError as error:
        logger.critical(f"You haven't required varieble: {error}")


def ResponseIsNot200(response):
    """Функция для обработки недоступного ENDPOINT."""
    status_code = response.status_code
    message = f'Status code your ENDPOINT is {status_code}'
    logger.error(message)
    return message


def send_message(bot, message):
    """Эта функция отправляет сообщение."""
    try:
        logger.info(f'Bot sent message: {message}')
        bot.send_message(CHAT_ID, message)
    except Exception as error:
        logger.error(f'Error in send message: {error}')


def get_api_answer(url, current_timestamp):
    """Эта функция делает запрос к API практикума."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    response = requests.get(
        url, headers=headers, params=payload
    )
    if response.status_code != 200:
        return ResponseIsNot200(response)
    response = response.json()
    return check_response(response)


def parse_status(homework):
    """Эта функция оповещает об изменение статуса."""
    if homework in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework]
        homework_name = homework
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    else:
        message = f'Your status({homework}) is unknown'
        logger.error(message)
        return message


def check_response(response):
    """Эта функция проверят статус д/з."""
    if response is None:
        message = "Your API hasn't expected keys"
        logger.error(message)
        return message
    homeworks = response.get('homeworks')
    print(homeworks)
    if homeworks != []:
        status = homeworks[0].get('status')
        return parse_status(status)
    return None


def main():
    """Функция служебного кода."""
    IsRequiredVariables()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    url = ENDPOINT
    while True:
        try:
            message = get_api_answer(url, current_timestamp)
            if message is not None:
                send_message(bot, message)
            time.sleep(RETRY_TIME)
            current_timestamp = int(time.time() - RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logger.error(message)
            time.sleep(RETRY_TIME)
            current_timestamp = int(time.time() - RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
