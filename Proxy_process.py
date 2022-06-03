# EE444 HW1
# pip install tabulate
import socket
import time
import re
from tabulate import tabulate
HOST = '127.0.0.1'
PORTS = 6002
PORTC = 4000
# CREATING TWO SOCKET. ONE OF THEM IS FOR CONNECTING WITH CLIENT WHERE THE OTHER ONE IS RESPONSIBLE FOR CONNECTING SERVER.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORTC))
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORTS))
server_socket.listen(1)
conn, clientAddress = server_socket.accept()
# Initial values and index
data = [0,10,20,30,40]
I = ["0","1","2","3","4"]
visual = list(zip(I,data))
col_names = ["Index","Data"]
display = 0; # Parameter if there is a change to display table.
print(tabulate(visual,headers = col_names))
counter = 0 # holds the oldest table entry. (Initially 0)
while 1:
    try:
        dataReceived = conn.recv(1024)
    except OSError:
        print (clientAddress, 'disconnected')
        server_socket.listen(1)
        conn, clientAddress = server_socket.accept()
        print ('Connected by', clientAddress)
        time.sleep(0.5)

    else:    
        dataReceived = dataReceived.decode('utf-8')
        print("Received message (from client to proxy): ",dataReceived)
        commandSplit = re.split(";",dataReceived)
        # OP determines the operation
        op = re.split("=",commandSplit[0])[1]
        # If operation is CLR or INF which does not have INDC part, no need to do it, pass it.
        if(op != "CLR" and op != "INF"):
            indcstring = re.split("=",commandSplit[1])[1]
            indc = re.split(",",indcstring)
        # m is the response string, which will be fullfilled in the below parts.
        m=[]
        if(op == "GET"):
            # This is the GET request.
            for i in range(len(indc)):
                if(indc[i] in I):
                    index = I.index(indc[i]) # Gives the index of data.
                    m.append(str(data[index])) # Response string is written.
                else:
                    I[counter] = indc[i]        # Newi index in the oldest entry.
                    n = ["OP=GET;IND=",indc[i],";","DATA="]
                    n = ''.join(n)
                    client_socket.sendall(bytes(n,'utf-8'))
                    print("Delivered message (from proxy to server): ",n)
                    dataReceived = client_socket.recv(1024)
                    dataReceived = dataReceived.decode('utf-8')
                    print("Received message (from server to proxy): ",dataReceived)
                    fromserver = re.split(";",dataReceived)
                    fromserver = re.split("=",fromserver[2])
                    if(fromserver[1] == "NO_DATA"):
                        m.append("NO_DATA")
                    else:
                        data[counter] = int(fromserver[1])  #New data in the oldest one.
                        m.append(str(data[counter]))        #Response string
                        counter = (counter + 1) % 5         #Next oldest entry.
                        display = 1                         #The table is changed, so display it.
            m = ','.join(m)
            m = "OP=GET;" + commandSplit[1] + ";DATA=" + m
            conn.sendall(bytes(m,'utf-8'))
            print("Delivered message (from proxy to client): ",m)
            visual = list(zip(I,data))
            if (display):
                print(tabulate(visual,headers = col_names))
                display = 0
        elif(op == "PUT"):
            # PUT REQUEST
            datastring = re.split("=",commandSplit[2])[1]
            dataSplit = re.split(",",datastring)            #data array
            for i in range(len(indc)):
                m = "OP=PUT" + ";IND=" + indc[i] + ";DATA=" + dataSplit[i]  # To SERVER
                client_socket.sendall(bytes(m,'utf-8'))
                print("Delivered message (from proxy to server): ",m)
                fromserver = client_socket.recv(1024)
                fromserver = fromserver.decode('utf-8')
                print("Received message (from server to proxy): ",fromserver)
                if(indc[i] in I):
                    index = I.index(indc[i])
                    data[index] = int(dataSplit[i])
                else:
                    I[counter] = indc[i]                    #Deleting the oldest entry.
                    data[counter] = int(dataSplit[i])
                    counter = (counter + 1) % 5
            n = dataReceived + ";DONE"
            conn.sendall(bytes(n,'utf-8'))
            print("Delivered message (from proxy to client): ",n)           
            visual = list(zip(I,data))
            print(tabulate(visual,headers = col_names))  
        elif(op == "ADD"):
            # ADD REQUEST
            Sum = 0;                                        #Sum variable is initialized to zero.
            for i in range(len(indc)):
                if(indc[i] in I):
                    index = I.index(indc[i])
                    Sum = Sum + data[index]                 #Element is in PROXY, add it directly.          
                else:
                    display = 1                             #Table will be changed since element is not in PROXY so take it and display.
                    n = "OP=GET;IND=" + indc[i]
                    client_socket.sendall(bytes(n,'utf-8')) #GET operation to take index-data that is required to ADD.
                    print("Delivered message (from proxy to server): ",n)
                    dataReceived = client_socket.recv(1024)
                    dataReceived = dataReceived.decode('utf-8')
                    print("Received message (from server to proxy): ",dataReceived)
                    dataReceived = re.split(";",dataReceived)[2]
                    dataReceived = re.split("=",dataReceived)[1]
                    I[counter] = indc[i]                    # The oldest entry is removed.
                    data[counter] = int(dataReceived)
                    Sum = Sum + int(dataReceived)
                    counter = (counter + 1) % 5
            m = "OP=ADD;" + commandSplit[1] + ";DATA=" + str(Sum)
            conn.sendall(bytes(m,'utf-8'))
            print("Delivered message (from proxy to client): ",m)
            if(display == 1):
                visual = list(zip(I,data))
                print(tabulate(visual,headers = col_names))
        elif(op == "CLR"):
            data = [None] * 5               # The size of the data and I (Index) lists stays the same, but they dont have any values.
            I = [None] * 5
            counter = 0
            toserver = "OP=CLR;;"
            client_socket.sendall(bytes(toserver,'utf-8'))              #Sends message to SERVER to clear table.
            print("Delivered message (from proxy to server): ",toserver)
            dataReceived = client_socket.recv(1024)
            dataReceived = dataReceived.decode('utf-8')
            print("Received message (from server to proxy): ",dataReceived)
            m = "OP=CLR;DONE"
            conn.sendall(bytes(m,'utf-8'))
            print("Delivered message (from proxy to client): ",m)
            visual = list(zip(I,data))
            print(tabulate(visual,headers = col_names))
            # INF operation returns the indexes of the PROXY table.
        elif(op == "INF"):
            indexsInProxy = []
            for i in range(len(I)):
                if(I[i] != "" and I[i] != None):
                    indexsInProxy.append(I[i])
            if(len(indexsInProxy) == 0):
                indexsInProxy = "NO_DATA"      # No data (CLR operation is applied and no data is written to corresponding index.)
            else:
                indexsInProxy = ','.join(indexsInProxy)                 
            m = "OP=INF;IND=" + indexsInProxy
            conn.sendall(bytes(m,'utf-8'))
            print("Delivered message (from proxy to client): ",m)
        else:
            conn.sendall(bytes("NO SUCH OPERATION DEFINED.",'utf-8'))

