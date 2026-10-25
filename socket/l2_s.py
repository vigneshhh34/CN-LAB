import socket

def start_server(): 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_IP = '172.17.228.8'
    PORT = 9999

    s.bind((SERVER_IP,PORT))
    s.listen(1)

    print(f"Server is listening on {SERVER_IP}:{PORT}")

    c , addr = s.accept()
    print(f"Connection established with {addr}")

    data = c.recv(1024).decode('utf-8')
    print(f"Received data: {data}")

    lowercase_data = data.lower()
    print('Sending Lower Case Data back to client')

    c.sendall(lowercase_data.encode('utf-8'))

    c.close()
    s.close()

if __name__ == "__main__" : 
    start_server()