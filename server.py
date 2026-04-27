import socket
import threading

clients = []       # list of (socket, color, avatar)
used_slots = []    # track used (color, avatar) pairs

# Palette of distinct bubble colors + matching avatars
SLOTS = [
    ("#FECDD3", "🐼"),  # rose
    ("#BBF7D0", "🦊"),  # green
    ("#BAE6FD", "🐬"),  # sky
    ("#FDE68A", "🐯"),  # amber
    ("#DDD6FE", "🦄"),  # violet
    ("#FED7AA", "🐻"),  # orange
    ("#CFFAFE", "🐙"),  # cyan
    ("#F5D0FE", "🦋"),  # fuchsia
]

slot_lock = threading.Lock()

def assign_slot():
    with slot_lock:
        for slot in SLOTS:
            if slot not in used_slots:
                used_slots.append(slot)
                return slot
        # Fallback if more than 8 clients
        import random
        return random.choice(SLOTS)

def release_slot(slot):
    with slot_lock:
        if slot in used_slots:
            used_slots.remove(slot)

def handle_client(client_socket, color, avatar):
    entry = (client_socket, color, avatar)
    while True:
        try:
            data = client_socket.recv(65536)
            if not data:
                break

            if data.startswith(b"MSG:"):
                # Wrap: MSG:<color>|<avatar>|<text>
                text = data[4:]
                tagged = f"MSG:{color}|{avatar}|".encode() + text
                broadcast(tagged, client_socket)

            elif data.startswith(b"FILE|"):
                # Wrap: FILE|<color>|<avatar>|<filename>|<size>|<bytes>
                # Original format: FILE|<filename>|<size>|<bytes>
                parts = data.split(b"|", 3)
                filename = parts[1]
                size = parts[2]
                rest = parts[3]
                tagged = b"FILE|" + color.encode() + b"|" + avatar.encode() + b"|" + filename + b"|" + size + b"|" + rest
                broadcast(tagged, client_socket)

            else:
                broadcast(data, client_socket)

        except:
            break

    clients.remove(entry)
    release_slot((color, avatar))
    client_socket.close()
    print(f"Client {avatar} disconnected.")

def broadcast(data, sender_socket):
    for (sock, col, av) in clients:
        if sock != sender_socket:
            try:
                sock.send(data)
            except:
                pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("0.0.0.0", 3000))
server.listen()

print("Server running on port 3000...")

while True:
    client_socket, addr = server.accept()
    color, avatar = assign_slot()
    print(f"Connected: {addr}  →  {avatar} ({color})")

    entry = (client_socket, color, avatar)
    clients.append(entry)

    # Tell the new client its own color and avatar
    greeting = f"IDENTITY:{color}|{avatar}".encode()
    client_socket.send(greeting)

    thread = threading.Thread(target=handle_client, args=(client_socket, color, avatar), daemon=True)
    thread.start()