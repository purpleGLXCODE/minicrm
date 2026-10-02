# MiniCRM

Минимальный MVP CRM для заявок агентства.

## Demo

**Telegram Bot:** @minicrm_leads_bot

**CRM:** http://107.189.18.133/

## Цель

Собрать рабочий end-to-end контур без лишней инфраструктуры:

Telegram → Bot → API → PostgreSQL → CRM

При этом **веб-CRM — главный продукт**, а Telegram — только один из инструментов поступления лидов.

## MVP

- список лидов;
- ручное добавление лида;
- Telegram-бот: имя → контакт → запрос;
- автоматическое создание лида в PostgreSQL;
- теги;
- фильтрация по тегу;
- источник лида;
- дата создания в Unix timestamp.

## Архитектура

```
                    ┌─────────────────┐
                    │     MiniCRM     │
                    │   WEB / CRM     │
                    └────────┬────────┘
                             │
                          FastAPI
                             │
                        PostgreSQL
                             ▲
                             │
                       Telegram Bot
```

Web — главный интерфейс. Bot — интеграционный канал.

## Стек

- Python 3.12+
- FastAPI
- psycopg 3
- PostgreSQL
- aiogram 3
- HTML / CSS / JavaScript
- Nginx

## Структура

```
minicrm/
│
├── index.html
├── app.js
├── style.css
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── api.py
│   └── bot.py
│
├── assets/
│   └── bot_welcome.jpg
│
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── README.md
```

**index.html не является частью backend/frontend-фреймворка и остаётся в корне проекта.** Веб-часть главнее бота.

## Deployment

Для текущего MVP используется обычный запуск Python + Nginx. Docker-файлы остаются для воспроизводимой упаковки проекта, но на небольшом VPS Docker не обязателен.

## Принцип разработки

Это тестовое задание. Не строим Enterprise-систему.

Сначала рабочий контур, затем только необходимое для MVP. Архитектура остаётся простой и прозрачной.
