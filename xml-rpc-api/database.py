import time
from typing import Tuple, Any

import psycopg2
from psycopg2 import connect, extensions, sql


class Database:
    def __init__(self, dbname, host, user, password):
        self.dbname = dbname
        self.host = host
        self.user = user
        self.password = password

        try:
            connection = self.get_connection()

            connection.autocommit = True
            with connection.cursor() as cursor:
                cursor.execute('DROP SCHEMA IF EXISTS public CASCADE;')
                cursor.execute('CREATE SCHEMA public')

            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE public.users(login varchar(50) PRIMARY KEY NOT NULL, '
                               'password varchar(50) NOT NULL'
                               ')')

            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE public.application_data('
                               'public_key varchar(100) NOT NULL, '
                               'string_value text'
                               ')')

            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE public.sessions('
                               'session_id varchar(50) PRIMARY KEY, '
                               'login varchar(50) references public.users(login) NOT NULL, '
                               'start_session_time timestamp, '
                               'live_up_time timestamp'
                               ')')

        except psycopg2.OperationalError as e:
            raise AttributeError
        finally:
            pass
            if connection:
                connection.close()

    def get_connection(self):

        connection = connect(
            dbname=self.dbname,
            user=self.user,
            host=self.host,
            password=self.password)

        return connection

    def save_user(self, login, user_password):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(f"insert into users values ('{login}', '{user_password}')")

        except psycopg2.OperationalError as e:
            raise AttributeError
        finally:
            if connection:
                connection.close()

    def get_password_by_login(self, login):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(f"select password from users where login='{login}'")

                user_password = cursor.fetchone()
                return user_password

        except psycopg2.OperationalError as e:
            raise AttributeError
        finally:
            if connection:
                connection.close()

    def save_session(self, session_id: str, login: str, start_session_time: str, live_up_time: str):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    f"INSERT INTO sessions values ('{session_id}', '{login}', '{start_session_time}', '{live_up_time}')")

        except psycopg2.OperationalError:
            raise AttributeError

        finally:
            if connection:
                connection.close()


if __name__ == '__main__':
    dbname = "xml-rpc-db"
    host = 'localhost'
    user = 'admin'
    password = 'admin'
    db = Database(dbname, host, user, password)
    time.sleep(5)

    ans = db.get_password_by_login('login')
    print(ans)
