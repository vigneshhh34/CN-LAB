import socket 

s = socket.socket()
print('Socket created')

s.bind(('localhost', 9999))

s.listen(3)
print('Waiting for connections')

while True : 
    c , addr = s.accept()
    print(f'Connection from {addr}')

    c.send(bytes('Welcome','utf-8'))

    c.close()