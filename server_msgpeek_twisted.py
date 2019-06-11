# echo server - msgpeek - twisted

from twisted.internet import protocol, reactor
from twisted.internet import ssl
from twisted.internet.threads import deferToThread
from OpenSSL import crypto
import socket

import argparse

argsParser = argparse.ArgumentParser(description="Experiment using twisted framework as echo server and MSGPEEK technique")
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


class Echo(protocol.Protocol):
    def checkSSLCallback(self, result):
        if result:
            print("[+] Detect SSL hello. Upgrading...")
            self.transport.startTLS(self.factory.options)
        self.transport.socket.setblocking(0)
        self.transport.resumeProducing()


    def checkSSL(self):
        data = self.transport.socket.recv(BUFFER_SIZE, socket.MSG_PEEK)
        if data.startswith(b"\x16\x03"):
            return True
        return False

    def connectionMade(self):
        # pause all callbacks
        self.transport.pauseProducing()

        # set blocking to capture first packet
        self.transport.socket.setblocking(1)

        # run blocking code in another thread and set callback in reactor thread
        d = deferToThread(self.checkSSL)
        d.addCallback(self.checkSSLCallback)


    def dataReceived(self, data):
        print("> {}Recv: {} bytes".format("[TLS] " if self.transport.TLS else "", len(data)))
        if data.startswith(b"quit"):
            self.transport.loseConnection()
        else:
            self.transport.write(data)


pem_priv = open(KEY, "rb").read()
pem_cert = open(CERT, "rb").read()

priv = ssl.KeyPair.load(pem_priv, format=crypto.FILETYPE_PEM)
cert = ssl.PrivateCertificate.load(pem_cert, priv, format=crypto.FILETYPE_PEM)
factory = protocol.Factory.forProtocol(Echo)
factory.options = cert.options()
reactor.listenTCP(PORT, factory, interface=HOST)

print("Server started at {}:{}".format(HOST, PORT))

reactor.run()