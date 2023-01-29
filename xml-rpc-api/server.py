import datetime
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from database import Database
from uuid import uuid4
from xmlrpc.client import Fault


class XMLRPCServer:
    def __init__(self, address, port, database: Database, user_session_alive_time_seconds=3600):
        self.address = address
        self.port = port
        self.database: Database = database
        self.user_session_alive_time_sec = user_session_alive_time_seconds

    def start(self):
        with SimpleXMLRPCServer((self.address, self.port)) as xml_rpc_server:
            xml_rpc_server.register_introspection_functions()

            # @xml_rpc_server.register_function()
            # def registration(login, user_password):
            #     db.save_user(login, user_password)
            #     return 'Success'

            @xml_rpc_server.register_function()
            def authorization(login, user_password):
                original_password = self.database.get_password_by_login(login)

                if original_password is not None and original_password[0] == user_password:
                    start_session_time = datetime.datetime.now()
                    session_alive_up_time = start_session_time + datetime.timedelta(
                        seconds=self.user_session_alive_time_sec)

                    session_id = uuid4().int

                    self.database.save_session(session_id, login, start_session_time, session_alive_up_time)

                    return str(session_id)
                    # return xmlrpc.client.dumps(str(session_id), methodresponse=True)
                else:
                    return xmlrpc.client.dumps(Fault(1, 'Authorization error'), methodresponse=True)

            @xml_rpc_server.register_function()
            def get_value_from_database():
                pass

            @xml_rpc_server.register_function()
            def generate_secret():
                pass

            @xml_rpc_server.register_function()
            def get_challenge():
                pass

            xml_rpc_server.serve_forever()


if __name__ == '__main__':
    dbname = "xml-rpc-db"
    host = 'localhost'
    user = 'admin'
    password = 'admin'
    db = Database(dbname, host, user, password)
    server = XMLRPCServer('localhost', 8000, db)

    server.start()
