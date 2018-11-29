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

# Espera SYN
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

# Seteamos un timeout
the_socket.settimeout(1)

# Espera ACK en caso 3-way
while three_way == 1:
    try:
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir ACK de SYNACK")
            break

        rmessage, address = the_socket.recvfrom(buf)

        if rmessage:

            try_counter = 0

            header = rmessage[:11].decode()
            data = rmessage[11:]

            rSeq, rAck, rType = header.split("|")

            if int(rSeq) == expected_seq and str(rType) == str(ACK) and int(rAck) == int(seq):
                expected_seq = (expected_seq + 1) % num_seq
                break

    except socket.timeout as e:
        print("Excepcion es: {}".format(e))
        try_counter += 1
        the_socket.sendto(message, address)

    except Exception as e:
        print("Excepcion es: {}".format(e))


# Descarga

# Nombre archivo
filename = ".txt"

# Recibo nombre archivo
while True:
    try:
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir nombre de archivo")
            break

        rmessage, address = the_socket.recvfrom(buf)

        if rmessage:

            try_counter = 0

            header = rmessage[:11].decode()
            data = rmessage[11:]

            rSeq, rAck, rType = header.split("|")

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
                try_counter = 0
                break

    except socket.timeout as e:
        print("Excepcion es: {}".format(e))
        try_counter += 1
        the_socket.sendto(message, address)

    except Exception as e:
        print("Excepcion es: {}".format(e))


# Abrimos archivo para guardar datos
downloading_file = open("received_" + filename, "wb")

# Descarga archivo

while True:
    try:
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al recibir datos de archivo")
            break

        rmessage, address = the_socket.recvfrom(buf)

        if rmessage:

            try_counter = 0

            header = rmessage[:11].decode()
            data = rmessage[11:]

            rSeq, rAck, rType = header.split("|")

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

            elif str(rType) == str(FIN):
                ack = (int(rSeq) + 1) % num_seq
                header = "{:04}|{:04}|{}".format(seq, ack, ACK)
                message = header.encode() + b''
                the_socket.sendto(message, address)
                seq = (seq + 1) % num_seq
                expected_seq = (expected_seq + 1) % num_seq
                break
    except socket.timeout as e:
        print("Excepcion es: {}".format(e))
        try_counter += 1
        the_socket.sendto(message, address)

    except Exception as e:
        print("Excepcion es: {}".format(e))

# Finalizar conexion
# Guardo ultimo ACK enviado
end_conection = [message]

# Envio FIN
header = "{:04}|{:04}|{}".format(seq, -1, FIN)
message = header.encode() + b''
the_socket.sendto(message, address)
seq = (seq + 1) % num_seq

# Guardo FIN enviado
end_conection.append(message)

# Espero ACK de FIN
while True:
    try:
        if try_counter == 10:
            print("Error: Alcanzado maximos intentos al esperar ACK de FIN")
            break
        # Obtenemos los datos desde el socket
        rmessage, address = the_socket.recvfrom(buf)
        if rmessage:

            try_counter = 0

            header = rmessage[:11].decode()
            data = rmessage[11:]

            rSeq, rAck, rType = header.split("|")

            if int(rSeq) != int(expected_seq):
                for msg in end_conection:
                    the_socket.sendto(msg, address)
                continue
            elif str(rType) == str(ACK):
                break

    except socket.timeout as e:
        print("Excepcion es: {}".format(e))
        try_counter += 1
        for msg in end_conection:
            the_socket.sendto(msg, address)

    except Exception as e:
        print("Excepcion es: {}".format(e))

# Cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y, si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print("File Downloaded")
