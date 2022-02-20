#!/bin/bash


#Number of parameters: 5
#Parameter:
#    $1: <server_address>
#    $2: <n_port>
#    $3: <mode>
#    $4: <req_code>
#    $5: <file_received>

#Run python scripts
python client.py $1 $2 "$3" $4 "$5"
