# Foodgram

***

### Описание

Foodgram — это удобное приложение, позволяющее пользователям создавать и делиться своими рецептами, добавлять их в
избранное, формировать списки покупок и подписываться на авторов.
***

### Как запустить приложение

#### 1. Клонировать репозиторий

```
git clone https://github.com/MoglaVOS/foodgram-st.git
сd foodgram-st
```

#### 2. Подготовить файл '.env'

Создайте в директории infra файл '.env' и заполните его данными из файла '.env.example'.

#### 3. Запуск приложения

```
# Выполните команду находясь в директории infra
docker compose up -d --build
```

#### 4. Наполнение данными и получение статики

- Выполним миграции

```
docker compose exec backend python manage.py migrate
```

- Соберём статику

```
docker compose exec backend python manage.py collectstatic --no-input
docker compose restart
```

- Наполним бд

```
docker compose exec backend python manage.py loaddata example_data/ingredients.json
```

#### 5. Примеры запросов к API

Адрес Описание

- http://localhost/    Главная страница
- http://localhost/admin/    Панель администратора
- http://localhost/api/docs/    Документация к API
