from fileinput import filename
import socket
import sys
import os

''' 
This is the client program for CS 456 Assignment 1.
./client.sh <server address> <n_port> <mode> <req_code> <file_received>
'''

# validate and initialize input parameters
if len(sys.argv) != 6:
    print('Missing parameters: <server address>, <n_port>, <mode>, <file_received>')
    exit()

fileName   = str(sys.argv[5]) # file name where file will be saved
if not os.path.isfile(fileName):
      open(fileName, 'a').close()     # create file if it does not exist

serverAddr = str(sys.argv[1]) # server hostname
nport      = int(sys.argv[2]) # negotiation port
mode       = str(sys.argv[3]) # active or passive
reqCode    = int(sys.argv[4]) # <req_code>
rport      = 0                # placeholder for <r_port>

if not (mode == 'A' or mode == 'P'):
    print("Mode must be either 'A' for active or 'P' for passive.")
    exit()
elif fileName == '':
    print("Not a valid file name")
    exit()
elif int(reqCode) != reqCode:
    print("<req_code> must be an integer")
    exit()


# Negotiation Stage - UDP
clientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if mode == 'A': # Active Mode Negotiation
    clientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientTCP.bind(('', 0))
    # client listening on <r_port>
    clientTCP.listen(1)
    rport = clientTCP.getsockname()[1]
    # request message is PORT with <req_code> and <r_port>
    message = 'PORT: ' + str(reqCode) + ' ' + str(rport)
    clientUDP.sendto(str(message).encode(), (serverAddr, nport))

    ack = clientUDP.recv(2048).decode()
    if int(ack) == 0:
        print("Incorrect <req_code> passed to server.")
        exit()
elif mode == 'P': # Passive Mode Negotiation 
    # request message is PASV with <req_code>
    message = 'PASV: ' + str(reqCode)
    clientUDP.sendto(message.encode(), (serverAddr, nport))
    rport = int(clientUDP.recv(2048).decode())

clientUDP.close()


# Transaction Stage
if mode == 'A': # Active Mode Transaction
    # client accepts TCP connection from server
    transmissionTCP, addr = clientTCP.accept()
    # open <file_received> and write to it
    with open(fileName, "w") as f:
        while True:
            byte = transmissionTCP.recv(32)
            if not byte:
                break
            f.write(byte)
elif mode == 'P': # Passive Mode Transaction
    clientTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client initiates TCP connection with server's <r_port>
    clientTCP.connect((serverAddr, rport))
    # open <file_received> and write to it
    with open(fileName, "w") as f:
        while True:
            byte = clientTCP.recv(32)
            if not byte:
                break
            f.write(byte)


clientTCP.close()
sys.exit()
