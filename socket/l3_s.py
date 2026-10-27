import socket
import threading 

global_string = "apple,banana"
active_connections = 0

string_lock = threading.Lock()
connections_lock = threading.Lock()

def handle_client(conn, addr):
    global global_string, active_connections

    with connections_lock: 
        active_connections += 1
        print(f"New Client Added : {addr}")
        print(f"Active connections : {active_connections}")

    try: 
        while True: 
            data = conn.recv(1024).decode('utf-8').strip()
            if not data:
                break 

            print(f"Received From Client {addr} : '{data}'")

            if data.lower() == 'exit': 
                print(f'{addr} requested to leave')
                break

            with string_lock: 
                word_list = [w.strip() for w in global_string.split(',')] if global_string else []

                if data in word_list:
                    action = 'No change word already present in global string'
                else: 
                    if global_string:
                        global_string += f",{data}"
                    else: 
                        global_string = data 
                    action = 'Word Added to global String'
                current_string = global_string
                
            print(f'Server Action : {action}')
            print(f'Current global string : {current_string}')

            conn.sendall(current_string.encode('utf-8'))
            
    except Exception as e: 
        print(f'Error Handling {e}')
    finally: 
        conn.close()
        with connections_lock:
            active_connections -= 1
            print(f"Client Disconnected {addr}")
            print(f"Active Connections : {active_connections}")


def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    HOST = '172.17.228.8'
    PORT = 9991

    s.bind((HOST, PORT))
    s.listen(5)

    print(f'Server Listening on {HOST} : {PORT}')
    print(f'Initial Global String : {global_string}')

    try: 
        while True: 
            conn, addr = s.accept()

            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True 
            client_thread.start()
            
    except KeyboardInterrupt: 
        print("Server Shutting Down Manually")
    finally: 
        s.close()

if __name__ == "__main__":
    start_server()  