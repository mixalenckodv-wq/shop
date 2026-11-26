# Shop — онлайн-магазин обуви

Учебный/рабочий проект интернет-магазина обуви: каталог, корзина, оформление
заказа, админка и Telegram-уведомления.

## Стек

- Python 3.12, Django 5, Django REST Framework
- PostgreSQL
- Django Admin
- Telegram-бот (python-telegram-bot, режим webhook)
- Docker Compose

## Возможности

- Каталог товаров, карточка товара, размеры и остатки
- Корзина и оформление заказа
- Админка для товаров, категорий, остатков и заказов
- Telegram: уведомление администратора о новом заказе
- Telegram: сообщение клиенту о переводе заказа в обработку

## Быстрый старт (Docker)

1. Скопируйте переменные окружения:

   ```bash
   cp .env.example .env
   ```

2. Заполните `.env` (при необходимости):

   - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
   - `POSTGRES_*`
   - `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ADMIN_CHAT_ID`, `TELEGRAM_WEBHOOK_URL`, `TELEGRAM_WEBHOOK_SECRET`

3. Запустите сервисы:

   ```bash
   docker compose up --build
   ```

4. Примените миграции и создайте администратора:

   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

5. Откройте:

   - Магазин: http://localhost:8000/
   - Админка: http://localhost:8000/admin/

## Запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Секреты

Реальные значения токенов и паролей в репозиторий не попадают.
Используйте `.env` (он в `.gitignore`), а в репозитории хранится только
`.env.example` с плейсхолдерами.

## Статус разработки

- [x] Фаза 1 — каркас проекта, настройки, Docker
- [ ] Фаза 2 — модели и админка
- [ ] Фаза 3 — каталог, корзина, оформление заказа
- [ ] Фаза 4 — Telegram-уведомления
- [ ] Фаза 5 — тесты
