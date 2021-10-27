import logging

import os

from http import HTTPStatus
import requests
from dotenv import load_dotenv
from telegram import Bot
import time

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

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
    message = 'Program stoped, because required variable is missing'
    if PRACTICUM_TOKEN is None:
        logger.critical(f'{message} PRACTICUM TOKEN')
    if TELEGRAM_TOKEN is None:
        logger.critical(f'{message} TELEGRAM TOKEN')
    if CHAT_ID is None:
        logger.critical(f'{message} CHAT_ID')


def TheAnswerIsNot200Error(message):
    """Функция обрабатывает статус неравный 200."""
    return message


class RequestExceptionError(Exception):
    """Функция для обработки недоступного ENDPOINT."""


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
    try:
        response = requests.get(
            url, headers=headers, params=payload
        )
        if response.status_code != HTTPStatus.OK:
            message = (
                f'Endpoint {url} is not available.'
                f"API response code is {response.status_code}"
            )
            logger.error(message)
            raise TheAnswerIsNot200Error(message)
        return response.json()
    except requests.exceptions.RequestException as request_error:
        message = (f'API response code is {request_error}')
        logger.error(message)
        raise RequestExceptionError(message)


def parse_status(homework):
    """Эта функция оповещает об изменение статуса."""
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES[homework_status]
    homework_name = homework.get("homework_name")
    if homework_name is None or verdict is None:
        raise Exception("Invalid results")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    """Эта функция проверят статус д/з."""
    if response is None:
        message = "Your API hasn't expected keys"
        logger.error(message)
        return message
    homeworks = response.get('homeworks')
    if homeworks != []:
        return parse_status(response.get('homeworks')[0])
    return None


def main():
    """Функция служебного кода."""
    IsRequiredVariables()
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    url = ENDPOINT
    while True:
        try:
            response = get_api_answer(url, current_timestamp)
            message = check_response(response)
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
