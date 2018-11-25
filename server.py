# archivo de servidor
import socket
import sys

# Tipos de mensajes
SYN = 's'
ACK = 'a'
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

# Establecemos parámetros
buf = 1024
ack = 0
current_size = 0
percent = round(0, 2)
can_receive = True
expected_seq = 0
seq = 0
# Partimos con la secuencia inicial: aquí abrimos el archivo a descargar
while True:
    # Recibimos un string con los datos y la dirección del socket que mandó los datos
    message, address = the_socket.recvfrom(buf)

    if message:
        # Separamos los datos recibidos
        header, data = message.split("&&&")
        num_seq, num_ack, flag_SYN, flag_ACK, flag_FIN = header.split("|||")
        file_name, total_size = data.split("|||")

        # Si recibimos los datos que esperabamos guardamos el archivo
        if str(num_seq) == str(expected_seq):
            downloading_file = open("received_" + file_name, "wb")
            # Actualizamos el ack
            expected_seq = (expected_seq + 1) % 10
            # Enviamos el ack
            header = str(seq) + "|||" + str(expected_seq) + "|||" + str(0) + "|||" + str(1) + "|||" + str(0)
            message = header + "&&&" + ""
            the_socket.sendto(message, address)
            break

# Seteamos un timeout (bloqueamos el socket después de 0.5s)
the_socket.settimeout(0.5)

# Contador de intentos
try_counter = 0

# Continuamos con la secuencia de descarga
while True:
    if can_receive:
        try:
            # Si en 10 intentos no funciona, salimos
            if try_counter == 10:
                print("error")
                break

            # Obtenemos los datos desde el socket
            message, address = the_socket.recvfrom(buf)

            # Si no me llegó nada, paramos
            if not message:
                break

            # Obtenemos el número de secuencia y los datos
            header, data = message.split("&&&")
            num_seq, num_ack, rtype = header.split("|||")

            # Si no es lo que esperabamos, descartamos
            if str(num_seq) != str(expected_seq):
                print("seq is not equal to ack")
                continue
            # Si es, el socket queda tomado
            can_receive = False
        except:
            pass
            # Si ocurre un error avisamos y aumentamos el contador
            #try_counter += 1
            #print("timed out")
            #the_socket.sendto(str(ack), address)

    if not can_receive:
        # Escribimos los datos en el archivo que abrimos antes
        downloading_file.write(data)

        # Enviamos el ack para que el enviador sepa que los datos llegaron
        try_counter = 0
        expected_seq = (expected_seq + 1) % 10
        header = str(seq) + "|||" + str(expected_seq) + "|||" + str(0) + "|||" + str(1) + "|||" + str(0)
        message = header + "&&&" + ""
        the_socket.sendto(message, address)

        # Ahora podemos volver a recibir cosas
        can_receive = True

# Cerramos conexion y archivo
downloading_file.close()
the_socket.close()

# y, si no fallamos mucho, el archivo fue descargado :D
if try_counter < 10:
    print("File Downloaded")
