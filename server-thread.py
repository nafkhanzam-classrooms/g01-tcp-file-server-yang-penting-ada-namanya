import socket
import threading
import os

HOST = '0.0.0.0'
PORT = 5000
FILES_DIR = 'files'

clients = []

os.makedirs(FILES_DIR, exist_ok=True)

def broadcast(msg, sender):
    for c in clients:
        if c != sender:
            c.send(msg)

def handle_client(conn):
    clients.append(conn)

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            if data == "/list":
                files = "\n".join(os.listdir(FILES_DIR))
                conn.send(files.encode())

            elif data.startswith("/upload"):
                _, filename = data.split()
                with open(os.path.join(FILES_DIR, filename), "wb") as f:
                    while True:
                        chunk = conn.recv(1024)
                        if chunk == b"EOF":
                            break
                        f.write(chunk)
                conn.send(b"Upload done")

            elif data.startswith("/download"):
                _, filename = data.split()
                path = os.path.join(FILES_DIR, filename)

                if not os.path.exists(path):
                    conn.send(b"ERROR")
                else:
                    conn.send(b"OK")
                    with open(path, "rb") as f:
                        while chunk := f.read(1024):
                            conn.send(chunk)
                    conn.send(b"EOF")

            else:
                broadcast(data.encode(), conn)

        except:
            break

    clients.remove(conn)
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Thread Server running...")

while True:
    conn, addr = server.accept()
    print("Connected:", addr)

    thread = threading.Thread(target=handle_client, args=(conn,))
    thread.start()
