# web server - msgpeek - twisted - geeky solution, demo only

from twisted.web import server, resource, http
from twisted.internet import reactor
from twisted.internet import ssl
from twisted.internet.threads import deferToThread
import socket

HOST =  "localhost"
PORT = 9999
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
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        return content.encode("ascii")

cert = ssl.PrivateCertificate.loadPEM(open("cert/my.pem", "rb").read())
s = server.Site(Counter())
s.protocol = lambda: http._GenericHTTPChannelProtocol(myHTTPChannel())
s.options = cert.options()

reactor.listenTCP(PORT, s, interface=HOST)
print("Server started")
reactor.run()