import socket
import os

HOST = '0.0.0.0'
PORT = 5000
FILES_DIR = 'files'

os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print("Server Sync running...")

while True:
    conn, addr = server.accept()
    print(f"Connected: {addr}")

    while True:
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
            conn.send(b"Upload complete")

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
            conn.send(f"ECHO: {data}".encode())

    conn.close()