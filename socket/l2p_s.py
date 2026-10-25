import socket 

def start_server() : 
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    IP = '172.17.228.8'
    PORT = 9991

    s.bind((IP,PORT))
    s.listen(1)
    print(f"Server is listening on {IP} : {PORT}")

    c,addr = s.accept()
    print(f"Conneection Established with {addr}")

    data = c.recv(1024).decode('utf-8')
    print(f'Recvied Data : {data}')

    lower_case = data.lower()
    print('Sending Lower Case Data')

    c.sendall(lower_case.encode('utf-8'))

    c.close
    s.close

if __name__ == "__main__" : 
    start_server()