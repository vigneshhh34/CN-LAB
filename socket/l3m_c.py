import socket

IP = '172.17.228.8'
PORT = 9991

def start_client():
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        c.connect((IP, PORT))

        c_addr = c.getsockname()
        print(f"Client Connected locally to : {c_addr}")

        # Receive and print the persistent username assigned by the server
        assigned_username = c.recv(1024).decode('utf-8')
        print(f"Assigned Persistent Username : {assigned_username}")

        print("Type A single Word or type exit to quit")

        while True:
            message = input("\nEnter A word : ").strip()
            if not message:
                continue
            
            c.sendall(message.encode('utf-8'))
            print(f"'{message}' sent to server")

            if message.lower() == 'exit':
                break

            response = c.recv(1024).decode('utf-8')
            print(f"Data From Server (Global String) : {response}")

    except Exception as e:
        print(f"Exception {e}")
    finally:
        c.close()
        print("Client socket closed.")

if __name__ == "__main__":
    start_client()