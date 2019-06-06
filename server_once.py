# echo server - serve once
import socket
from hexdump import hexdump
from OpenSSL import SSL

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

# recv first packet in peek mode
data = conn.recv(BUFFER_SIZE, socket.MSG_PEEK)
hexdump(data)

is_tls = ""

# check if ssl context
if data.startswith(b"\x16\x03"):
    print(">> Detect ssl request")

    # ssl
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.use_privatekey_file("my.key")
    ctx.use_certificate_file("my.pem")
    sock = SSL.Connection(ctx, conn)

    sock.set_accept_state()
    try:
        sock.do_handshake()
    except:
        print(">> Failed to switch ssl")
    else:
        conn = sock
        is_tls = "[TLS] "
else:
    # 
    pass

# loop
while True:
    try:
        data = conn.recv(BUFFER_SIZE)
    except SSL.Error:
        # ssl socket error
        break

    # client closed
    if not data:
        break

    print("> {}Recv: {} bytes".format(is_tls, len(data)))
    hexdump(data)
    if data.startswith(b"quit"):
        break
    conn.send(data)

conn.close()
server.close()