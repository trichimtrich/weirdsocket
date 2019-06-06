# echo server - serve forever

import socket
import select
import queue

from OpenSSL import SSL

HOST = "localhost"
PORT = 9999
BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)

server.bind((HOST, PORT))
server.listen(5)

print("Server started")

inputs = [server]
outputs = []
conn_dict = {}

def doClose(s, isServer=False):
    inputs.remove(s)
    if s in outputs:
        outputs.remove(s)
    if not isServer:
        del conn_dict[s]
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
            conn_dict[conn] = {
                "flag": socket.MSG_PEEK,
                "msg": queue.Queue()
            }
        else:
            # clients
            try:
                data = s.recv(BUFFER_SIZE, conn_dict[s]["flag"])
            except SSL.Error:
                # ssl socket error
                doClose(s)
                continue

            if data:
                # first packet
                if conn_dict[s]["flag"] != 0:
                    conn_dict[s]["flag"] = 0

                    if data.startswith(b"\x16\x03"):
                        print(">> Detect SSL request")

                        # set blocking first
                        s.setblocking(1)

                        # ssl
                        ctx = SSL.Context(SSL.SSLv23_METHOD)
                        ctx.use_privatekey_file("cert/my.key")
                        ctx.use_certificate_file("cert/my.pem")

                        s2 = SSL.Connection(ctx, s)
                        s2.set_accept_state()
                        try:
                            s2.do_handshake()
                        except:
                            print(">> Failed to switch SSL")
                        else:
                            print(">> Upgraded")
                            # switch data from s -> s2
                            inputs.remove(s)
                            inputs.append(s2)
                            if s in outputs:
                                outputs.remove(s)
                                outputs.append(s2)
                            conn_dict[s2] = conn_dict[s]
                            del conn_dict[s]
                        
                        # non-blocking again
                        s.setblocking(0)
                    
                    continue

                # handle data after handshake
                print("> [{}] Recv: {} bytes".format(s.getpeername(), len(data)))
                if data.startswith(b"quit"):
                    doClose(s)
                else:
                    conn_dict[s]["msg"].put(data)
                    if s not in outputs:
                        outputs.append(s)
            else:
                # client closed
                doClose(s)
    
    for s in writable:
        try:
            next_msg = conn_dict[s]["msg"].get_nowait()
        except queue.Empty:
            outputs.remove(s)
        else:
            s.send(next_msg)
    
    for s in exceptional:
        # exception of input fd
        doClose(s)


