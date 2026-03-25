import socket, select, os

HOST = '0.0.0.0'
PORT = 5000
FILES_DIR = 'files'
END = b"<END_OF_FILE>"

os.makedirs(FILES_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen()

poll = select.poll()
poll.register(server, select.POLLIN)

fd_map = {server.fileno(): server}
buffers = {}
states = {}

print("Poll server running...")

def broadcast(sender, msg):
    for s in fd_map.values():
        if s != server and s != sender:
            s.sendall((msg + "\n").encode())

while True:
    events = poll.poll()

    for fd, event in events:
        sock = fd_map[fd]

        if sock == server:
            conn, _ = server.accept()
            poll.register(conn, select.POLLIN)
            fd_map[conn.fileno()] = conn
            buffers[conn] = b""
            states[conn] = {"mode": "cmd"}

        else:
            try:
                data = sock.recv(1024)
                if not data:
                    raise Exception()

                buffers[sock] += data

                while True:
                    state = states[sock]

                    if state["mode"] == "cmd":
                        if b"\n" not in buffers[sock]:
                            break

                        line, buffers[sock] = buffers[sock].split(b"\n", 1)
                        line = line.decode()

                        if line == "/list":
                            files = os.listdir(FILES_DIR)
                            resp = "\n".join(files) if files else "(empty)"
                            sock.sendall((resp + "\n").encode())

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
                            broadcast(sock, line)

                    elif state["mode"] == "upload":
                        needed = state["remaining"]
                        chunk = buffers[sock][:needed]

                        state["data"] += chunk
                        state["remaining"] -= len(chunk)
                        buffers[sock] = buffers[sock][len(chunk):]

                        if state["remaining"] == 0:
                            path = os.path.join(FILES_DIR, state["filename"])
                            with open(path, "wb") as f:
                                f.write(state["data"])

                            sock.sendall(b"OK\n")
                            states[sock] = {"mode": "cmd"}
                        else:
                            break

            except:
                poll.unregister(fd)
                fd_map.pop(fd, None)
                buffers.pop(sock, None)
                states.pop(sock, None)
                sock.close()
