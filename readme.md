# TeamFinder

TeamFinder - веб-приложение для поиска команды и участников в учебные или pet-проекты. Пользователи могут регистрироваться, заполнять профиль, создавать проекты, указывать нужные навыки, присоединяться к чужим проектам и просматривать карточки участников.

## Возможности

- регистрация, вход, выход, редактирование профиля и смена пароля;
- кастомная модель пользователя с авторизацией по email;
- список пользователей и публичные страницы профилей;
- создание, редактирование и завершение проектов;
- участие пользователей в проектах;
- навыки проекта с добавлением и удалением через AJAX;
- фильтр проектов по навыку;
- пагинация списков проектов и пользователей;
- админ-панель для пользователей, проектов и навыков;
- команда для заполнения демо-данными.

## Стек

- Python 3.10+
- Django 5.2
- PostgreSQL
- Docker Compose
- Pillow
- python-decouple
- HTML, CSS, JavaScript

## Настройка окружения

Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
```

Windows PowerShell:

```bash
venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

## Переменные окружения

Скопируйте пример настроек:

```bash
cp .env_example .env
```

Заполните `.env`:

| Переменная | Назначение |
| --- | --- |
| `DJANGO_SECRET_KEY` | Секретный ключ Django. |
| `DJANGO_DEBUG` | Режим отладки: `True` для разработки, `False` для проверки и продакшена. |
| `DJANGO_ALLOWED_HOSTS` | Разрешенные хосты через запятую. |
| `USE_SQLITE` | `True` включает SQLite для быстрой локальной проверки, `False` использует PostgreSQL. |
| `POSTGRES_DB` | Имя базы данных PostgreSQL. |
| `POSTGRES_USER` | Имя пользователя PostgreSQL. |
| `POSTGRES_PASSWORD` | Пароль пользователя PostgreSQL. |
| `POSTGRES_HOST` | Хост PostgreSQL. |
| `POSTGRES_PORT` | Порт PostgreSQL. |

## Запуск PostgreSQL

Запустите базу данных:

```bash
docker compose up -d
```

Остановить контейнеры можно командой:

```bash
docker compose down
```

Если Docker недоступен, для локальной проверки можно временно указать в `.env`:

```bash
USE_SQLITE=True
```

Для финальной проверки по заданию используйте PostgreSQL.

## Запуск проекта

Примените миграции:

```bash
python manage.py migrate
```

Создайте демо-данные:

```bash
python manage.py seed_demo
```

Демо-пользователи:

- `anna@example.com`
- `pavel@example.com`
- `maria@example.com`

Пароль для всех демо-пользователей: `password123`.

Запустите сервер разработки:

```bash
python manage.py runserver
```

Приложение будет доступно по адресу http://localhost:8000/.

## Автор

Автор: Артем

Для связи можно использовать email или профиль GitHub, указанный в вашем репозитории.
