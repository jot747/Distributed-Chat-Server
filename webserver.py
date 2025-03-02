import socket
import select
import threading
import sys
import json
import os
from time import gmtime, strftime

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 8000               # Arbitrary non-privileged port

page = '''<html>
<body>
Hey ya! You are the {}th visitor, click here to claim your prize.
</body>
</html>
'''

cookieHeader='''HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: {}
Set-Cookie: {}
'''

header = """HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: {}

"""

counter = 0  # Start count at 0


def reply(conn, addr):
    global counter
    with conn:
        # Receive the request data from the browser
        request = conn.recv(1024).decode()
        print('Request received:', request)

        # Check if the request is for the main page (root path "/")
        if "GET / " in request:  # Only increment counter for the main page
            counter += 1
            formattedPage = page.format(counter)
            replyHeader = header.format(len(formattedPage))
            conn.sendall(replyHeader.encode())
            conn.sendall(formattedPage.encode())
        else:
            
            # Respond with a 404 for other resources
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
            

def readCookie(request):
    
    splitRequest = request.split('\r\n')
    cookie_dict = {}
    
    for i in splitRequest:
        if("Cookie:" in i):
            
            for cookie in i.split('; '):
                key, value = cookie.split('=', 1)  # Split each cookie at the '='
                cookie_dict[key] = value  # Store in a dictionary for easy access
                
    
    return cookie_dict


def readMessage(request):
    
    splitRequest = request.split('\r\n')
    
    unParsedMessage=splitRequest[-1]
    parsed_message = json.loads(unParsedMessage)  # Parse it as JSON
    print(parsed_message['message'])
    return parsed_message['message']

    
#DEAL WITH REQUESTS           

