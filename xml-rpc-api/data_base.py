from psycopg2 import connect, extensions, sql

dbname = "xml-rpc-db"
host = 'localhost'
user = 'postgres'
password = 'admin1234'

try:
    connection = connect(
        dbname=dbname,
        user=user,
        host=host,
        password=password)

    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')

        print(cursor.fetchone())


except Exception as e:
    print("Somthing went wrong!")
finally:
    pass
    # if connection:
    #     connection.close()
