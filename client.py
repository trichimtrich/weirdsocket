# echo client
import socket
from OpenSSL import SSL
from hexdump import hexdump

HOST = "localhost"
PORT = 9999
BUFFER_SIZE = 4096

ctx = SSL.Context(SSL.SSLv23_METHOD) # latest TLS
# ctx = SSL.Context(SSL.SSLv2_METHOD) # no protocol
# ctx = SSL.Context(SSL.SSLv3_METHOD) # no protocol
# ctx = SSL.Context(SSL.TLSv1_METHOD)
# ctx = SSL.Context(SSL.TLSv1_1_METHOD)
# ctx = SSL.Context(SSL.TLSv1_2_METHOD)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = SSL.Connection(ctx, socket)

client.connect((HOST, PORT))

while True:
    message = input("message (quit?): ").encode()

    if not message:
        break

    client.send(message)

    if message.startswith(b"quit"):
        print("> Bye!")
        break
    else:
        data = client.recv(BUFFER_SIZE)
        print("> Recv: {} bytes".format(len(data)))
        hexdump(data)

client.close()