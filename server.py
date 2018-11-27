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
# Abrimos archivo para guardar datos
downloading_file = open("received_file.txt", "wb")

# Contador de intentos
try_counter = 0
address = ("", 0)
message = ""
# Conexion
send_SYNACK = False
three_way = 1
while True:
    rmessage, address = the_socket.recvfrom(buf)
    if rmessage:
        header, data = rmessage.decode().split("&&&")
        rSeq, rAck, rType = header.split("|||")
        print("LLego1: {}".format(rmessage.decode()))
        if str(rType) == str(SYN):
            ack = (int(rSeq) + 1) % num_seq
            header = str(seq) + "|||" + str(ack) + "|||" + str(SYNACK)
            message = header + "&&&" + ""
            seq = (seq + 1) % num_seq
            expected_seq = (int(rSeq) + 1) % num_seq
            the_socket.sendto(message.encode(), address)
            print("Envio: {}".format(message))
            three_way = int(data)
            break

while three_way == 1:
    try:
        rmessage, address = the_socket.recvfrom(buf)
        print("LLego2: {}".format(rmessage.decode()))
        if rmessage:
            header, data = rmessage.decode().split("&&&")
            rSeq, rAck, rType = header.split("|||")
            if int(rSeq) == expected_seq and str(rType) == str(ACK) and int(rAck) == int(seq):
                expected_seq = (expected_seq + 1) % num_seq
                break
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message.encode(), address)

# Descarga

# Seteamos un timeout
# the_socket.settimeout(1)

# recibo nombre archivo
while True:
    try:
        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir nombre archivo")
            break
        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)
        print("LLego3: {}".format(rmessage.decode()))
        if rmessage:
            header, data = rmessage.decode().split("&&&")
            rSeq, rAck, rType = header.split("|||")
            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                the_socket.sendto(message.encode(), address)
                continue
            elif str(rType) == str(DATOS):
                downloading_file.close()
                downloading_file = open("received_" + str(data), "wb")
                expected_seq = (expected_seq + 1) % num_seq
                header = str(seq) + "|||" + str(expected_seq) + "|||" + str(ACK)
                message = header + "&&&" + ""
                seq = (seq + 1) % num_seq
                the_socket.sendto(message.encode(), address)
                print("Envio1: {}".format(message))
                break
            try_counter = 0
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message.encode(), address)
# Descarga archivo
try_counter = 0
while True:
    try:
        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir datos de archivo")
            break

        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)
        if rmessage:
            header, data = rmessage.decode().split("&&&")
            print("LLego4: este header {}".format(header))
            rSeq, rAck, rType = header.split("|||")
            print("Llego {} y espero {}".format(rSeq, expected_seq))
            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                the_socket.sendto(message.encode(), address)
                continue
            elif str(rType) == str(DATOS):
                downloading_file.write(data.encode())
                expected_seq = (expected_seq + 1) % num_seq
                seq = (seq + 1) % num_seq
                header = str(seq) + "|||" + str(expected_seq) + "|||" + str(ACK)
                message = header + "&&&" + ""
                the_socket.sendto(message.encode(), address)
            elif str(rType) == str(FIN):
                ack = (int(rSeq) + 1) % num_seq
                header = str(seq) + "|||" + str(ack) + "|||" + str(ACK)
                message = header + "&&&" + ""
                seq = (seq + 1) % num_seq
                the_socket.sendto(message.encode(), address)
                break
            try_counter = 0
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message.encode(), address)
        print("Envio2: {}".format(message))

# Finalizar conexion
end_conection = [message]
header = str(seq) + "|||" + str(-1) + "|||" + str(FIN)
message = header + "&&&" + ""
the_socket.sendto(message.encode(), address)
end_conection.append(message)
while True:
    try:
        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al esperar ACK de FIN")
            break
        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)
        print("LLego5: {}".format(rmessage.decode()))
        if rmessage:
            header, data = rmessage.decode().split("&&&")
            rSeq, rAck, rType = header.split("|||")

            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                the_socket.sendto(message.encode(), address)
                continue
            elif str(rType) == str(ACK):
                break
            try_counter = 0
    except Exception as e:
        print(e)
        try_counter += 1
        i = 0
        for msg in end_conection:
            the_socket.sendto(msg.encode(), address)
            i += 1
# Cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y, si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print("File Downloaded")
