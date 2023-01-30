import xmlrpc.client
import random
import hmac
import hashlib


class XMLRPCClient:
    def __init__(self, server_proxy):
        self.proxy = xmlrpc.client.ServerProxy(server_proxy)
        self.private_key = int
        self.session_id = str
        self.challenge = str

    def authorization(self, login, password):
        response = self.proxy.authorization(login, password)
        try:
            response = xmlrpc.client.loads(response)
            self.session_id = response[0][0]
            return self.session_id
        except xmlrpc.client.Fault as f:
            print(f.faultString)

    def generate_private_key(self,
                             base=random.randint(2 ** 10, 2 ** 20),
                             pow=random.randint(2 ** 10, 2 ** 20),
                             mod=random.randint(2 ** 10, 2 ** 20)):

        partial_client_key = base ** pow % mod
        response = self.proxy.generate_private_key(self.session_id, partial_client_key, base, mod)
        try:
            self.private_key = xmlrpc.client.loads(response)[0][0] ** pow % mod
            return self.private_key
        except xmlrpc.client.Fault as f:
            print(f.faultString)

    def get_challenge(self):
        response = self.proxy.get_challenge(self.session_id)

        try:
            self.challenge = xmlrpc.client.loads(response)[0][0]
            return self.challenge
        except xmlrpc.client.Fault as f:
            print(f.faultString)

    def get_value_from_database(self, data_key):
        sign = hmac.new(key=bytes(str(self.private_key), encoding='utf-8'),
                        msg=bytes(self.challenge, encoding='utf-8'),
                        digestmod=hashlib.sha256).hexdigest()

        response = self.proxy.get_value_from_database(self.session_id, data_key, sign)
        try:
            value = xmlrpc.client.loads(response)[0][0]
            return value
        except xmlrpc.client.Fault as f:
            print(f.faultString)


if __name__ == '__main__':
    client = XMLRPCClient('http://localhost:8001/')
    print(client.authorization('login', 'password'))
    print(client.generate_private_key())
    print(client.get_challenge())
    print(client.get_value_from_database('somthing_key'))
