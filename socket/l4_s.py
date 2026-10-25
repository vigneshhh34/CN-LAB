# Name: [Your Name]
# Roll Number: [Your Roll Number]

import socket
import threading 
import os 
import time 
from datetime import datetime

active_connections = 0
client_username = {}
username_count = 1

connections_lock = threading.Lock()
username_lock = threading.Lock()
log_lock = threading.Lock()
file_check = threading.Lock()

IP = '172.17.228.8'
PORT = 9991
LOG_FILENAME = 'server_log.txt'

def log_event(server_addr, client_addr, username, filename, action, file_size=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action.lower() == 'accepted': 
        log_entry = f'[{timestamp}] serversocket : {server_addr[0]} : {server_addr[1]} , client socket : {client_addr[0]} : {client_addr[1]}, username : {username}, filename : {filename}, Action: {action}, size : {file_size} bytes\n'
    else:
        log_entry = f'[{timestamp}] serversocket : {server_addr[0]} : {server_addr[1]} , client socket : {client_addr[0]} : {client_addr[1]}, username : {username}, filename : {filename}, Action: {action}\n'

    with log_lock: 
        with open(LOG_FILENAME, 'a') as log_file:
            log_file.write(log_entry)

def handle_client(conn, addr, server_adress):
    global active_connections, username_count

    client_ip = addr[0]

    # Managing Persistent Username 
    with username_lock:
        if client_ip in client_username:
            assigned_username = client_username[client_ip]
        else:
            assigned_username = f'user{username_count}'
            client_username[client_ip] = assigned_username
            username_count += 1

    # Manage Active Connections 
    with connections_lock:
        active_connections += 1
        print(f'Client Connected | socket : {addr} | Assigned UserName : {assigned_username}')
        print(f'No Of Active Connections : {active_connections}')

    try: 
        # Send assigned username to the client immediately 
        conn.sendall(assigned_username.encode('utf-8'))

        # Receive requested filename from client 
        filename_data = conn.recv(1024).decode('utf-8').strip()
        if not filename_data: 
            return 

        base_filename = os.path.basename(filename_data)
        target_filename = f"{assigned_username}_{base_filename}"

        print(f"Client {assigned_username} ({addr}) requested to upload file : '{base_filename}'")

        # Check if file already exists on server storage 
        with file_check: 
            file_exists = os.path.exists(target_filename)

        if file_exists: 
            print(f"File Already Exists '{target_filename}' . Reject Transfer")
            conn.sendall("File Already Exists".encode('utf-8'))
            log_event(server_adress, addr, assigned_username, target_filename, "Rejected")
            return 
        else: 
            conn.sendall("READY".encode('utf-8'))

        # Receive File Data in chunks until b'EOF' is detected
        received_file_size = 0
        with open(target_filename, 'wb') as f: 
            while True: 
                chunk = conn.recv(4096)
                if not chunk or chunk == b'EOF':
                    break
                f.write(chunk)
                received_file_size += len(chunk)

        print(f"Successfully received {target_filename} of {received_file_size} bytes from {assigned_username}")

        confirmation_msg = f"Upload Complete for {target_filename}"
        conn.sendall(confirmation_msg.encode('utf-8'))

        log_event(server_adress, addr, assigned_username, target_filename, "Accepted", received_file_size)

    except Exception as e:
        print(f"Exception {e}")
    finally:
        conn.close()
        with connections_lock:
            active_connections -= 1
            print(f"Client Disconnected | socket : {addr} | Username : {assigned_username}")
            print(f"Active Connections count : {active_connections}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((IP, PORT))
    s.listen(5)

    server_adress = s.getsockname()

    print('Server Started Listening: ')
    print(f'Logging Events to {LOG_FILENAME}')

    try: 
        while True: 
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr, server_adress))
            client_thread.daemon = True 
            client_thread.start()
    except KeyboardInterrupt: 
        print("Server Shutting Down Manually")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()