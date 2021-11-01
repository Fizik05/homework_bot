import logging
import os
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="main.log",
    filemode="w",
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"

HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена, в ней нашлись ошибки.",
}


def is_required_variables():
    """Эта функция проверяет обязательные переменнные."""
    message = "Program stoped, because required variable is missing"
    stop_program = False
    if PRACTICUM_TOKEN is None:
        logger.critical(f"{message} PRACTICUM TOKEN")
        stop_program = True
    if TELEGRAM_TOKEN is None:
        logger.critical(f"{message} TELEGRAM TOKEN")
        stop_program = True
    if CHAT_ID is None:
        logger.critical(f"{message} CHAT_ID")
        stop_program = True
    return stop_program


class EndpointIsNotAvaileble(Exception):
    """Функция для обработки недоступного ENDPOINT."""


class TGBotException(Exception):
    """Класс для обработки пустго API ответа."""


def send_message(bot, message):
    """Эта функция отправляет сообщение."""
    try:
        logger.info(f"Bot sent message: {message}")
        bot.send_message(CHAT_ID, message)
    except TelegramError as error:
        logger.error(f"Error in send message: {error}")


def get_api_answer(url, current_timestamp):
    """Эта функция делает запрос к API практикума."""
    headers = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}
    payload = {"from_date": current_timestamp}
    try:
        response = requests.get(url, headers=headers, params=payload)
    except requests.exceptions.RequestException as request_error:
        message = f"API response code is {request_error}"
        logger.error(message)
        raise EndpointIsNotAvaileble(message)
    if response.status_code != HTTPStatus.OK:
        message = (
            f"Endpoint {url} is not available."
            f"API response code is {response.status_code}"
        )
        logger.error(message)
        raise TGBotException(message)
    return response.json()


def parse_status(homework):
    """Эта функция оповещает об изменение статуса."""
    homework_status = homework.get("status")
    verdict = HOMEWORK_STATUSES[homework_status]
    homework_name = homework.get("homework_name")
    if homework_name is None:
        raise TGBotException("Invalid results")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    """Эта функция проверят статус д/з."""
    if response is None:
        message = "Your API hasn't expected keys"
        logger.error(message)
        return message
    homeworks = response.get("homeworks")
    if len(homeworks) > 0 and type(homeworks) == list:
        return parse_status(response.get("homeworks")[0])
    return None


def main():
    """Функция служебного кода."""
    stop_program = is_required_variables()
    if stop_program:
        raise TGBotException("Одна из обязательных переменных отсутствует")
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    url = ENDPOINT
    while True:
        try:
            response = get_api_answer(url, current_timestamp)
            message = check_response(response)
            if message is not None:
                send_message(bot, message)
        except Exception as error:
            message = f"Сбой в работе программы: {error}"
            send_message(bot, message)
            logger.error(message)
        finally:
            time.sleep(RETRY_TIME)
            current_timestamp = int(time.time() - RETRY_TIME)


if __name__ == "__main__":
    main()
