# archivo de servidor
import socket
import sys

# Tipos de mensajes
SYN = 's'
ACK = 'a'
SYNACK = 'k'
FIN = 'f'
DATOS = 'd'

# Parámetros para echar a correr el recibidor
if len(sys.argv) != 2:
    print("python3 receiver.py [PORTNUMBER]")

SW_IP = ""
SW_PORT = int(sys.argv[1])
# Armamos el socket
the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Asociamos el socket a la dirección y el puerto especificados
the_socket.bind((SW_IP, SW_PORT))

# Numero max numeros de sequencia
num_seq = pow(2, 11)
# Establecemos parámetros
buf = 1024
expected_seq = 0
seq = 0
last_ack_message = ""
# Abrimos archivo para guardar datos
downloading_file = open("received_file", "wb")

# Seteamos un timeout
the_socket.settimeout(1)


# Contador de intentos
try_counter = 0
address = b'0'
# Continuamos con la secuencia de descarga
while True:
    try:
        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            print("error")
            break

        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)

        # Si no me llegó nada, paramos
        if not rmessage:
            break

        header, data = str(rmessage).split("&&&")
        rnum_seq, rnum_ack, rtype = header.split("|||")

        # Si no es lo que esperabamos, descartamos
        if str(rnum_seq) != str(expected_seq):
            the_socket.sendto(bytes(last_ack_message), address)
            continue
        elif str(type) == str(DATOS):
            downloading_file.write(data)

            # Enviamos el ack para que el enviador sepa que los datos llegaron
            try_counter = 0
            expected_seq = (expected_seq + 1) % num_seq
            seq = (seq + 1) % num_seq
            header = str(seq) + "|||" + str(expected_seq) + "|" + str(ACK)
            message = header + "&&&" + ""
            the_socket.sendto(bytes(message), address)
            last_ack_message = message
        elif str(type) == str(FIN):
            break
    except:
        try_counter += 1
        the_socket.sendto(bytes(last_ack_message), address)


# Cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y, si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print("File Downloaded")
