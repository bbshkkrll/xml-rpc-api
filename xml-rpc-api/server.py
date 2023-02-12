import datetime
import hashlib
import hmac
import random
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
from database import Database
from uuid import uuid4
from xmlrpc.client import Fault
from session import Session


class XMLRPCServer:
    def __init__(self, address, port, database: Database, user_session_alive_time_seconds=3600):
        self.address = address
        self.port = port
        self.database: Database = database
        self.user_session_alive_time_sec = user_session_alive_time_seconds

    @staticmethod
    def _is_session_alive(user_session_id):
        session_params = db.get_session_by_id(user_session_id)

        if session_params is not None:
            session = Session(session_params)
            return session.session_id == user_session_id and (
                    session.start_session_time <= datetime.datetime.now() <= session.live_up_time)

        return False

    @staticmethod
    def _get_sign(key, msg):
        return hmac.new(key=bytes(str(key), encoding='utf-8'), msg=bytes(msg, encoding='utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

    @staticmethod
    def _encrypt_password(user_password):
        return hashlib.sha256(user_password.encode()).hexdigest()

    def start(self):
        with SimpleXMLRPCServer((self.address, self.port), allow_none=True) as xml_rpc_server:

            xml_rpc_server.register_introspection_functions()

            @xml_rpc_server.register_function()
            def authorization(login, user_password):
                original_password_hash = self.database.get_password_by_login(login)
                user_password_hash = self._encrypt_password(user_password)

                if original_password_hash is not None and original_password_hash[0] == user_password_hash:
                    start_session_time = datetime.datetime.now()
                    session_alive_up_time = start_session_time + datetime.timedelta(
                        seconds=self.user_session_alive_time_sec)

                    session_id = uuid4().int

                    self.database.save_session(session_id, login, start_session_time, session_alive_up_time)

                    return xmlrpc.client.dumps((str(session_id),), methodresponse=True)
                else:
                    return xmlrpc.client.dumps(Fault(1, 'FAULT: Authorization error'), methodresponse=True)

            @xml_rpc_server.register_function()
            def generate_private_key(session_id, partial_client_key, base, module):
                if self._is_session_alive(session_id):
                    power = random.randint(2 ** 10, 2 ** 20)
                    partial_server_key = base ** power % module
                    private_key = partial_client_key ** power % module

                    db.save_private_key(session_id, private_key)

                    return xmlrpc.client.dumps((partial_server_key,), methodresponse=True)
                else:
                    return xmlrpc.client.dumps(Fault(1, 'FAULT: Your session is terminate, please start new session'),
                                               methodresponse=True)

            @xml_rpc_server.register_function()
            def get_challenge(session_id):
                if self._is_session_alive(session_id):
                    current_challenge = str(datetime.datetime.now())
                    db.save_current_challenge(session_id, current_challenge)
                    return xmlrpc.client.dumps((current_challenge,), methodresponse=True)

                return xmlrpc.client.dumps(Fault(1, 'FAULT: Your session is terminate, please start new session'),
                                           methodresponse=True)

            @xml_rpc_server.register_function()
            def get_value_from_database(session_id, data_key, sign):
                if self._is_session_alive(session_id):
                    session_data = db.get_session_data_by_session_id(session_id)
                    if session_data is not None:
                        private_key, current_challenge = session_data
                        sever_sign = self._get_sign(key=private_key, msg=current_challenge)

                        if sever_sign == sign:
                            response_data = db.get_application_data_by_key(data_key)
                            if response_data is not None:
                                return xmlrpc.client.dumps((response_data,), methodresponse=True)
                        else:
                            return xmlrpc.client.dumps(Fault(1, 'FAULT: Wrong key, try again.'))
                else:
                    return xmlrpc.client.dumps(Fault(1, 'FAULT: Your session is terminate, please start new session'))

            xml_rpc_server.serve_forever()


if __name__ == '__main__':
    dbname = "xml-rpc-db"
    host = 'localhost'
    user = 'admin'
    password = 'admin'
    db = Database(dbname, host, user, password)
    server = XMLRPCServer('localhost', 8001, db)

    server.start()
