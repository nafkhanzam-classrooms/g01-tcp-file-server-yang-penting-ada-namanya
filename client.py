import socket
import threading
import os

HOST = '127.0.0.1'
PORT = 5000

client = socket.socket()
client.connect((HOST, PORT))

END = b"<END_OF_FILE>"

# =========================
# RECEIVER THREAD (CHAT ONLY)
# =========================
def receiver():
    buffer = b""

    while True:
        try:
            data = client.recv(1024)
            if not data:
                break

            buffer += data

            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                print(line.decode())

        except:
            break

threading.Thread(target=receiver, daemon=True).start()

# =========================
# MAIN LOOP
# =========================
while True:
    cmd = input()

    # =====================
    # LIST
    # =====================
    if cmd == "/list":
        client.sendall(b"/list\n")
        # biarkan receiver yang print → tidak blocking

    # =====================
    # UPLOAD
    # =====================
    elif cmd.startswith("/upload"):
        try:
            _, filename = cmd.split()
        except:
            print("Usage: /upload <filename>")
            continue

        if not os.path.exists(filename):
            print("File not found")
            continue

        client.sendall(f"/upload {filename}\n".encode())

        with open(filename, "rb") as f:
            while chunk := f.read(1024):
                client.sendall(chunk)

        client.sendall(END)

        print("Upload sent")

    # =====================
    # DOWNLOAD
    # =====================
    elif cmd.startswith("/download"):
        try:
            _, filename = cmd.split()
        except:
            print("Usage: /download <filename>")
            continue

        client.sendall(f"/download {filename}\n".encode())

        print("Downloading...")

        buffer = b""

        while True:
            data = client.recv(1024)
            buffer += data

            if END in buffer:
                file_data, _ = buffer.split(END, 1)
                break

        with open(filename, "wb") as f:
            f.write(file_data)

        print("Downloaded")

    # =====================
    # CHAT
    # =====================
    else:
        client.sendall((cmd + "\n").encode())
