# -*- coding: utf-8 -*-
import socket
import sys
import os

# Parámetros para echar a correr el enviador
if len(sys.argv) != 4:
    print("python sender.py [IPADDRESS] [PORTNUMBER] [FILENAME]")
    sys.exit()

# Armamos el socket
the_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# Obtenemos el puerto y la IP
Server_IP = sys.argv[1]
Server_Port = int(sys.argv[2])

# Establecemos parámetros
buf = 1024
address = (Server_IP,Server_Port)
seq = 0
ack = 0
syn = 1
# Obtenemos los parámetros del archivo a enviar
file_name=sys.argv[3]
total_size = os.path.getsize(file_name)
current_size = 0
percent = round(0,2)

# while para three-way handshake
while True:

    # Esperamos un SYN para iniciar conección y la dirección del socket que mandó los datos
    data, address = the_socket.recvfrom(buf)

    if data:
        # Separamos los datos recibidos
        (syn_client, seq_client) = data.split("|||")

        # Si recibimos el SYN esperado, se reserva un buffer para el cliente
        if str(syn) == str(syn_client):
            buf = 1024
            ack = int(str(seq_client))
            # 'Codificamos' el SYNACK y el numero de secuencia X a mandar
            data = str(syn) + "|||" + str(ack) + "|||" + str(seq)
            #enviamos SYNACK
            the_socket.sendto(str(ack), address)
            # Actualizamos el ack
            ack = int(str(seq_client)) + 1

            #Actualizamos el numero de secuencia
            seq += 1
            break

#esperamos ACK del SYNACK para comenzar a enviar datos
while True:
    data, address = the_socket.recvfrom(buf)
    if data:
        # Separamos los datos recibidos
        (ack_client, seq_client) = data.split("|||")
        # Si recibimos el ACK esperado, terminamos 3-way
        if str(ack_client) == str(seq):
            break

#enviamos datos
#(...)

# Cerramos conexión y archivo
the_socket.close()
