# xml-rpc-api
Используя только средства стандартных библиотек Python 3.8 (кроме работы с БД) написать http-сервер реализующий XMLRPC API.

1) Служебная БД на PostgreSQL

- таблица с учетными записями (логин, пароль)

- таблица со прикладными данными (ключ, какое-то строковое значение)

2) Сервис должен иметь XMLRPC-запросы (методы)

- метод авторизации

- метод получения данных из БД, с подписью запроса секретом

- методы для выработки секрета по алгоритму Диффи-Хеллмана

- метод запроса челленджа

3) Метод авторизации

- в параметрах запроса принять строки логина и пароля

- проверить пароль по таблице учетных записей

- создать "сессию" с ограниченным временем жизни для этого логина

- вернуть идентификатор сессии, если ок, либо ошибку авторизации

4) Метод выработки секрета

- выработать с клиентской стороной разделяемый секрет по алгоритму Диффи-Хеллмана

- прикрепить полученный секрет к "сессии"

5) метод запроса челленджа

- сформировать случайную строку челленджа

- прикрепить челлендж к "сессии"

- вернуть челлендж.

6) Метод чтения из БД данных по ключу БД, с подписью запроса секретом

- в параметрах запроса получить идентификатор "сессии"

- в параметрах запроса получить ключевое значение для выборки из БД

- в параметрах запроса получить подпись челленджа на выработанном секрете (см. п. 7)

- проверить подпись челленджа, в случае неуспешной проверки вернуть ошибку

- выполнить выборку из БД

- вернуть полученное значение.

7) Подпись на клиентской стороне

- функция HMAC

- алгоритм SHA256

- ключ - выработанный секрет

- данные - полученный челлендж

## Подготовка
Чтобы запустить приложение, предварительно необходимо создать базу данных и добавить записиси:
1) В таблицу users (_insert into users values ('login', 'password')_)
2) В таблицу application_data (insert into application_data values (_'somthing_key', 'something_data'))
## Запуск
1) Запустить server.py
2) Запустить client.py со своими параметрами
