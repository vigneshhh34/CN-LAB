import socket 

def start_client(): 
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    IP = '172.17.228.8'
    PORT = 9991

    try: 
        c.connect((IP, PORT))

        c_addr = c.getsockname()
        # FIXED: Added 'f' prefix to print string
        print(f"Client Connected locally to : {c_addr}")
        print("Type A Single Word or type 'exit' to quit ")

        while True: 
            word = input("\nEnter A Word: ").strip()
            if not word: 
                continue 

            c.sendall(word.encode('utf-8'))
            print(f"Data Sent to Server : {word}")

            if word.lower() == 'exit':
                print("Terminating Connection")
                break 

            response = c.recv(1024).decode('utf-8')
            print(f"Data Received From server: {response}")

    except Exception as e: 
        print(f"Exception: {e}")
    finally: 
        c.close()
        print("Client Socket Closed")

# FIXED: Corrected __main__ syntax
if __name__ == "__main__":
    start_client()