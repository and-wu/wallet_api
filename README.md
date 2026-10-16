# Wallet API

REST API для управления электронными кошельками. Проект разработан на FastAPI с использованием асинхронной работы с PostgreSQL.

## Технологии

- **Python 3.13**
- **FastAPI** — создание REST API
- **SQLAlchemy 2.0** — асинхронная работа с базой данных
- **PostgreSQL 17** — хранение данных
- **Alembic** — миграции базы данных
- **Pydantic Settings** — управление настройками приложения
- **Docker Compose** — запуск приложения и базы данных
- **pytest** — автоматизированное тестирование
- **Ruff** — проверка и форматирование кода

## Возможности

- Создание кошелька с уникальным UUID.
- Получение текущего баланса кошелька.
- Пополнение кошелька.
- Снятие средств с кошелька.
- Проверка достаточности средств перед снятием.
- Обработка параллельных операций с использованием блокировки записи в базе данных для предотвращения некорректного изменения баланса.

## Запуск проекта через Docker Compose

### Требования

- Установленный Docker Desktop с работающим Docker Engine.
- Docker Compose.

### 1. Клонирование репозитория

```bash
git clone <https://github.com/and-wu/wallet_api>
cd wallet_api
```

### 2. Запуск приложения

```bash
docker compose up --build -d
```

Команда соберёт образы, запустит PostgreSQL, применит миграции Alembic и запустит FastAPI.

API будет доступно по адресу:

http://127.0.0.1:8000

Интерактивная документация Swagger:

http://127.0.0.1:8000/docs

### 3. Проверка контейнеров

```bash
docker compose ps
```

Просмотр логов API:

```bash
docker compose logs -f api
```

Просмотр логов миграций:

```bash
docker compose logs migrate
```

### 4. Остановка приложения

```bash
docker compose stop
```

Для повторного запуска:

```bash
docker compose up -d
```

Данные PostgreSQL сохраняются в Docker volume `postgres_data`. Не используйте `docker compose down -v`, если необходимо сохранить данные базы.

## Настройки

Для подключения к PostgreSQL используется переменная окружения `DATABASE_URL`.

Пример URL для локального запуска:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:password@127.0.0.1:5433/wallet_db
```

В Docker Compose приложение подключается к базе по внутреннему адресу сервиса:

```text
postgresql+asyncpg://postgres:password@db:5432/wallet_db
```

Для локального запуска создайте файл `.env` в корне проекта и укажите необходимые настройки. Не добавляйте реальные пароли и другие секреты в публичный репозиторий.

## API

### Создание кошелька

**`POST /api/v1/wallets`**

Создаёт новый кошелёк с нулевым балансом.

Пример ответа:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": "0.00"
}
```

UUID в примере приведён для иллюстрации. Фактическое значение будет сгенерировано при создании кошелька.

### Получение баланса

**`GET /api/v1/wallets/{wallet_id}`**

Пример запроса:

```http
GET /api/v1/wallets/550e8400-e29b-41d4-a716-446655440000
```

Пример ответа:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "balance": "0.00"
}
```

### Пополнение кошелька

**`POST /api/v1/wallets/{wallet_id}/operation`**

Тело запроса:

```json
{
  "operation_type": "DEPOSIT",
  "amount": "100.00"
}
```

### Снятие средств

Для снятия средств используется тот же endpoint.

```json
{
  "operation_type": "WITHDRAW",
  "amount": "30.00"
}
```

После успешного пополнения на 100.00 и снятия 30.00 баланс составит 70.00.

### Обработка ошибок

- `400 Bad Request` — недостаточно средств для снятия.
- `404 Not Found` — кошелёк не найден.
- `422 Unprocessable Entity` — некорректные входные данные.

## Миграции базы данных

При запуске через Docker Compose миграции применяются автоматически.

Для ручного применения миграций при локальном запуске:

```bash
uv run alembic upgrade head
```

Создание новой миграции:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Проверка текущей версии схемы:

```bash
uv run alembic current
```

## Тестирование

Установите зависимости проекта:

```bash
uv sync
```

Укажите URL тестовой базы данных в PowerShell:

```powershell
$env:TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@127.0.0.1:5433/wallet_test_db"
```

Запустите тесты:

```bash
uv run pytest
```

Проверка кода Ruff:

```bash
uv run ruff check .
```

Проверка форматирования:

```bash
uv run ruff format --check .
```

Тесты следует запускать на отдельной тестовой базе данных, чтобы не изменять данные основной базы.

## Структура проекта

```text
wallet_api/
├── alembic/
│   └── versions/       # Миграции базы данных
├── app/
│   ├── api/            # API-маршруты
│   ├── db/             # Настройки базы данных
│   ├── models/         # Модели SQLAlchemy
│   ├── repositories/   # Работа с данными
│   ├── schemas/        # Схемы Pydantic
│   ├── services/       # Бизнес-логика
│   ├── config.py       # Настройки приложения
│   └── main.py         # Точка входа FastAPI
├── tests/              # Автоматизированные тесты
├── .env                # Локальные настройки, не коммитить
├── alembic.ini         # Конфигурация Alembic
├── docker-compose.yml  # Конфигурация сервисов
├── Dockerfile          # Сборка образа приложения
├── pyproject.toml      # Зависимости и настройки инструментов
├── uv.lock             # Зафиксированные версии зависимостей
└── README.md
```

