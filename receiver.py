# -*- coding: utf-8 -*-
import socket
import sys


# Parámetros para echar a correr el recibidor
if len(sys.argv) != 2:
    print("python receiver.py [IPADDRESS] [PORTNUMBER]")


SW_IP = int(sys.argv[1])
SW_PORT = int(sys.argv[2])
# Armamos el socket
the_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# Asociamos el socket a la dirección y el puerto especificados
the_socket.bind((SW_IP,SW_PORT))

# Establecemos parámetros
buf = 1024
ack = 0
seq = 0
current_size = 0
percent = round(0,2)
can_receive = True
syn = 1
address = (SW_IP,SW_PORT)

#Three-Way Handshake

# 'Codificamos' el SYN y el numero de secuencia X a mandar
data = str(syn) + "|||" + str(seq)

#Mandamos el SYN X
the_socket.sendto(data,address)

#Actualizamos el ACK a X + 1
ack = seq + 1

# Quedamos esperando el SYN-ACK del servidor
while True:
    # Recibimos un string con los datos y la dirección del socket que mandó los datos
    data, address = the_socket.recvfrom(buf)

    if data:
        # Separamos los datos recibidos
        (syn_serv, ack_serv, seq_serv) = data.split("|||")

        # Si recibimos el ACK esperado, enviamos confirmación para terminar 3-way
        if str(ack_serv) == str(ack) and str(syn) == str(syn_serv):


            # Actualizamos el ack
            ack = int(str(seq_serv)) + 1

            #Actualizamos el numero de secuencia
            seq = int(str(ack_serv))


            # Enviamos el ack y numero de secuencia
            data = str(syn) + "|||" + str(seq)

            the_socket.sendto(str(ack),address)
            break

#ahora esperamos los datos

#...

# Cerramos conexion
the_socket.close()

