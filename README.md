# Телеграмм-бот
## Этот бот смождет проверять статус домашней работы и отправлять уведомление, в случае каких-либо изменений.
____
## Развёртывание проекта
- Для того, чтобы развернуть этот проект у себя на ПК нужно открыть терминал и вбить команду ```git clone https://github.com/Fizik05/homework_bot.git```
- Далее устанавливаем виртуальное окружение в корневую папку проекта ```python -m venv venv```
- После активируем его ```source venv/Scripts/activate```, обновляем PIP ```python -m pip install --upgrade pip``` и устанавливаем зависимости ```pip install -r requirements.txt```
- Далее в корне проекта создаём файл ```.env``` и вводим туда переменные:
```
PRACTICUM_TOKEN="Токен от вашего аккаунта в Яндекс.Практикуме"
TELEGRAM_TOKEN="Токен вашего бота"
CHAT_ID="ID вашего профиля"
```
- Запускаем файл и наш бот заработает
____
## Системные требования
- Python=3.7+
- PIP=22.0.4
____
