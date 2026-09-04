# Bookmarks Project

## Запуск
1. Установка зависимостей:
   `uv sync`
2. Настройка переменных окружения:
   Скопировать `.env.example` в `.env` и заполнить ключи.
3. Генерация SSL-сертификатов (для runserver_plus):
   `openssl req -x509 -newkey rsa:4096 -keyout cert.key -out cert.crt -days 365 -nodes`
4. Миграции и запуск:
   `uv run python manage.py migrate`
   `uv run python manage.py runserver_plus --cert-file cert.crt --key-file cert.key`