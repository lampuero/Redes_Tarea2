# Redes_Tarea2
Tarea 2 de Redes

## Para correr

- El cliente y servidor se corren con los siguientes comandos respectivamente:
    - `python3 client.py [IPADDRESS] [PORTNUMBER] [FILENAME] [3-WAY HANDSHAKE]`
    - `python3 server.py [PORTNUMBER]`
- Donde:    
    - `[IPADDRESS]` es la direccion ip del servidor.
    - `[PORTNUMBER]` el numero de puerto conde correra el servidor.
    - `[FILENAME]` nombre (con extension) del archivo a enviar.
    - `[3-WAY HANDSHAKE]` es `True` si se desea ocupar 3-way handshake ó `False` en caso contrario.
## Consideraciones:

- Tanto cliente como servidor tienen el mismo numero maximo de secuencia distintos.
- Tanto cliente como servidor estan escritos en Python 3.
- El cliente le comunica al servidor si se ocupa 3-way handshake con un parametro que se envia como un dato en el mensaje de SYN.
- El servidor setea su timeout a 1 s cuando recibe el primer mensaje SYN.
- En la ventana se guardan los mensaje codificados en byte.
- El servidor corre en localhost.
- Los archivos fueron probados enviando archivos `.txt` y `.jpg`.

## Autores

- Luis Ampuero C.
- Vicente Illanes
