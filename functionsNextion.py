
import sqlite3
import time

import serial as sr
import serial.tools.list_ports
import io

def main():
    if not nextion.is_open: #Si la conexión no se ha realizado, iniciamos
        nextion.open()
    if nextion.is_open:
        print('Conexión serial establecida correctamente') #Comprobamos que la conexión serial se ha establecido
    else:
        print('Ha ocurrido un error al establecer la conexión serial')
    connect = sqlite3.connect('openfoods.sqlite')
    c = connect.cursor()
    print('Iniciado')
    while True: #Iniciamos un bucle infinito que lea constantemente en que página de la interfaz nos encontramos
        # sio.write(b"sendme\n") #Pedimos a la pantalla que nos diga en que página se encuentrau
        # sio.flush()
        nextion.write(b"sendme\xFF\xFF\xFF")
        # pagina = nextion.readline().decode().strip("\r\n") #La pantalla nos da la información que hemos pedido
        pagina = nextion.read(100) # Numero de bytes grande para que lea la linea entera
        pagina = parse_pagina(pagina) 
        print(f"{pagina=}, longitud={len(pagina)}, pagina[1]={pagina[1]}, pagina[0]={pagina[0]}")
        if not pagina:
            print('Esto no lee nada')
        if pagina == 'page 1': #Si el lenctor escanea un producto mientras estamos en la página 1 se añadirá a la base de datos
            print('Estas en la pagina 1')
            codigo = input("Ingrese el código del producto: ")
            print(f"{codigo=}")
            c.execute('SELECT * FROM productos WHERE ean = ?', (codigo,)) #Comprobamos que el producto este en la base de datos de productos
            producto = c.fetchone()
            print(producto)
            if producto is not None:
                c.execute('INSERT INTO nevera (ean, nombre, producto) VALUES (?, ?, ?)', (producto[0], producto[1], producto[2])) #Añadimos el producto a la nevera
                print("Producto insertado con exito")
            else:
                print("Error, el producto no existe")


        if pagina == 'page 2': #En la página 2 tenemos la lista de ingredientes
            ingredients(c, 0, 4) #Explicación en la función

        if pagina == 'page 3': #En la página 3 tenemos la lista de recetas
            recetas(c, 0, 4) #Explicación en la función

        time.sleep(0.1) #Para evitar saturación

def ingredients(c, init, fin): #Como parámetros damos el cursor de la bbdd, y dos ints que delimitan el rango de la lista de productos en la nevera
                                #que se va a mostrar en la pantalla
    c.execute('SELECT nombre FROM nevera') #Extraemos el nombre de todos los productos de la nevera
    ingLista = c.fetchall()

    if fin > len(ingLista)-1: #Si el fin del rango es mayor al tamaño de la lista, leeremos los últimos 5 productos
        fin = len(ingLista)-1
        init = fin - 4

    if init < 0: #Si el rango inicial es menor que 0, leeremos los 5 primeros productos
        init = 0
        fin = 4
    c = init
    diff = fin - init #La cantidad de productos que mostraremos
    for i in range(0, diff):
        nextion.write(("txt"+str(i+1)+".txt=\"" + ingLista[c] + "\"").encode) #Cambiamos el valor del texto de la pantalla
        c = c+1

    nextion.write(b'get ~touched.id~') #Preguntamos a la pantalla que campo se ha tocado
    event = nextion.readline().decode().strip() #Recibimos la respuesta de la pantalla


    if event.startswith('click btnavz'): #Si se pulsa el botón de avanzar, se vuelve a ejecutar la función con los siguientes 5 ingredientes
        i = init + 5
        f = fin + 5
        ingredients(c, i, f)
    elif event.startswith('click btnret'): #Si se pulsa el botón de retroceder, se vuelve a ejecutar la función con los 5 ingredientes anteriores
        i = init - 5
        f = fin - 5
        ingredients(c, i, f)

    elif event.startswith('t'): #Si se pulsa algún ingrediente, se muestra los detalles de ese ingrediente
        nextion.write('get ' + event)# Le pedimos a la pantalla que nos muestre el ingrediente del que queremos los detalles
        ingrediente = nextion.readline().decode().strip()
        nextion.write(b'page page5') #Cambiamos a la pantalla 5


