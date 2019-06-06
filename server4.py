from twisted.internet import protocol, reactor, endpoints
from twisted.internet import ssl

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        print("Recv len:", len(data))

        
        print(dir(self.transport))

        if data.startswith(b"\x16"):
            print("Switch to TLS")
            self.transport.startTLS(self.factory.options)
        else:
            self.transport.write(data)


cert = ssl.PrivateCertificate.loadPEM(open("my.pem", "rb").read())
factory = protocol.Factory.forProtocol(Echo)
factory.options = cert.options()

endpoints.serverFromString(reactor, "tcp:9999").listen(factory)
reactor.run()