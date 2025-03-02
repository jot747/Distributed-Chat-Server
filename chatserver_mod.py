import socket
import sys
import select
import traceback

HOST = ''              #Listen on all interfaces

PORT = 50008 
WEB_PORT = 50009

webclients=[]
termclients=[]

def storeMessage(content): #Store messages in text file
    
    with open('msgs.txt', 'a') as file1:
        file1.write(content)
        
        
    #f = open("msgs.txt", "a")
    #f.write(content)
    #f.close()
    
def sendMessageToWeb(conn):
    
    with open('msgs.txt', 'r') as file1:
        msg=file1.read()

    conn.sendall(msg.encode())
            
        

def sendPriorMessages(conn):    #Send last 20 messages to client on connection
    
    
    try:
    
        with open('msgs.txt', 'r') as file1:
            Lines = file1.readlines()
        
        lastMessage=len(Lines)-1
        messagesToBeSent=min(len(Lines),20) 
                
        for i in range(lastMessage-messagesToBeSent,lastMessage):
            
            conn.sendall(Lines[i].encode())
        

    except:
        
        print("not enough messages")
        
    
    
    print("NEW CLIENT")
    
    file1.close()
    
def receiveData(conn):

    data = b'' 
    
    while True:
        chunk = conn.recv(1024)     #Receive message in chunks if it is too big(ie. over 1024 bytes)
        
        if not chunk: 
            break
        
        data += chunk  
    return data
    

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as term_socket, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as web_socket:
    
    term_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    web_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #term_socket.setblocking(False)
    #web_socket.setblocking(False)

    term_socket.bind((HOST, PORT))
    web_socket.bind((HOST,WEB_PORT))
    
    term_socket.listen()
    web_socket.listen()
    
    
    clients = []            #List of clients we will be serving
    
    while True:
        try:
            
            inputs = [term_socket,web_socket] + clients 
            
            readable, writable, exceptional = select.select(inputs, [], inputs) #Select to listen to all clients

            for client in readable: #When client is sending
                
                if client is web_socket:
                    
                    conn, addr = web_socket.accept()
                    clients.append(conn)
                    webclients.append(conn)
                                        
                                        
                    if conn in clients:
                        
                        data = conn.recv(1024)
                        msg=data.decode()
                        msgList=msg.split()
                        
                        
                        if(msgList[0]=="POST"):

                            webMessage= " ".join(msgList[1:])+"\n"
                            storeMessage(webMessage)   
                            clients.remove(conn)
                            conn.close()
                                      
                            for other in clients:  
                                
                                if(other in termclients):
                                    other.sendall(webMessage.encode())
                            
                            
                        if(msgList[0]=="GET"):
                            if(msgList[1]=="ALL"):
                                
                                sendMessageToWeb(conn)
                                clients.remove(conn)
                                conn.close()    
                                                                    
                                                                                        
                if client is term_socket:
                    # new client
                    
                    conn, addr = term_socket.accept()
                    print('Connected by', addr)
                    clients.append(conn)
                    termclients.append(conn)
                    
                    
                if client in clients:
                        
                    data = client.recv(1024)
                    msg=data.decode()
                    msgList=msg.split()
                    
                    if data:
                        
                        if client==readable[-1]:        #If we have received a new client we send them the last 20 messages
                            
                            if(len(msg.split())==1):
                                
                                print(data)
                                sendPriorMessages(conn)       
                                print(msg)
                            
                            elif (len(msg.split())>=4):     #If the message follows protocol then we store it
                                
                                msgList=msg.split()
                        
                                if(len(msgList)>=4):    
                                    
                                    username=msgList[0]
                                    time=msgList[1]
                                    
                                    storeMessage(data.decode())
                                
                                    for other in clients:   #Relay message to all other clients
                                        
                                        other.sendall(data)
                                    
                            elif (len(msg.split())==3):     #New client has entered empty message, ignore it
                                
                                print("Invalid Message")
                                    
                                
                            else:                           #New client has entered invalid username, remove them from list of clients
                                
                                print(data)
                                client.sendall(b"Invalid Username") 
                                clients.remove(client)
                                client.close()
                                print("Invalid Username")
                                
                        
                        else:                               #if the user is not the last client added,
                            
                            if (len(msg.split())>=4):
                                
                                msgList=msg.split()
                        
                                if(len(msgList)>=4):        #If the user has sent message store and relay it
                                    
                                    username=msgList[0]
                                    time=msgList[1]
                                    
                                    storeMessage(data.decode())
                                
                                for other in clients:
                                    
                                    other.sendall(data)
                                    
                            elif (len(msg.split())==3): #client has entered empty message, ignore it
                                
                                print("Invalid Message")
                                    
                                    
                    else: 
                        print("goodbye")
                        clients.remove(client)
                        client.close()
                        
            

        except KeyboardInterrupt as e:
            print("You have quit")
            sys.exit(0)
            
        except Exception as e:
            print("Something happened... I guess...")
            print(e)
            print("Exception in user code:")
            print("-"*60)
            traceback.print_exc(file=sys.stdout)
            print("-"*60)


