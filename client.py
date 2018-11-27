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
if len(sys.argv) != 5:
    print("python3 client.py [IPADDRESS] [PORTNUMBER] [FILENAME] [3-WAY HANDSHAKE]")
    sys.exit()

# Armamos el socket
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Procesamos los datos ingresados por el usuario
Server_IP = sys.argv[1]
Server_Port = int(sys.argv[2])
file_name = sys.argv[3]
three_way = 1
if sys.argv[4] != "True":
    three_way = 0
# Establecemos parámetros
address = (Server_IP, Server_Port)

buf = 1024

num_seq = pow(2, 11)
window_size = 5
window_start = 0
window_messages = []
send_times = []

last_send = -1
next_to_send = 0

seq = 0
ack = 0
received_message = b''

overflow = 0

send_file = False
received_ack = False
# tiempo de inicio
start_time = datetime.datetime.now()
# Conexion
header = "{:04}|{:04}|{}".format(seq, -1, SYN)
data = str(three_way)
message = header.encode() + data.encode()
seq = (seq + 1) % num_seq
the_socket.sendto(message, address)
the_socket.settimeout(timeout)
# while para handshake
try_counter = 0
while True:
    try:
        received_message, address = the_socket.recvfrom(buf)
        if received_message:
            # Separamos los datos recibidos
            received_time = datetime.datetime.now()
            received_header = received_message[:11].decode()
            received_data = received_message[11:]
            rSeq, rAck, rType = received_header.split("|")
            if str(rType) == str(SYNACK) and int(seq) == int(rAck):
                if three_way == 1:
                    ack = (int(rSeq) + 1) % num_seq
                    header = "{:04}|{:04}|{}".format(seq, ack, ACK)
                    message = header.encode() + b''
                    window_start = seq
                    seq = (seq + 1) % num_seq
                    the_socket.sendto(message, address)
                    send_times.append(datetime.datetime.now())
                    window_messages.append(message)
                break
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message, address)
        the_socket.settimeout(timeout)

# Envio de Datos

# Abrimos el archivo
sending_file = open(file_name, "rb")
finished_reading = False
finished_sending = False

# Envio el nombre
header = "{:04}|{:04}|{}".format(seq, -1, DATOS)
data = str(file_name)
message = header.encode() + data.encode()
seq = (seq + 1) % num_seq
the_socket.sendto(message, address)

the_socket.settimeout(timeout)
send_times.append(datetime.datetime.now())
window_messages.append(message)

while not finished_sending:
    try:
        if try_counter == 10:
            print("Error: espera en el envio de archivo")
            break
        received_message, address = the_socket.recvfrom(buf)
        received_time = datetime.datetime.now()
        received_header = received_message[:11].decode()
        received_data = received_message[11:]
        rSeq, rAck, rType = received_header.split("|")
        if rType == ACK:
            received_ack = True
            while window_start < int(rAck) + overflow*num_seq:
                sample = received_time - send_times[0]
                del send_times[0], window_messages[0]
                window_start = (window_start + 1) % num_seq
                if window_start == 0:
                    overflow = 0
                if window_start == int(rAck):
                    karn_algorithm(sample.total_seconds())
            if finished_reading and len(window_messages) == 0:
                finished_sending = True
                break
        try_counter = 0
    except Exception as e:
        print("Excepcion es: {}".format(e))
        if not received_ack:
            timeout = 2*timeout
        # Si ocurre un error avisamos y aumentamos el contador
        try_counter += 1
        for msg in window_messages:
            the_socket.sendto(msg, address)
        the_socket.settimeout(timeout)

    while (not finished_reading) and len(window_messages) < window_size:
        header = "{:04}|{:04}|{}".format(seq, -1, DATOS)
        data = sending_file.read(buf - len(header))
        if not data:
            finished_reading = True
            break
        message = header.encode() + data
        the_socket.sendto(message, address)
        the_socket.settimeout(timeout)
        send_times.append(datetime.datetime.now())
        window_messages.append(message)
        if seq == num_seq:
            overflow = 1
        seq = (seq + 1) % num_seq

# Fin de conexion
print("empiezo fin de conexion")
header = "{:04}|{:04}|{}".format(seq, -1, FIN)
message = header.encode() + b''
the_socket.sendto(message, address)
the_socket.settimeout(timeout)
# espero ack de fin
while True:
    try:
        if try_counter == 10:
            print("Error: espera de ack para fin")
            break
        received_message, address = the_socket.recvfrom(buf)
        received_time = datetime.datetime.now()
        received_header = received_message[:11].decode()
        received_data = received_message[11:]
        rSeq, rAck, rType = received_header.split("|")
        if str(rType) == str(ACK) and int(rAck) == int(seq):
            break
    except socket.timeout:
        try_counter += 1
        the_socket.sendto(message, address)
        the_socket.settimeout(timeout)
    except Exception as e:
        print("Excepcion1 es: {}".format(e))

# espero fin para enviar ack
while True:
    try:
        if try_counter == 10:
            print("Error: espera de fin de servidor para ack")
            break
        received_message, address = the_socket.recvfrom(buf)
        received_time = datetime.datetime.now()
        received_header = received_message[:11].decode()
        received_data = received_message[11:]
        rSeq, rAck, rType = received_header.split("|||")
        if str(rType) == str(FIN):
            ack = (int(rSeq) + 1) % num_seq
            header = "{:04}|{:04}|{}".format(seq, ack, ACK)
            message = header.encode() + b''
            the_socket.sendto(message, address)
            break
    except socket.timeout:
        try_counter += 1
        the_socket.sendto(message, address)
        the_socket.settimeout(timeout)
    except Exception as e:
        print("Excepcion2 es: {}".format(e))

# poner reloj al principio y al final e imprimir
# Cerramos conexión y archivo
the_socket.close()
sending_file.close()

# tiempo de inicio
end_time = datetime.datetime.now()
delta = end_time - start_time
print("El tiempo de duracion es {} segundos".format(delta.total_seconds()))