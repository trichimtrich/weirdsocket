import socket
import select
import queue

from hexdump import hexdump
from OpenSSL import SSL

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)

server.bind(('localhost', 9999))
server.listen(5)

print("Server started")

inputs = [server]
outputs = []
message_queues = {}

def doClose(s, isServer=False):
    inputs.remove(s)
    if s in outputs:
        outputs.remove(s)
    if not isServer:
        del message_queues[s]
        print("[-] Close client:", s.getpeername())
    else:
        print("Server closed")
    s.close()


while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    
    for s in readable:
        if s is server:
            conn, client_address = s.accept()
            print("[+] New client:", client_address)
            conn.setblocking(0)
            inputs.append(conn)
            message_queues[conn] = queue.Queue()
        else:
            # clients
            data = s.recv(1024)
            if data:
                # handle data
                if data.startswith(b"\x16"):
                    # ssl
                    ctx = SSL.Context(SSL.TLSv1_2_METHOD)
                    ctx.use_privatekey_file("my.key")
                    ctx.use_certificate_file("my.crt")
                    ctx.set_verify(SSL.VERIFY_NONE, lambda : True)
                    ctx.set_mode(SSL._lib.SSL_MODE_AUTO_RETRY)

                    s2 = SSL.Connection(ctx, s)
                    s2.set_accept_state()
                    try:
                        s2.do_handshake()
                    except:
                        print("Lost")
                    else:

                        # do slave
                        inputs.remove(s)
                        inputs.append(s2)
                        if s in outputs:
                            outputs.remove(s)
                            outputs.append(s2)
                        message_queues[s2] = message_queues[s]
                        del message_queues[s]
                        


                elif data.startswith(b"quit"):
                    doClose(s)
                else:
                    message_queues[s].put(data)
                    if s not in outputs:
                        outputs.append(s)
            else:
                # client closed
                doClose(s)
    
    for s in writable:
        try:
            next_msg = message_queues[s].get_nowait()
        except queue.Empty:
            outputs.remove(s)
        else:
            s.send(next_msg)
    
    for s in exceptional:
        # exception of input fd
        doClose(s)



# # while not finnished
# while not finnished:
#     # send and receive data from the client socket
#     data_in = connection.recv(4096)

#     print('client send')
#     hexdump(data_in)

#     if data_in.startswith(b'quit'):
#         finnished = True
#     else:
#         data_out = data_in
#         connection.send(data_out)

# # close the connection
# connection.shutdown(SHUT_RDWR)
# connection.close()

# # close the server socket
# server_socket.shutdown(SHUT_RDWR)
# server_socket.close()
