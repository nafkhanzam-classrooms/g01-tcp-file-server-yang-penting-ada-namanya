import socket
import select
import os

HOST = '0.0.0.0'
PORT = 5000
FILES_DIR = 'files'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

sockets = [server]

os.makedirs(FILES_DIR, exist_ok=True)

print("Select Server running...")

while True:
    read_sockets, _, _ = select.select(sockets, [], [])

    for sock in read_sockets:
        if sock == server:
            conn, addr = server.accept()
            sockets.append(conn)
            print("Connected:", addr)

        else:
            try:
                data = sock.recv(1024)
                if not data:
                    sockets.remove(sock)
                    sock.close()
                    continue

                msg = data.decode()

                for client in sockets:
                    if client != server and client != sock:
                        client.send(data)

            except:
                sockets.remove(sock)
                sock.close()