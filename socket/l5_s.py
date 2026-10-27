# Name: [Your Name]
# Roll Number: [Your Roll Number]

import socket
import threading
import os
import time
from datetime import datetime

IP = '172.17.228.8'
PORT = 9991
LOG_FILENME = 'log.txt'

active_users = {}
user_details = {}
client_lock = threading.Lock()
log_lock = threading.Lock()

def write_logentry(entry):
    # FIXED: Removed list brackets [] so strftime receives a valid string format
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] : {entry}\n"
    with log_lock:
        with open(LOG_FILENME, 'a') as f:
            f.write(log_line)

def print_active_connections():
    with client_lock:
        print("Active Client Connections : ")
        print(f"Total Active Connections : {len(active_users)}")
        for uname, conn in active_users.items():
            addr = user_details[uname]['addr']
            print(f"Socket {addr[0]} : {addr[1]} | Username : {uname}")

def handle_client(conn, addr):
    username = None
    join_time = None

    try: 
        # Handle Username Registration
        raw_username = conn.recv(1024).decode('utf-8').strip()

        with client_lock:
            if raw_username in active_users or raw_username.lower() in ['broadcast', 'users', 'exit']:
                conn.sendall("Rejected".encode('utf-8'))
                write_logentry(f"{addr[0]} : {addr[1]} , AttemptedUsername : {raw_username}, Status: Rejected (already in use)")
                conn.close()
                return 
            else:
                conn.sendall("Success".encode('utf-8'))
                username = raw_username
                join_time = datetime.now()
                active_users[username] = conn
                user_details[username] = {'addr': addr, 'join_time': join_time}

        write_logentry(f"{addr[0]} : {addr[1]}, Username : {username}, Activity : Joined")
        print(f"Client Joined {addr} as {username}")
        print_active_connections()

        # Main Communication Loop 
        while True:
            # FIXED: Added .decode('utf-8') to prevent bytes vs string comparison errors
            data = conn.recv(1024).decode('utf-8')
            if not data: 
                break 

            if data.strip() == '/users':
                with client_lock:
                    user_list = ",".join(active_users.keys())
                conn.sendall(f"Online Users : {user_list}".encode('utf-8'))

            elif data.strip() == '/exit':
                break

            elif data.startswith('<broadcast>:'):
                msg = data.split(':', 1)[1]
                msg_size = len(msg.encode('utf-8'))
                broadcast_packet = f"BroadCast From {username} : {msg}"

                failed_count = 0
                with client_lock:
                    for uname, uconn in active_users.items():
                        if uname != username:
                            try: 
                                uconn.sendall(broadcast_packet.encode('utf-8'))
                            except:
                                failed_count += 1 

                # Log Broadcast
                client_str = f"{addr[0]} : {addr[1]}"
                if failed_count == 0:
                    write_logentry(f"From: {username} ({client_str}), To: Broadcast, Size: {msg_size}Bytes, Status: Sent")
                else:
                    write_logentry(f"From: {username} ({client_str}), To: Broadcast, Size: {msg_size}Bytes, Status: Failed (Some users unreachable)")

            elif ':' in data:
                target_user, msg = data.split(':', 1)
                target_user = target_user.strip()
                msg_size = len(msg.encode('utf-8'))
                client_str = f"{addr[0]} : {addr[1]}"

                with client_lock:
                    if target_user in active_users:
                        target_conn = active_users[target_user]
                        target_addr = user_details[target_user]['addr']
                        # FIXED: Corrected string formatting for target address
                        target_str = f"{target_addr[0]}:{target_addr[1]}"

                        try:
                            target_conn.sendall(f"Private From {username} : {msg}".encode('utf-8'))
                            conn.sendall(f"System : Message sent to {target_user}".encode('utf-8'))
                            write_logentry(f"From: {username} ({client_str}), To: {target_user}({target_str}), Size: {msg_size}Bytes, Status: Sent")
                        except: 
                            conn.sendall(f"System: Failed to send message to {target_user}".encode('utf-8'))
                            write_logentry(f"From: {username} ({client_str}), To: {target_user}({target_str}), Size: {msg_size}Bytes, Status: Failed (Socket Error)")
                    else:
                        conn.sendall("System : User not online".encode('utf-8'))
                        write_logentry(f"From: {username} ({client_str}), To: {target_user} (Offline), Size: {msg_size}Bytes, Status: Failed (User Not Online)")

    except Exception as e:
        print(f"Error With Client {addr} : {e}")
    finally:
        if username:
            leave_time = datetime.now()
            duration = leave_time - join_time
            hours, remainder = divmod(int(duration.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"

            with client_lock:
                if username in active_users:
                    del active_users[username]
                if username in user_details:
                    del user_details[username]

            write_logentry(f"{addr[0]}:{addr[1]}, Username: {username}, Activity: left, session_duration: {duration_str}")
            print(f"[-] Client Left: {addr} ({username}) | Session Duration: {duration_str}")
            print_active_connections()
        conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((IP, PORT))
    s.listen(5)

    print(f"Server Started listening on {IP} : {PORT}")

    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.daemon = True 
            t.start()
    except KeyboardInterrupt:
        print("Server Shutting Down")
    finally:
        s.close()

if __name__ == "__main__": 
    start_server()