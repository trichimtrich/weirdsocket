# web server - msgpeek - twisted - geeky solution, demo only

from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.threads import deferToThread
from OpenSSL import crypto
import socket

import argparse

argsParser = argparse.ArgumentParser(description="Experiment using twisted framework as webserver and MSGPEEK technique")
argsParser.add_argument("--host", type=str, help="listen interface", default="localhost")
argsParser.add_argument("--port", type=int, help="listen port", default=9999)
argsParser.add_argument("--cert", type=str, help="server certificate", default="cert/web.weirdsocket.com.crt")
argsParser.add_argument("--key", type=str, help="server private key", default="cert/web.weirdsocket.com.key")

args = argsParser.parse_args()

HOST = args.host
PORT = args.port
CERT = args.cert
KEY = args.key
BUFFER_SIZE = 4096


class myHTTPChannel(http.HTTPChannel):
    def checkSSLCallback(self, result):
        if result:
            print("[+] Detect https request. Upgrading...")
            self.transport.startTLS(self.factory.options)
        self.transport.socket.setblocking(0)
        self.transport.resumeProducing()


    def checkSSL(self):
        try:
            data = self.transport.socket.recv(BUFFER_SIZE, socket.MSG_PEEK)
            if data.startswith(b"\x16\x03"):
                return True
            return False
        except:
            return False


    def connectionMade(self):
        # pause all callbacks
        self.transport.pauseProducing()

        # set blocking to capture first packet
        self.transport.socket.setblocking(1)

        # run blocking code in another thread and set callback in reactor thread
        d = deferToThread(self.checkSSL)
        d.addCallback(self.checkSSLCallback)

        super().connectionMade()
        

class Counter(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def render_GET(self, request):
        self.numberRequests += 1
        addr = request.getClientAddress()
        print("[{}:{}] GET {}".format(addr.host, addr.port, request.uri.decode()))
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        return content.encode("ascii")


pem_priv = open(KEY, "rb").read()
pem_cert = open(CERT, "rb").read()
priv = ssl.KeyPair.load(pem_priv, format=crypto.FILETYPE_PEM)
cert = ssl.PrivateCertificate.load(pem_cert, priv, format=crypto.FILETYPE_PEM)

s = server.Site(Counter())
s.protocol = lambda: http._GenericHTTPChannelProtocol(myHTTPChannel())
s.options = cert.options()

reactor.listenTCP(PORT, s, interface=HOST)

print("Server started at {}:{}".format(HOST, PORT))
reactor.run()