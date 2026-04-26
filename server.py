import socket
import threading

clients = []

def handle_client(client):
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            broadcast(data, client)
        except:
            break

    clients.remove(client)
    client.close()

def broadcast(data, sender):
    for client in clients:
        if client != sender:
            try:
                client.send(data)
            except:
                client.close()
                clients.remove(client)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 3000))
server.listen()

print("Server running...")

while True:
    client, addr = server.accept()
    print("Connected:", addr)
    clients.append(client)

    thread = threading.Thread(target=handle_client, args=(client,))
    thread.start()