import bluetooth

server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

port = 1
server_socket.bind(("",port))
server_socket.listen(1)

client_socket, address = server_socket.accept()
print ("Got address")

while(1):
    data = client_socket.recv(1024)
    print ("Data recieved: ", data)

client_socket.close()
server_socket.close()
