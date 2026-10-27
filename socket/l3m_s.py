import socket
import threading

global_string = 'apple,banana'
active_connections = 0

# Persistent tracking dictionaries & counters
client_usernames = {}  # Maps client IP string -> assigned username (e.g., '192.168.1.5' -> 'user1')
username_counter = 1

string_lock = threading.Lock()
connection_lock = threading.Lock()
username_lock = threading.Lock()

IP = '172.17.228.8'
PORT = 9991

def handle_client(conn, addr):
    global global_string, active_connections, username_counter

    client_ip = addr[0]

    # 1. Manage Persistent Username Assignment based on IP
    with username_lock:
        if client_ip in client_usernames:
            assigned_username = client_usernames[client_ip]
        else:
            assigned_username = f"user{username_counter}"
            client_usernames[client_ip] = assigned_username
            username_counter += 1

    # Send the assigned username to the client immediately upon connection
    conn.sendall(assigned_username.encode('utf-8'))

    # 2. Track Active Connections safely
    with connection_lock:
        active_connections += 1  # FIXED: Corrected from '=+ 1' to '+= 1'
        print(f"\n[+] New Client Added: {addr} | Username: {assigned_username}")
        print(f"[*] Active Connections: {active_connections}")

    try:
        while True:
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break
            print(f"[<- Received From Client {assigned_username} ({addr})]: '{data}'")

            if data.lower() == 'exit':
                print(f"[*] Client {assigned_username} requested to leave.")
                break

            # Thread-safe global string modification
            with string_lock:
                word_list = [w.strip() for w in global_string.split(',')] if global_string else []

                if data in word_list:
                    action = 'Word already present in global string (No change)'
                else:
                    if global_string:
                        global_string += f",{data}"
                    else:
                        global_string = data
                    action = 'Word Added to global string'
                current_string = global_string

            print(f"[*] Server Action: {action}")
            print(f"[*] Current Global String: {current_string}")

            conn.sendall(current_string.encode('utf-8'))

    except Exception as e:
        print(f"[-] Exception with {assigned_username}: {e}")
    finally:
        conn.close()
        with connection_lock:
            active_connections -= 1
            print(f"\n[-] Client Disconnected: {addr} ({assigned_username})")
            print(f"[*] Active Connections: {active_connections}")

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allows immediate reuse of the port after server restart
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((IP, PORT))
    s.listen(5)

    print(f"==================================================")
    print(f"[*] Server listening on {IP} : {PORT}")
    print(f"[*] Initial Global String : {global_string}")
    print(f"==================================================")

    try:
        while True:
            conn, addr = s.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    except Exception as e:
        print(f"[-] Server Exception: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()