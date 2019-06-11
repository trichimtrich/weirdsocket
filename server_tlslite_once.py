# echo server - tlslite - serve once

from tlslite import TLSConnection
from tlslite.recordlayer import RecordLayer, RecordSocket, RecordHeader3, Parser
from tlslite import X509, X509CertChain, parsePEMKey
import socket

import argparse
from hexdump import hexdump

argsParser = argparse.ArgumentParser(description="Experiment using tlslite-ng module as wrapper and pure TLS")
argsParser.add_argument("--host", type=str, help="listen interface", default="localhost")
argsParser.add_argument("--port", type=int, help="listen port", default=9999)
argsParser.add_argument("--cert", type=str, help="server certificate", default="cert/my.crt")
argsParser.add_argument("--key", type=str, help="server private key", default="cert/my.key")

args = argsParser.parse_args()

HOST = args.host
PORT = args.port
CERT = args.cert
KEY = args.key
BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("Server started at {}:{}".format(HOST, PORT))

conn, client_addr = server.accept()
print("New client:", client_addr)


# TLSConnection -> _recordLayer (RecordLayer) -> _recordSocket (RecordSocket)
class MyRecordSocket(RecordSocket):
    def __init__(self, sock, data):
        super().__init__(sock)
        self._amazingData = data
        self._startOfSomethingAmazing = True

    def recv(self):
        if self._startOfSomethingAmazing:
            self._startOfSomethingAmazing = False
            # assume it is SSL3 header, who cares about SSL2 ?
            record = RecordHeader3().parse(Parser(self._amazingData))
            return (record, self._amazingData[5:]), 
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

isTLS = ""
isRunning = True

if data.startswith(b"\x16\x03"):
    print(">> Detect ssl request")

    # ssl context
    x509 = X509()
    x509.parse(open(CERT).read())
    certChain = X509CertChain([x509])
    privateKey = parsePEMKey(open(KEY).read(), private=True)

    # wrap it with modified class
    connection = MyTLSConnection(conn, data)

    # resume the handshake
    try:
        connection.handshakeServer(certChain=certChain, privateKey=privateKey, reqCert=True)
    except:
        print(">> Failed to switch ssl")
    else:
        print(">> Upgraded")
        conn = connection
        isTLS = "[TLS] "
else:
    # its not ssl context, so we send back the first packet / or quit
    if data.startswith(b"quit"):
        isRunning = False
    else:
        conn.send(data)

# loop
while isRunning:
    try:
        data = conn.recv(BUFFER_SIZE)
    except:
        # tlslite socket error
        break

    # client closed
    if not data:
        break

    print("> {}Recv: {} bytes".format(isTLS, len(data)))
    hexdump(data)
    if data.startswith(b"quit"):
        break
    conn.send(data)

conn.close()
server.close()