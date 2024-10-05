# Имя проекта: Foodgram 
# Ссылка [foodgram](https://foodgram-free.sytes.net/recipes)

# Описание: 
Проект позволяет вести список рецептов, словно кулинарный блог. В проекте есть возможность подписаться на блоги других пользователей, добавлять любимые рецепты в избранное и в корзину для покупок. Корзина покупок помогает пользователю собрать итоговый лист для покупок с учетов всех ингредиентов. Важно!!! Ингредиенты не дублируется, а суммируются при наличии в нескольких рецептах. 

# Требования 
* Ubuntu System
* DRF, Django Framework
* PostgreeSQL/MySQL/SQLite
* GitActions, GitHub
* Docker, Docker Compose
* Djoser
* React js

# Как запустить проект
<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQq2c44WMARcNfGcqi2TJEdNwzNEnu5EJfhxA&s" width="370" height="200" alt="CYBERMAP">

### Step 1.
Клонируйте данный репозиторий на локальное устройство, командой
```
git clone https://github.com/Vladislav-ing/foodgram.git
```
Создайте виртуальное окружение в корне backend части
```
python3 -m venv venv
```
Активируйте вирт. окружение командой
```
python3 source venv/bin/activate (Linux command)
```
Установите зависимости для back-end проекта.
```
pip install -r requirements.txt
``` 
### Step 2.
Создайте переменные окружения.
* Backend(.env)
```
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- SECRET_KEY
- DB_HOST
- DB_PORT
```

*Для генерации SECRET_KEY в Django, выполните команду в терминале: 
```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
* Action(secrets for workflow at CI/CD process)
```
- DOCKER_PASSWORD
- DOCKER_USERNAME
- HOST
- SECRET_KEY
- SSH_KEY
- SSH_PASSPHRASE
- TELEGRAM_TO
- TELEGRAM_TOKEN
- USER
```

#### Образы для развертывания/деплоя на сервер
- https://hub.docker.com/repositories/vhlinkos

### Step 3.
Установите docker, проверьте его доступность
```
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```
Далее выполните установку docker-compose 
```
Установка:
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```
Проверка версии и доступности:
```
docker-compose --version
```
Выполните скачивание образов и создание контейнерев при помощи команды
```
sudo docker compose -f имя_фала_compose.yml up (-d)
```
### Step 4.

Соберите статику для бэка и примените миграции
```
sudo docker compose -f имя_фала_compose.yml exec backend python manage.py migrate

sudo docker compose -f имя_фала_compose.yml exec backend python manage.py collectstatic

sudo docker compose -f имя_фала_compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

## Дополнительно:
При выполнении git-push(MAIN/MASTER branch) в репозиторий проекта, выполняется workflow согласно условиям on, и задачам из jobs.

## Доступы
1. Уровень пользователя.
2. Уровень администратора. 
### Возможности
* Пользователь способен создать рецепт, редактировать и удалить свои рецепты. Подписка на других пользователей, добавление рецепта в избранное,скачивание списка продуктов для рецептов добавленных в корзину, изменение своего логина и автара. 
* Администратор обладает правами обычного пользователя, также имеет доступ к редактированию пользователей, их деактивации и создании. Доступ ко всем рецептам, тэгам, ингредиентам, возможности их создания, удаления и полные права.


## Author by VladislaV Glinka
[Ссылка на телеграм автора](https://t.me/vhlinkos_me)
