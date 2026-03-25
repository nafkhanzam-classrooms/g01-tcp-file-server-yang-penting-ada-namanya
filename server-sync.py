import socket, os

HOST = '0.0.0.0'
PORT = 5000
FILES_DIR = 'files'
END = b"<END_OF_FILE>"

os.makedirs(FILES_DIR, exist_ok=True)

def recv_line(conn):
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1)
        if not chunk:
            return None
        data += chunk
    return data.decode().strip()

def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(min(1024, size - len(data)))
        if not chunk:
            break
        data += chunk
    return data

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

print("Sync server running...")

while True:
    conn, _ = server.accept()

    while True:
        line = recv_line(conn)
        if not line:
            break

        if line == "/list":
            files = os.listdir(FILES_DIR)
            conn.sendall(("\n".join(files) + "\n").encode())

        elif line.startswith("/upload"):
            _, filename = line.split()

            buffer = b""

            while True:
                chunk = conn.recv(1024)
                buffer += chunk

                if END in buffer:
                    file_data, _ = buffer.split(END, 1)
                    break

            with open(os.path.join(FILES_DIR, filename), "wb") as f:
                f.write(file_data)

            conn.sendall(b"OK\n")

        elif line.startswith("/download"):
            _, filename = line.split()
            path = os.path.join(FILES_DIR, filename)

            if not os.path.exists(path):
                conn.sendall(b"ERROR\n")
            else:
                conn.sendall(b"OK\n")

                with open(path, "rb") as f:
                    while chunk := f.read(1024):
                        conn.sendall(chunk)

                conn.sendall(END)

        else:
            conn.sendall(("ECHO: " + line + "\n").encode())

    conn.close()
