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

### Почему без ORM

Используем прямой PostgreSQL через **psycopg**.

SQLAlchemy, Alembic, asyncpg и другие дополнительные слои сознательно не используются: для этого MVP они не дают необходимой ценности и только увеличивают объём проекта.

Принцип: **минимум кода и зависимостей, максимум рабочего контура.**

## База данных

Всего 3 таблицы.

### leads

- id — BIGSERIAL PK
- name — VARCHAR(150)
- contact — VARCHAR(255)
- request — TEXT
- source — VARCHAR(50)
- created_at — BIGINT, Unix timestamp

### tags

- id — BIGSERIAL PK
- name — VARCHAR(50), UNIQUE

### lead_tags

- lead_id — FK → leads.id
- tag_id — FK → tags.id
- PRIMARY KEY (lead_id, tag_id)

Никаких users, roles, pipelines, activities, audit logs и прочих сущностей в MVP нет.

## API

Планируем минимальный REST API:

- GET /api/leads
- GET /api/leads/{id}
- POST /api/leads
- POST /api/leads/{id}/tags
- DELETE /api/leads/{id}/tags/{tag}
- GET /api/tags
- GET /api/leads?tag=hot

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

## Definition of Done

1. Открыть CRM.
2. Добавить лид вручную.
3. Увидеть его в списке.
4. Добавить тег.
5. Отфильтровать по тегу.
6. Отправить данные боту.
7. Увидеть созданный ботом лид в CRM.

## Принцип разработки

Это тестовое задание. Не строим Enterprise-систему.

Сначала рабочий контур, затем только необходимое для MVP. Архитектура остаётся простой и прозрачной.
