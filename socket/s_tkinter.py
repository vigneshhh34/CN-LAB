import socket, threading

clients = []

def handle(conn):
    while True:
        data = conn.recv(1024)
        if not data:                       # client disconnected
            break
        for c in clients:                  # broadcast to everyone
            c.sendall(data)
    clients.remove(conn)
    conn.close()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", 5000))
srv.listen()
print("Server running")

while True:
    conn, addr = srv.accept()
    clients.append(conn)
    threading.Thread(target=handle, args=(conn,), daemon=True).start()