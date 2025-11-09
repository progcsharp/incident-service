
# Incident API

Асинхронный сервис для регистрации и просмотра инцидентов. Реализован на FastAPI с поддержкой PostgreSQL (через SQLAlchemy) и кэшем Redis для ускорения чтения списков инцидентов.

## Возможности
- Создание инцидентов с валидацией входных данных на уровне схем Pydantic.
- Получение списка инцидентов с пагинацией и фильтрацией по статусу/источнику.
- Кэширование результатов `GET /incident/get` на стороне Redis (1 час) с автоматической инвалидизацией при изменении данных.
- Получение конкретного инцидента по идентификатору.
- Обновление статуса существующего инцидента.
- Единый декоратор `log_route` для логирования запросов и ответов (место для будущей записи логов в базу).

## Технологии
- FastAPI, Pydantic v2
- SQLAlchemy 2.x (async engine, async sessionmaker)
- PostgreSQL, Alembic
- Redis (asyncio client)
- Docker, Docker Compose
- python-dotenv

## Ключевые компоненты
- `app.py` — создание FastAPI-приложения и подключение роутера инцидентов, настройка жизненного цикла (lifespan) для Redis.
- `routers/incident.py` — CRUD-эндпоинты для работы с инцидентами.
- `schemas/incident.py` — Pydantic-схемы `Incident` и `IncidentResponse`.
- `db/models.py` — модель `Incident`, описанная через SQLAlchemy.
- `db/handler/*` — прикладная логика работы с базой (create/get/update).
- `db/engine.py` и `db/config.py` — настройка асинхронного движка SQLAlchemy и параметров подключения.
- `redis_core/redis.py` — инициализация клиента Redis в lifespan, зависимость `get_redis`.
- `utils/logging.py` — декоратор для логирования запросов/ответов.
- `alembic/` — инфраструктура миграций, первая миграция создаёт таблицу `Incident`.

## Структура проекта
```
.
├─ app.py
├─ config.py
├─ docker-compose.yml
├─ Dockerfile
├─ requirements.txt
├─ alembic/
│  ├─ env.py
│  ├─ versions/
│  │  └─ dadc1db062ae_init_migrations.py
├─ db/
│  ├─ config.py
│  ├─ engine.py
│  ├─ handler/
│  ├─ models.py
│  └─ utils.py
├─ enums/
│  └─ inedent.py
├─ redis_core/
│  └─ redis.py
├─ routers/
│  └─ incident.py
├─ schemas/
│  └─ incident.py
└─ utils/
   └─ logging.py
```

## Переменные окружения
Приложение ожидает `.env` в корне проекта (используется `python-dotenv`), например:

```
POSTGRES_DB=fastapi_test
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=0
DB_ECHO=True
```

> Значения по умолчанию зашиты в `db/config.py` и `alembic/env.py`, но для продакшена рекомендуется использовать переменные окружения.

## Запуск через Docker Compose
1. Создайте `.env` (см. пример выше). Файл используется как для приложения, так и для сервисов в `docker-compose.yml`.
2. Соберите и поднимите стек:
   ```bash
   docker compose up --build
   ```
3. Команда сборки выполнит:
   - установку зависимостей;
   - прогон миграций `alembic upgrade head`;
   - запуск Uvicorn на порту `8000`.
4. Приложение будет доступно по адресу `http://localhost:8000`. Swagger UI: `http://localhost:8000/docs`.

## Локальный запуск (без Docker)
1. Создайте и активируйте виртуальное окружение (Python ≥ 3.11).
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустите PostgreSQL и Redis (локально или через любые контейнеры) и убедитесь, что `.env` корректно настроен.
4. Примените миграции:
   ```bash
   alembic upgrade head
   ```
5. Запустите приложение:
   ```bash
   uvicorn app:app --reload
   ```

## Работа с миграциями
- Создать новую миграцию:
  ```bash
  alembic revision --autogenerate -m "описание изменений"
  ```
- Применить миграции:
  ```bash
  alembic upgrade head
  ```
- Откатить последнюю миграцию:
  ```bash
  alembic downgrade -1
  ```

## API
| Method | Path | Описание | Параметры | Кэш |
|--------|------|----------|-----------|-----|
| `POST` | `/incident/create` | Создаёт новый инцидент. | Body: `Incident` | Инвалидирует кэш списка. |
| `GET` | `/incident/get` | Возвращает список инцидентов. | Query: `page` (1), `limit` (10), `status` (`new/completed/failed`), `source` (`operator/monitoring/partner`) | Результат кэшируется в Redis на 3600 сек с ключом `incidents:{page}:{limit}:{status}:{source}`. |
| `GET` | `/incident/get/{incident_id}` | Возвращает инцидент по ID. | Path: `incident_id` | Нет |
| `PATCH` | `/incident/update-status` | Обновляет статус инцидента. | Query: `incident_id`, `status` | Инвалидирует кэш списка. |

### Схемы
- `Incident` — тело запроса для создания (`incident_message`, `incident_type`, `source`). Строка сообщения валидируется: длина 5–1000, запрещены «test», «none», «null».
- `IncidentResponse` — ответ API, включает `incident_id`, `incident_message`, `incident_type`, `source`, `created_at` (формат `YYYY-MM-DD HH:MM:SS`).
- Статусы (`IncidentStatus`): `new`, `completed`, `failed`.
- Источники (`IncidentSource`): `operator`, `monitoring`, `partner`.

## Кэширование
- Cписки инцидентов кэшируются на 1 час.
- Любое создание или обновление статуса очищает кэш по шаблону `incidents:*`.
- Подключение к Redis создаётся в lifespan FastAPI, при запуске сервис проверяет соединение (`redis.ping()`), неуспех приводит к HTTP 500.

## Логирование
- Декоратор `@log_route()` добавляет базовое логирование начала/завершения запроса.
- Текущая реализация выводит сообщения в stdout и включает заготовку для записи логов в базу (TODO).
- Для расширенного логирования настройте стандартный модуль `logging` или доработайте декоратор.
