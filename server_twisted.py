# echo server - twisted

from twisted.internet import protocol, reactor
from twisted.internet import ssl
from twisted.internet.threads import deferToThread
import socket

HOST = "localhost"
PORT = 9999
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
        self.transport.write(data)


cert = ssl.PrivateCertificate.loadPEM(open("cert/my.pem", "rb").read())
factory = protocol.Factory.forProtocol(Echo)
factory.options = cert.options()

reactor.listenTCP(PORT, factory, interface=HOST)

print("Server started")

reactor.run()