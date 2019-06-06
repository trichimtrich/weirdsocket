import socket
import ssl

import select
import queue

from hexdump import hexdump
from OpenSSL import SSL

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server.setblocking(0)

server.bind(('localhost', 9999))
server.listen(5)

print("Server started")

conn, client_addr = server.accept()
print("New client:", client_addr)
print(dir(conn))
print(conn.fileno)

# data = conn.recv(4096)
# hexdump(data)

# if data.startswith(b"\x16"):
if True:
    # ssl
    ctx = SSL.Context(SSL.TLSv1_2_METHOD)
    ctx.use_privatekey_file("my.key")
    ctx.use_certificate_file("my.crt")
    ctx.set_verify(SSL.VERIFY_NONE, lambda : True)
    ctx.set_mode(SSL._lib.SSL_MODE_AUTO_RETRY)

    s2 = SSL.Connection(ctx, conn)
    # s2.bio_write(data)

    s2.set_accept_state()
    try:
        s2.do_handshake()
    except:
        print("Lost")
    else:
        data = s2.recv(4096)
        hexdump(data)
else:
    conn.send(data)


conn.close()
server.close()