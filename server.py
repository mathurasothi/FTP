import socket
import sys


''' 
This is the server program for CS 456 Assignment 1.
./server.sh <req_code> <file_to_send>
'''

# validate and initialize input parameters
if len(sys.argv) != 3:
    print('Missing parameters: <req_code>, <file_to_send>')
    exit()

reqCode    = int(sys.argv[1])     # <req_code>
fileName   = str(sys.argv[2])     # file name of file that client will download
rport      = 0                    # placeholder for <r_port>
flag       = False                # flag is set to true only if Active mode

if fileName == '':
    print("File name is invalid")
    exit()
elif int(reqCode) != reqCode:
    print("<req_code> must be an integer")
    exit()


# Negotiation Stage - UDP
serverUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverUDP.bind(('', 0))
# get <n_port> and print to stdout
serverAddr, nport = serverUDP.getsockname()
print('SERVER_PORT=%d' % nport)

while True:
    try:
        message, clientAddr = serverUDP.recvfrom(2048)

        # determine if PORT or PASV message then parse the message accordingly
        if message[0:4] == 'PORT':
            req_code = int(message[6:8])
            rport    = int(message[-5:])
            flag     = True
        elif message[0:4] == 'PASV':
            req_code = int(message[6:8])
            flag     = False

        if req_code != reqCode:
            # send negative acknowledgement to client
            print("Incorrect <req_code> provided by client")
            serverUDP.sendto('0'.encode(), clientAddr)
            continue
        elif flag == True:
            # send positive acknowledgement to client (active mode only)
            serverUDP.sendto('1'.encode(), clientAddr)
        else:
            serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverTCP.bind(('', 0))
            serverTCP.listen(1)
            rport = serverTCP.getsockname()[1]
            # send <r_port> to client (passive mode only)
            serverUDP.sendto(str(rport).encode(), clientAddr)


    # Transaction Stage - TCP

        hostname, port = clientAddr       # grab client hostname
        file       = open(fileName, "rb") # file that client will download as binary

        if flag == True: # Active Mode Transaction
            serverTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # server initiates TCP connection with client's <r_port>
            serverTCP.connect((hostname, rport))
            l = file.read(32)
            while(l):
                # send file contents to client
                serverTCP.sendto(str(l).encode(), (hostname, rport))
                l = file.read(32)

        else: # Passive Mode Transaction
            # accept client's TCP connection to server's <r_port>
            transmissionTCP, addr = serverTCP.accept()
            l = file.read(32)
            while(l):
                # send file contents to client
                transmissionTCP.sendto(str(l).encode(), (hostname, rport))
                l = file.read(32)
            transmissionTCP.close()
        
        file.close()
        serverTCP.close()
    
    except KeyboardInterrupt:
        print("")
        sys.exit()

