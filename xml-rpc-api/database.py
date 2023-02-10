from psycopg2 import connect, OperationalError


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
                               'data_key varchar(100) NOT NULL, '
                               'string_value text'
                               ');')

            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE public.sessions('
                               'session_id varchar(50) PRIMARY KEY, '
                               'login varchar(50) references public.users(login) NOT NULL, '
                               'start_session_time timestamp, '
                               'live_up_time timestamp'
                               ')')

            with connection.cursor() as cursor:
                cursor.execute('CREATE TABLE public.session_data('
                               'session_id varchar(50) references public.sessions, '
                               'private_key varchar(10) NOT NULL, '
                               'current_challenge varchar(30)'
                               ')')


        except OperationalError as e:
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

    def get_application_data_by_key(self, data_key):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:

                cursor.execute("select string_value FROM application_data "
                               "where data_key='{0:s}'".format(data_key))

                return cursor.fetchone()
        except OperationalError and ValueError as e:
            raise AttributeError

        finally:
            if connection:
                connection.close()

    def save_user(self, login, user_password):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute("insert into users values ('{0:s}', '{1:s}')".format(login, user_password))

        except OperationalError and ValueError as e:
            raise AttributeError
        finally:
            if connection:
                connection.close()

    def get_password_by_login(self, login: str):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute("select password from users where login='{0:s}'".format(login))

                user_password = cursor.fetchone()
                return user_password

        except OperationalError and ValueError as e:
            raise AttributeError
        finally:
            if connection:
                connection.close()

    def save_session(self, session_id: str, login: str, start_session_time: str, live_up_time: str):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    f"insert into sessions values {0:s} {1:s} {2:s} {3:s}".format(session_id,
                                                                                  login,
                                                                                  start_session_time,
                                                                                  live_up_time))

                connection.commit()
        except OperationalError and ValueError:
            raise AttributeError

        finally:
            if connection:
                connection.close()

    def get_session_by_id(self, session_id):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    "select * from sessions where session_id='{0:s}'".format(session_id)
                )

                session = cursor.fetchone()
                return session

        except OperationalError and ValueError:
            raise AttributeError
        finally:
            if connection:
                connection.close()

    def save_private_key(self, session_id, private_key):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    "insert into session_data(session_id, private_key) values ({0:s}, {1:s})".format(session_id,
                                                                                                     private_key)
                )

                connection.commit()

        except OperationalError and ValueError:
            raise AttributeError

        finally:
            if connection:
                connection.close()

    def save_current_challenge(self, session_id, current_challenge):
        try:
            connection = self.get_connection()

            with connection.cursor() as cursor:
                cursor.execute(
                    "update session_data set current_challenge='{0:s}' where session_id='{1:s}'".format(session_id,
                                                                                                        current_challenge)
                )
                connection.commit()

        except OperationalError and ValueError:
            raise AttributeError

        finally:
            if connection:
                connection.close()

    def get_session_data_by_session_id(self, session_id):
        connection = self.get_connection()

        with connection.cursor() as cursor:
            cursor.execute(
                "select private_key, current_challenge FROM session_data where session_id='{0:s}'".format(session_id)
            )

            session_data = cursor.fetchone()
            return session_data
