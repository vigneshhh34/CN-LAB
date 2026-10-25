import socket 

def start_client() :
    c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    IP = '172.17.228.8'
    PORT = 9991

    try : 
        c.connect((IP,PORT))

        c_addr = c.getsockname()
        print(f"Client connected in {c_addr}")

        message = input("Enter Message To Convert Into Lower Case : ")

        c.sendall(message.encode('utf-8'))

        response = c.recv(1024).decode('utf-8')
        print(f"Lower Case Message Recivied from server is : {response}")

    except Exception as e  : 
        print(f"Error Occured {e}")
    finally : 
        c.close()

if __name__ == "__main__" :
    start_client()