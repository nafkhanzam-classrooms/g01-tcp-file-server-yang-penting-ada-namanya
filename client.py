import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            data = client.recv(1024)
            if not data:
                break
            print(data.decode())
        except:
            break

threading.Thread(target=receive, daemon=True).start()

while True:
    cmd = input()

    if cmd.startswith("/upload"):
        _, filename = cmd.split()
        client.send(cmd.encode())

        with open(filename, "rb") as f:
            while chunk := f.read(1024):
                client.send(chunk)
        client.send(b"EOF")

    elif cmd.startswith("/download"):
        _, filename = cmd.split()
        client.send(cmd.encode())

        status = client.recv(1024)
        if status == b"ERROR":
            print("File not found")
        else:
            with open(filename, "wb") as f:
                while True:
                    chunk = client.recv(1024)
                    if chunk == b"EOF":
                        break
                    f.write(chunk)
            print("Downloaded")

    else:
        client.send(cmd.encode())