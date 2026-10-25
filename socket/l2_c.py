import socket

def start_client () : 
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    SERVER_IP = '172.17.228.8'
    PORT = 9999

    try: 
        c.connect((SERVER_IP,PORT))

        c_addr = c.getsockname()
        print(f"Client is connected to server at {SERVER_IP}:{PORT} from {c_addr}")

        message = input("enter Data To convert into lower case : ")

        c.sendall(message.encode('utf-8'))

        response = c.recv(1024).decode('utf-8')
        print(f"Received response from server: {response}")

    except Exception as e :
        print(f"Error occurred: {e}")

    finally :
        c.close()

if __name__ == "__main__" :
    start_client()