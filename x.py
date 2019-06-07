# echo server - serve once

import socket
from hexdump import hexdump
from OpenSSL import SSL

# ssl
'''
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_alpn_select_callback_args', '_app_data', '_context', '_from_ssl', '_get_finished_message', '_handle_bio_errors', '_into_ssl', '_npn_advertise_callback_args', '_npn_select_callback_args', '_raise_ssl_error', '_reverse_mapping', '_socket', '_ssl', 'accept', 'bio_read', 'bio_shutdown', 'bio_write', 'client_random', 'connect', 'connect_ex', 'do_handshake', 'export_keying_material', 'get_alpn_proto_negotiated', 'get_app_data', 'get_certificate', 'get_cipher_bits', 'get_cipher_list', 'get_cipher_name', 'get_cipher_version', 'get_client_ca_list', 'get_context', 'get_finished', 'get_next_proto_negotiated', 'get_peer_cert_chain', 'get_peer_certificate', 'get_peer_finished', 'get_protocol_version', 'get_protocol_version_name', 'get_servername', 'get_session', 'get_shutdown', 'get_state_string', 'makefile', 'master_key', 'pending', 'read', 'recv', 'recv_into', 'renegotiate', 'renegotiate_pending', 'request_ocsp', 'send', 'sendall', 'server_random', 'set_accept_state', 'set_alpn_protos', 'set_app_data', 'set_connect_state', 'set_context', 'set_session', 'set_shutdown', 'set_tlsext_host_name', 'shutdown', 'sock_shutdown', 'total_renegotiations', 'want_read', 'want_write', 'write']
'''

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


class supermagic(SSL.Connection):
    def bio_read(self, bufsiz):
        print("bio_read")
        return super().bio_read(bufsiz)
    
    def bio_write(self, buf):
        print("bio_write")
        return super().bio_write(buf)

    def recv(self, bufsiz, flags=None):
        print("recv")
        return super().recv(bufsiz, flags)
    read = recv

    def send(self, buf, flags=0):
        print("send")
        return super().send(buf, flags)
    write = send


is_tls = ""

# check if ssl context
if data.startswith(b"\x16\x03"):
    print(">> Detect ssl request")

    # ssl
    ctx = SSL.Context(SSL.SSLv23_METHOD)
    ctx.use_privatekey_file("cert/my.key")
    ctx.use_certificate_file("cert/my.pem")
    sock = SSL.Connection(ctx)
    # sock = supermagic(ctx)

    sock.set_accept_state()
    sock.do_handshake()

    print("hello dellila")

    sock.bio_write(data)
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