def recetas(c, init, fin):#Como parámetros damos el cursor de la bbdd, y dos ints que delimitan el rango de la lista de recetas
                             #que se va a mostrar en la pantalla
    c.execute('SELECT nombre FROM recetas') #Buscamos en la base de datos todas las recetas
    recLista = c.fetchall()

    if fin > len(recLista) - 1: #Si el fin del rango es mayor al tamaño de la lista, leeremos los últimos 5 productos
        fin = len(recLista) - 1

    if init < 0: #Si el rango inicial es menor que 0, leeremos los 5 primeros productos
        init = 0
        fin = 4
    c = init
    diff = fin - init #La cantidad de productos que mostraremos
    for i in range(0, diff):
        nextion.write(("t" + str(i + 1) + ".txt=\"" + recLista[c] + "\"").encode) #Cambiamos el valor del texto de la pantalla
        c = c + 1



    nextion.write(b'get ~touched.id~') #Preguntamos a la pantalla que campo se ha tocado
    event = nextion.readline().decode().strip() #Recibimos la respuesta de la pantalla

    if event.startswith('btn_avz'): #Si se pulsa el botón de avanzar, se vuelve a ejecutar la función con los siguientes 5 ingredientes
        i = init + 5
        f = fin + 5
        recetas(c, i, f)
    elif event.startswith('btn_retr'): #Si se pulsa el botón de retroceder, se vuelve a ejecutar la función con los 5 ingredientes anteriores
        i = init - 5
        f = fin - 5
        recetas(c, i, f)

    elif event.startswith('t'): #Si se pulsa alguna receta, se muestra el contenido de la receta
        nextion.write('get ' + event) #Le pedimos a la pantalla que nos muestre el ingrediente del que queremos los detalles
        rec = nextion.readline().decode().strip()
        nextion.write(b'page page4') #Nos movemos a la pagina 4
        receta(rec, c)


def receta(receta, c): #Los parametros proporcionados son el cursor de la bbdd y la receta seleccionada en la pantalla
    c.execute('SELECT ingredientes FROM recetas WHERE nombre = ?', receta) #Buscamos los ingredientes que pertenecen a la receta que hemos seleccionado
    ingReceta = c.fetchall()
    c = 1
    nextion.write(("t0.txt=\"" + receta + "\"").encode) #Cambiamos el título para que aparezca el nombre de la receta
    for i in ingReceta:
        nextion.write(("t" + str(c) + ".txt=\"" + i + "\"").encode) #Cambiamos el nombre de los ingredientes para que aparezcan los ingredientes de la receta
        c = c+1

def send_command(self, command):
    self.serial.write(command.encode())

def change_page(self, page_name):
    command = 'page ' + page_name + '\n'
    self.send_command(command)

def home_view(self):
    while True:
        event = self.serial.readline().decode().strip()

        if event.startswith('click btn_page1'):
            self.change_page('1')
        elif event.startswith('click btn_page2'):
            self.change_page('2')
        elif event.startswith('click btn_page3'):
            self.change_page('3')

def find_nextion_port(): #Localizamos el puerto serial en el que está conectada la pantalla
    ports = serial.tools.list_ports.comports() #
    for port in ports:
        if 'Silicon' in port.description:
            return port.device
    return None
def parse_pagina(bytestream: bytes) -> str:
    if bytestream[0] == 102 and len(bytestream) == 5:
        return f"page {int(bytestream[1])}"
    else:
        return None

#nextion_port = find_nextion_port()
nextion_port = "/dev/ttyUSB0"
print(nextion_port)
# nextion = sr.Serial(nextion_port, 115200)
nextion = sr.Serial(nextion_port,9600)
nextion.timeout=2
main()