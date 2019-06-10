# echo server - serve once
from tlslite import TLSConnection
from tlslite.recordlayer import RecordLayer, RecordSocket, RecordHeader3, Parser
import socket
from hexdump import hexdump
from tlslite import X509, X509CertChain, parsePEMKey

HOST = "localhost"
PORT = 9999
BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("Server started")

conn, client_addr = server.accept()
print("New client:", client_addr)


x509 = X509()
x509.parse(open("cert/my.crt").read())
certChain = X509CertChain([x509])
privateKey = parsePEMKey(open("cert/my.key").read(), private=True)

# TLSConnection -> _recordLayer (RecordLayer) -> _recordSocket (RecordSocket)
class MyRecordSocket(RecordSocket):
    def __init__(self, sock, data):
        super().__init__(sock)
        self._amazingData = data
        self._startOfSomethingAmazing = True

    
    def recv(self):
        if self._startOfSomethingAmazing:
            print("Is that it?")
            record = RecordHeader3().parse(Parser(self._amazingData))
            self._startOfSomethingAmazing = False
            yield (record, self._amazingData[5:])
        else:
            return super().recv()


class MyRecordLayer(RecordLayer):
    def __init__(self, sock, data):
        super().__init__(sock)
        self._recordSocket = MyRecordSocket(sock, data)


class MyTLSConnection(TLSConnection):
    def __init__(self, sock, data):
        super().__init__(sock)
        self._recordLayer = MyRecordLayer(sock, data)


# recv first packet
data = conn.recv(BUFFER_SIZE)
hexdump(data)
connection = MyTLSConnection(conn, data)
# connection = TLSConnection(conn)
connection.handshakeServer(certChain=certChain, privateKey=privateKey, reqCert=True)


# loop
while True:
    try:
        data = connection.recv(BUFFER_SIZE)
    except SSL.Error:
        # ssl socket error
        break

    # client closed
    if not data:
        break

    print("> Recv: {} bytes".format(len(data)))
    hexdump(data)
    if data.startswith(b"quit"):
        break
    connection.send(data)

conn.close()
server.close()