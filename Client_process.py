# YUSUF MERT KAHRAMAN EE444
import socket
import time

HOST = '127.0.0.1'
PORT = 6002
#Create a sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST,PORT))
print('You can both write "OP=XXX;IND=indc1,indc2;DATA=data1,data2" OR automatically')
print("For the next stages, input 'm' for manual input, 'o' for automatic input...")
print("I recommend you to choose 'o' automatic mod, which will be easier for you.")
choose = input("Choose: ")
while 1:
    if(choose == "m" or choose == "M"):
        message = input("Enter the command to be sent: ")
    elif(choose == "o" or choose == "O"):
        op = input("Please,write the opcode (GET,PUT,CLR,ADD,INF): ")
        if(op == "GET"):
            indc = input("Enter the indices (Seperate using commas ','): ")
            message = "OP=GET;IND=" + indc + ";"
        elif(op == "PUT"):
            indc = input("Enter the indices (Seperate using commas ','): ")
            data = input("Enter the data respectively with indices (Seperate using commas ','): ")
            message = "OP=PUT;IND=" + indc + ";DATA=" + data
        elif(op == "ADD"):
            indc = input("Enter the indices (Seperate using commas ','): ")
            message = "OP=ADD;IND=" + indc + ";" 
        elif(op == "CLR"):
            message = "OP=CLR;;"
        elif(op == "INF"):
            message = "OP=INF;;"
    else:
        print("Invalid choice. Restart the programme.")
    #You can only send byte-like objects through the socket
    print("Delivered the message (from client to proxy):", message)
    client_socket.sendall(bytes(message,'utf-8'))
    time.sleep(0.5)
    dataReceived=client_socket.recv(1024)
    dataReceived = dataReceived.decode('utf-8')
    print("Received message (from proxy to client): ",dataReceived)
