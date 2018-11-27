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
    print("python3 server.py [PORTNUMBER]")
    sys.exit()

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
        header = rmessage[:11].decode()
        data = rmessage[11:]
        rSeq, rAck, rType = header.split("|")
        if str(rType) == str(SYN):
            ack = (int(rSeq) + 1) % num_seq
            header = "{:04}|{:04}|{}".format(seq, ack, SYNACK)
            message = header.encode() + b''
            seq = (seq + 1) % num_seq
            expected_seq = (int(rSeq) + 1) % num_seq
            the_socket.sendto(message, address)
            three_way = int(data)
            break

while three_way == 1:
    try:
        rmessage, address = the_socket.recvfrom(buf)
        if rmessage:
            header = rmessage[:11].decode()
            data = rmessage[11:]
            rSeq, rAck, rType = header.split("|")
            if int(rSeq) == expected_seq and str(rType) == str(ACK) and int(rAck) == int(seq):
                expected_seq = (expected_seq + 1) % num_seq
                break
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message, address)

# Descarga


# Seteamos un timeout
the_socket.settimeout(1)

filename = ".txt"
# recibo nombre archivo
while True:
    try:
        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir nombre archivo")
            break
        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)
        if rmessage:
            header = rmessage[:11].decode()
            data = rmessage[11:]
            rSeq, rAck, rType = header.split("|")
            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                the_socket.sendto(message, address)
                continue
            elif str(rType) == str(DATOS):
                filename = data.decode()
                ack = (int(rSeq) + 1) % num_seq
                header = "{:04}|{:04}|{}".format(seq, ack, ACK)
                message = header.encode() + b''
                seq = (seq + 1) % num_seq
                expected_seq = (expected_seq + 1) % num_seq
                the_socket.sendto(message, address)
                break
            try_counter = 0
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message, address)

# Abrimos archivo para guardar datos
downloading_file = open("received_" + filename, "wb")

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
            header = rmessage[:11].decode()
            data = rmessage[11:]
            rSeq, rAck, rType = header.split("|")
            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                the_socket.sendto(message, address)
                continue
            elif str(rType) == str(DATOS):
                downloading_file.write(data)
                ack = (int(rSeq) + 1) % num_seq
                header = "{:04}|{:04}|{}".format(seq, ack, ACK)
                message = header.encode() + b''
                the_socket.sendto(message, address)
                # actualizo secuencia de proximo mensaje a enviar y la secuencia esperada de proximo mensaje a recibir
                seq = (seq + 1) % num_seq
                expected_seq = (expected_seq + 1) % num_seq
                # reinicio counter de intentos
                try_counter = 0
            elif str(rType) == str(FIN):
                ack = (int(rSeq) + 1) % num_seq
                header = "{:04}|{:04}|{}".format(seq, ack, ACK)
                message = header.encode() + b''
                the_socket.sendto(message, address)
                seq = (seq + 1) % num_seq
                expected_seq = (expected_seq + 1) % num_seq
                break
    except Exception as e:
        print(e)
        try_counter += 1
        the_socket.sendto(message, address)

# Finalizar conexion
end_conection = [message]
print(f'envie {message}')
header = "{:04}|{:04}|{}".format(seq, -1, FIN)
message = header.encode() + b''
the_socket.sendto(message, address)
print(f'envio ahora {message}')
seq = (seq + 1) % num_seq
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
            header = rmessage[:11].decode()
            data = rmessage[11:]
            rSeq, rAck, rType = header.split("|")
            # Si no es lo que esperabamos, descartamos
            if int(rSeq) != int(expected_seq):
                for msg in end_conection:
                    the_socket.sendto(msg, address)
                continue
            elif str(rType) == str(ACK):
                break
            try_counter = 0
    except Exception as e:
        print(e)
        try_counter += 1
        for msg in end_conection:
            the_socket.sendto(msg, address)
# Cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y, si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print("File Downloaded")
