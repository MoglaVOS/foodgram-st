# Foodgram
![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)
![Nginx](https://img.shields.io/badge/Nginx-009639?logo=nginx&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
***

### Описание

Foodgram — это удобное приложение, позволяющее пользователям создавать и делиться своими рецептами, добавлять их в
избранное, формировать списки покупок и подписываться на авторов.
***

### Команды развертывания

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
- Создадим суперпользователя

```
docker compose exec backend python manage.py createsuperuser
```

- Импортируем ингредиенты

```
docker compose exec backend python manage.py loaddata ./data/ingredients.json
```

#### 5. Примеры запросов к API
- [Главная страница](http://localhost/)
- [Панель администратора](http://localhost/admin/)
- [Документация к API](http://localhost/api/docs/)
   

>Автор: Юрин Андрей
> [GitHub](https://github.com/MoglaVOS)
> [Telegram](https://t.me/shiverof)

