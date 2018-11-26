# Redes_Tarea2
Tarea 2 de Redes

## Consideraciones:

- Tanto cliente como servidor tienen el mismo numero maximo de secuencia dsitintos.
- Tanto cliente como servidor estan escritos en Python 3.
- Para iniciar el cliente se debe usar el comando
`python3 client.py [IPADDRESS] [PORTNUMBER] [FILENAME] [3-WAY HANDSHAKE]`
donde la mayoria de lso terminos se explican solos excepto `[3-WAY HANDSHAKE]` que corresponde a un `True` o un `False` dependiendo de si se quiere usar 3-way handshake o no.
- El cliente le comunica al servidor si se ocupa 3-way handshake con un parametro que se envia como un dato en el mensaje de SYN.
