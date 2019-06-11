# echo client
import socket
from OpenSSL import SSL
from hexdump import hexdump

import argparse

argsParser = argparse.ArgumentParser(description="SSL client")
argsParser.add_argument("--host", type=str, help="connect to interface", default="localhost")
argsParser.add_argument("--port", type=int, help="connect to port", default=9999)

args = argsParser.parse_args()

HOST = args.host
PORT = args.port
BUFFER_SIZE = 4096


ctx = SSL.Context(SSL.SSLv23_METHOD) # latest TLS
# ctx = SSL.Context(SSL.SSLv2_METHOD) # no protocol
# ctx = SSL.Context(SSL.SSLv3_METHOD) # no protocol
# ctx = SSL.Context(SSL.TLSv1_METHOD)
# ctx = SSL.Context(SSL.TLSv1_1_METHOD)
# ctx = SSL.Context(SSL.TLSv1_2_METHOD)

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client = SSL.Connection(ctx, socket)

print("Make SSL Connection to {}:{}".format(HOST, PORT))

try:
    client.connect((HOST, PORT))
except Exception as e:
    print("[!] Failed lah~")
    print(e)
else:
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