def landingPage(conn,addr):
    
            
    with conn:
        request = conn.recv(1024).decode()
        #print('Request received:', request)
        
        print(request)
        
        if "GET / " in request:  # Only increment counter for the main page
            
            # Python code to illustrate with()
            with open("webclient.html") as file:  
                htmlPage = file.read() 

            replyHeader = header.format(len(htmlPage))
            conn.sendall(replyHeader.encode())
            conn.sendall(htmlPage.encode())
            
        elif "GET /images" in request:
            
            splitHeader=request.split(" ")
            print(splitHeader[1])
            
            fileName=splitHeader[1].split("/")[-1] 
            print(fileName)
            
            path=splitHeader[1].split("/")
                    
            textFiles = ['.py', '.txt', '.html']
            
            currentDirectory=os.getcwd()
            
            folderName='/'.join(path[:-1])
            folderName=folderName[1:]
            folderName="files/images"
            print("folder PATHHHHH "+folderName)
            
            folderDirectory=os.path.join(currentDirectory, folderName)
            os.chdir(folderDirectory)
            foundAFile = False
            serveFile=""

            for aFile in os.listdir('.'):
                
                wholePath = os.path.join(folderDirectory, aFile)
                
                print(wholePath+"\n")

                #print("File full path is {}".format(wholePath))

                if os.path.isfile(aFile):

                    if isAFileICanPrint(aFile,textFiles):
                        
                        #print("opening {}".format(aFile))
                        print("INPUT FILE "+fileName)
                        print("LIST FILES "+aFile)
                        
                        if(fileName==aFile):
                        
                            with open(aFile) as theFile:
                                serveFile=theFile.read()
                                
                            foundAFile = True
                        

                    else:

                        with open(aFile, 'rb') as binaryFile: 
                            serveFile = binaryFile.read()


            if not foundAFile:
                print("Didn't find a file in {}".format(os.getcwd()))
            
            os.chdir(currentDirectory)
            
            content_type = 'image/jpeg'
            response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(serveFile)}\r\n\r\n"

            #replyHeader = header.format(len(serveFile))
            os.chdir(currentDirectory)
            conn.sendall(response_header.encode())
            conn.sendall(serveFile)
                       
                       
        #GET http://127.0.0.1:8000/files/images/binary.jpeg
            
        elif "GET /files/" in request:  # Only increment counter for the main page
            
            splitHeader=request.split(" ")
            print(splitHeader[1])
            
            fileName=splitHeader[1].split("/")[-1] 
            print(fileName)
            
            
            path=splitHeader[1].split("/")
                    
            textFiles = ['.py', '.txt', '.html']
            imageFiles=['png','jpg','jpeg']
            
            suffix= fileName.split('.')[1]
            currentDirectory=os.getcwd()


            try:
            
                folderName='/'.join(path[:-1])
                folderName=folderName[1:]
                
                
                if(suffix in imageFiles):
                    
                    folderDirectory=currentDirectory+"/files/images"
                    
                else:
                    
                    folderDirectory=os.path.join(currentDirectory, folderName)
                
                            
                os.chdir(folderDirectory)
                foundAFile = False
                serveFile=""

                for aFile in os.listdir('.'):
                    wholePath = os.path.join(folderDirectory, aFile)

                    #print("File full path is {}".format(wholePath))

                    if os.path.isfile(aFile):

                        if isAFileICanPrint(aFile,textFiles):
                            
                            
                            if(fileName==aFile):
                            
                                with open(aFile) as theFile:
                                    serveFile=theFile.read()
                                    
                                foundAFile = True
                                os.chdir(currentDirectory)
                                replyHeader = header.format(len(serveFile))
                                conn.sendall(replyHeader.encode())
                                conn.sendall(serveFile.encode())
                            

                        else:
                            
                            if(fileName==aFile):

                                with open(aFile, 'rb') as binaryFile: 
                                    serveFile = binaryFile.read()
                                    content_type = "image/"+suffix
                                    response_header = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(serveFile)}\r\n\r\n"

                                    os.chdir(currentDirectory)
                                    conn.sendall(response_header.encode())
                                    conn.sendall(serveFile) 

                if not foundAFile:
                    print("Didn't find a file in {}".format(os.getcwd()))
                    conn.sendall(b"HTTP/1.1 404 Image Not Found\r\n\r\n")
                    os.chdir(currentDirectory)

                    
                os.chdir(currentDirectory)
            
            except FileNotFoundError:
                os.chdir(currentDirectory)
                conn.sendall(b"HTTP/1.1 404 Image Not Found\r\n\r\n")
                print("NOT FOUND")
            
        elif "POST /api/login/" in request:  # Handle login requests
            
            
            username = request.split('/api/login/')[1].split(' ')[0]  # Extract username
            response_message = f"\nWelcome, {username}!"
            
            conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nSet-Cookie: username={username}; Path=/; HttpOnly\r\nContent-Length: {len(response_message)}\r\n\r\n".encode() + response_message.encode())
            
        elif "DELETE /api/login" in request:
            
            
            print("PEACE OUT")
            
            response_message = f"\nGoodbye!"
            cookie_header = 'Set-Cookie: username=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
            
            headers = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n{cookie_header}\r\n"
            full_response = headers + f"Content-Length: {len(response_message)}\r\n\r\n" + response_message
            
            conn.sendall(full_response.encode())
        
            
        elif "POST /api/messages" in request:  # Handle login requests
            
            try:
                
                cookies= readCookie(request)
                msg= readMessage(request)
                username=cookies.get('Cookie: username')
                
                if(len(username)>0):
                        
                    timeNow = strftime("%Y-%m-%d %H:%M:%S", gmtime())
                    message= username+ " "+ timeNow + ": "+ msg+"\n"
                    
                    
                    sendToChatServer(username,message)
                    responseMessage="Message Sent"
                    
                    
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(responseMessage)}\r\n\r\n".encode() + responseMessage.encode())
                
                else:
                    conn.sendall(f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(chatMessages)}\r\n\r\n".encode() + chatMessages.encode())            

                
            except:
                
                chatMessages="403 Forbidden"
                conn.sendall(f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(chatMessages)}\r\n\r\n".encode() + chatMessages.encode())            

                       
            

        elif "GET /api/messages" in request:  # Handle login requests
            
            try:
                
                cookies= readCookie(request)
                username=cookies.get('Cookie: username')
                if username:
                    
                    chatMessages=getAllMessages(conn)
                    conn.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {len(chatMessages)}\r\n\r\n".encode() + chatMessages.encode())  

                else:
                    chatMessages="Forbidden"
                    conn.sendall(f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(chatMessages)}\r\n\r\n".encode() + chatMessages.encode())                                
                    
                          
            except:
                
                chatMessages="403 Forbidden"
                conn.sendall(f"HTTP/1.1 403 Forbidden\r\nContent-Type: text/html\r\nContent-Length: {len(chatMessages)}\r\n\r\n".encode() + chatMessages.encode())            

        
        
        else:
            
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
    
    
    
def getAllMessages(conn):
    
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.connect(('127.0.0.1', 50009))  # Connect to the server
    
    sendMsg = "GET ALL"
    serverSocket.sendall(sendMsg.encode())

    msg = b""
        
    while True:

        chunk = serverSocket.recv(1024)
        
        if not chunk:

            break
        
        msg += chunk

    msg = msg.decode()
    serverSocket.close()
    
    return msg


def getLastMessages(username,conn):
    print("ol")
    
    
def sendToChatServer(username,message):
        
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.connect(('127.0.0.1', 50009))  # Connect to the server
    
    inputs=[conn,serverSocket]  
    
    user=username
    
    sendMsg="POST "+message
    serverSocket.sendall(sendMsg.encode())
    
    while True:
        # Use select to wait for I/O events
        readable, writable, exceptional = select.select(inputs, [], [])
        msg=""

        for sock in readable:
            
            if sock == serverSocket:
                # Message from the server
                msg = sock.recv(1024)
                if msg:
                    print("FROM SERVER")
                    print(f"{msg.decode()}")
                    
                else:
                    # Server closed the connection
                    inputs.remove(serverSocket)
                    serverSocket.close()
                    break    

        if(serverSocket not in inputs):
            
            break

def isAFileICanPrint(filename,textFiles):
    for suffix in textFiles:
        if filename.endswith(suffix):
            return True #gasp!
    return False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on port {PORT}...")

    while True:
        
        conn, addr = s.accept()
        
        myThread = threading.Thread(target=landingPage, args=(conn, addr))

        myThread.start()

