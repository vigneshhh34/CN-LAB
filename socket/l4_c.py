# Name: [Your Name]
# Roll Number: [Your Roll Number]

import socket
import os
import time

IP = '172.17.228.8'
PORT = 9991

def start_client():
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        c.connect((IP, PORT))

        client_addr = c.getsockname()
        print(f"Connected to server {IP} : {PORT}")
        print(f"Client Local Socket Address : {client_addr}")

        assigned_username = c.recv(1024).decode('utf-8')
        print(f"Assigned User Name For me is : {assigned_username}")

        while True: 
            file_path = input("\nEnter the path of the file to upload (e.g., sample.txt, sample.pdf, sample.mp4) or type 'exit': ").strip()

            if file_path.lower() == 'exit':
                print("Client Exiting")
                break
            
            if not os.path.exists(file_path):
                print("File Does Not exist locally")
                continue

            filename = os.path.basename(file_path)

            c.sendall(filename.encode('utf-8'))
            print(f"Sent File Name Request : {filename}")

            server_response = c.recv(1024).decode('utf-8')
            print(f"Server Response : {server_response}")

            if "File already exists" in server_response:
                print("Server Rejected file As it ALREADY exists")
                choice = input("Would you like to (1) Try a different file or (2) Exit? Enter 1 or 2: ").strip()
                if choice == '1':
                    continue # Let the loop prompt for another file instead of breaking
                else:
                    break
                    
            elif server_response == 'READY':
                print("[*] Server is READY. Beginning chunk-based file transfer with simulation delays...")

                sent_bytes = 0

                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        c.sendall(chunk)
                        sent_bytes += len(chunk)
                        time.sleep(0.01)

                # Send EOF signal so the server knows the upload is complete
                c.sendall(b'EOF')

                print(f"[-> Uploaded {sent_bytes} bytes in total. Waiting for server confirmation...]")
                confirmation = c.recv(1024).decode('utf-8')
                print(f"Final Server Confirmation : {confirmation}")
                break

    except Exception as e:
        print(f"Exception is {e}")
    finally: 
        c.close()
        print("Client Socket Closed")

if __name__ == "__main__":
    start_client()