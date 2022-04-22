# Запуск prod-версии сайта через Docker

Убедитесь, что у вас установлен [Docker](https://www.docker.com/):
```shell
$ docker --version
```

Перейдите в каталог `production`:

```shell
$ cd production
```

Создайте файл `.env.prod` с переменными окружения. Добавьте следующие переменные в формате
`ПЕРЕМЕННАЯ=значение`:

- `DEBUG` — дебаг-режим. Поставьте `False`.
- `ALLOWED_HOSTS` - список обслуживаемых хостов [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts).
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте. Не стоит использовать значение по-умолчанию, **замените на своё**.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)
- `YANDEX_API_KEY` — API ключ Яндекс-геокодера. [Как получить](https://developer.tech.yandex.ru/services/).
- `ROLLBAR_TOKEN` - токен от [Rollbar](https://rollbar.com).
- `ROLLBAR_ENVIRONMENT` - окружение, в котором запускается сервер. По умолчанию - `development`.
- `DATABASE_URL` - URl используемой бд. [Шаблоны URL](https://github.com/jacobian/dj-database-url#:~:text=unlimited%20persistent%20connections.-,URL%20schema,-Engine).

В качестве значение `DATABASE_URL` должно быть `postgres://postgres:postgres@db:5432/star_burger` - url базы, 
запущенной в контейнере. Если вы хотите использовать какую-то другую бд, то укажите ее url.

В список обслуживаемых хостов (`ALLOWED_HOSTS`) должны входить следующие значения: `127.0.0.1,localhost,star_burger`.

В качестве `ROLLBAR_ENVIRONMENT` можете поставить `production`.

Запустите деплойный скрипт:
```shell
$ ./deploy.sh
```

Дождитесь завершения процесса деплоя. О готовности вы узнаете по сообщению в консоли:
```
Deploy in production is completed
```

Миграции накатятся автоматически. Чтобы создать суперпользователя, выполните следующую команду:
```shell
$ docker-compose -f docker-compose.yaml -f production/docker-compose.prod.yaml exec web python manage.py createsuperuser
```

Откройте сайт в браузере по адресу [http://127.0.0.1/](http://127.0.0.1/). Сайт работает на дефолтном `80` порту.