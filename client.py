# archivo de cliente
import socket
import sys
import os
import datetime

SampleRTT = 0
EstimatedRTT = 0
DevRTT = 0
timeout = 1
alpha = 1/8
beta = 1/4


def karn_algorithm(sample):
    global SampleRTT, EstimatedRTT, DevRTT, timeout
    SampleRTT = sample
    EstimatedRTT = (1-alpha)*EstimatedRTT + alpha*SampleRTT
    DevRTT = (1-beta)*DevRTT + beta*abs(SampleRTT-EstimatedRTT)
    timeout = EstimatedRTT + 4*DevRTT


# Go back N

# Tipos de mensajes
SYN = 's'
ACK = 'a'
SYNACK = 'k'
FIN = 'f'
DATOS = 'd'


# Parámetros para echar a correr el enviador
if len(sys.argv) != 4:
    print("python3 client.py [IPADDRESS] [PORTNUMBER] [FILENAME]")
    sys.exit()

# Armamos el socket
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Obtenemos el puerto y la IP
Server_IP = sys.argv[1]
Server_Port = int(sys.argv[2])

# Establecemos parámetros
buf = 1024
address = (Server_IP, Server_Port)
window_size = 5
# Numero max numeros de sequencia
num_seq = pow(2, 11)
seq = 0
ack = 0
received_message = ""
window_start = 0
last_send = -1
next_to_send = 0
overflow = 0
window_messages = []
send_file = False
received_ack = False
send_times = []
# Obtenemos los parámetros del archivo a enviar
file_name = sys.argv[3]

# Abrimos el archivo
sending_file = open(file_name,"rb")

# 'Codificamos' el header
# header = seq + "|||" + ack num + "|||" + "type message"
header = str(seq) + "|||" + str(-1) + "|||" + str(DATOS)
data = str(file_name)
message = header + "&&&" + data
# header = seq + "|||" + ack num + "|||" + "flag SYN" + "|||" + "flag ACK" + "|||" + "flag FIN"
# while para enviar datos

while not send_file:
    try_counter = 0
    while len(window_messages) < window_size:
        header = str(seq) + "|||" + str(-1) + str(DATOS)
        data = sending_file.read(buf - len(header + "&&&"))
        message = header + "&&&" + str(data)
        the_socket.sendto(bytes(message), address)
        the_socket.settimeout(timeout)
        send_times.append(datetime.datetime.now())
        window_messages.append(message)
        if seq == num_seq:
            overflow = 1
        seq = (seq + 1) % num_seq

    try:
        if try_counter == 10:
            print("error")
            break
        received_message, address = the_socket.recvfrom(buf)
        received_time = datetime.datetime.now()
        received_header, received_data = str(received_message).split("|||")
        rseq, rack, rtype = received_header.split("|||")
        if str(rtype) == str(ACK):
            received_ack = True
            while window_start < int(rack) + overflow*num_seq:
                sample = received_time - send_times[0]
                del send_times[0]
                del window_messages[0]
                karn_algorithm(sample.total_seconds())
                window_start = (window_start + 1) % num_seq
                if window_start == 0:
                    overflow = 0

    except:
        if not received_ack:
            timeout = 2*timeout
        # Si ocurre un error avisamos y aumentamos el contador
        try_counter += 1
        i = 0
        while i < window_size:
            the_socket.sendto(bytes(window_messages[i]), address)
        the_socket.settimeout(timeout)


# Cerramos conexión y archivo
the_socket.close()
sending_file.close()
