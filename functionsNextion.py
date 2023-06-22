
from dataclasses import dataclass
import sqlite3
import time

import serial as sr
import serial.tools.list_ports
import io
from ccd_read_usb0 import read_scanner
PATH = "/dev/input/by-id/usb-USB_Adapter_USB_Device-event-kbd"
def main():
    global connect
    global connect_nevera
    if not nextion.is_open: #Si la conexión no se ha realizado, iniciamos
        nextion.open()
    if nextion.is_open:
        print('Conexión serial establecida correctamente') #Comprobamos que la conexión serial se ha establecido
    else:
        print('Ha ocurrido un error al establecer la conexión serial')
    connect = sqlite3.connect('openfoods.sqlite')
    c = connect.cursor()
    connect_nevera = sqlite3.connect('nevera.db')
    n = connect_nevera.cursor()
    print('Iniciado')
    while True: #Iniciamos un bucle infinito que lea constantemente en que página de la interfaz nos encontramos
        estado = nextion.read(7)
        # print(f"{estado=}")
        estado = parse_estado(estado) 
        if not estado:
            # print('Esto no lee nada')
            continue
        # else:
            # print(f"{estado=}")
        if estado.touched == False:
            print(f"{estado=}")
            # Desde la pagina 0 se le da al boton de escanear
            if estado.page == 0 and estado.component_id==3: #Si el lenctor escanea un producto mientras estamos en la página 1 se añadirá a la base de datos
                nextion.write(b"page page1\xFF\xFF\xFF")
                print('Estas en la pagina 1')
                # codigo = input("Ingrese el código del producto: ")
                codigo = read_scanner(PATH)
                print(f"{codigo=}")
                c.execute('SELECT * FROM productos WHERE ean = ?', (codigo,)) #Comprobamos que el producto este en la base de datos de productos
                producto = c.fetchone()
                print(producto)
                if producto is not None:
                    n.execute('INSERT INTO nevera (ean, nombre, "fecha de caducidad") VALUES (?, ?, ?)', (int(producto[1]), producto[2], 0)) #Añadimos el producto a la nevera
                    connect_nevera.commit()
                    print("Producto insertado con exito")
                    nextion.write(b"page page0\xFF\xFF\xFF")
                else:
                    print("Error, el producto no existe")
                    nextion.write(b"page page0\xFF\xFF\xFF")

            # Desde la pagina 0 se le da al boton de la nevera
            if estado.page==0 and estado.component_id == 2: #En la página 2 tenemos la lista de ingredientes
                    nextion.write(b"page page2\xFF\xFF\xFF")
                    ingredients(n, 0, 4) #Explicación en la función

            # Desde la pagina 0 se le da al boton de las recetas
            if estado.page==0 and estado.component_id == 4: #En la página 3 tenemos la lista de recetas
                nextion.write(b"page page3\xFF\xFF\xFF")
                recetas(n, 0, 4) #Explicación en la función

        time.sleep(0.001) #Para evitar saturación


@dataclass
class State:
    page: int
    component_id: int
    touched: bool

def _write_ingredients(number_of_text_boxes:int, list_of_ingredients:list[str], first_ingredient:int ):
    if len(list_of_ingredients) == 0:
        return
    if first_ingredient >= len(list_of_ingredients) :
        return
    c = first_ingredient
    for i in range(1, number_of_text_boxes+1):
        message = f't{str(i)}.txt=""\xFF\xFF\xFF'
        nextion.write(bytes(message, encoding='iso-8859-1'))
        time.sleep(0.01)
    for i in range(1, number_of_text_boxes+1):
        print(i)
        if c >= len(list_of_ingredients):
            message = f't{str(i)}.txt=""\xFF\xFF\xFF'
            nextion.write(bytes(message, encoding='iso-8859-1'))
            time.sleep(0.01)
        else:
            message = f't{str(i)}.txt="{list_of_ingredients[c][0]}"\xFF\xFF\xFF'
            nextion.write(bytes(message, encoding='iso-8859-1'))
            time.sleep(0.01)
        c+=1
        # c = min(len(list_of_ingredients)-1, c+1)

def ingredients(c, init, fin): #Como parámetros damos el cursor de la bbdd, y dos ints que delimitan el rango de la lista de productos en la nevera
                                #que se va a mostrar en la pantalla
    c.execute('SELECT nombre,id FROM nevera') #Extraemos el nombre de todos los productos de la nevera
    ingLista = c.fetchall()
    # print(ingLista)

    if fin > len(ingLista)-1: #Si el fin del rango es mayor al tamaño de la lista, leeremos los últimos 5 productos
        fin = len(ingLista)-1
        init = fin - 4

    if init < 0: #Si el rango inicial es menor que 0, leeremos los 5 primeros productos
        init = 0
        fin = 4
    _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
    while True:
        estado = nextion.read(7)
        estado = parse_estado(estado)
        if not estado:
            continue
        if estado.touched== False:
            if estado.page == 2:
                match estado.component_id:
                    case 2: ## Volver a inicio
                        nextion.write(b"page page0\xFF\xFF\xFF")
                        break
                    case 9: ## Siguiente
                        init = min(init+5,len(ingLista))
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 8: ## Retroceso
                        init = max(init-5, 0)
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 3: ## Ingrediente 1
                        index = init
                        if index >= len(ingLista):
                            continue
                        nombre,id = ingLista[index]
                        init = detalles_ingredientes(nombre_ingrediente=nombre,id=id,c=c,init=init)
                        ingLista = c.fetchall()
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 4: ## Ingrediente 2
                        index = init +1
                        if index >= len(ingLista):
                            continue
                        nombre,id = ingLista[index]
                        init = detalles_ingredientes(nombre_ingrediente=nombre,id=id,c=c,init=init)
                        ingLista = c.fetchall()
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 5: ## Ingrediente 3
                        index = init +2 
                        if index >= len(ingLista):
                            continue
                        nombre,id = ingLista[index]
                        init = detalles_ingredientes(nombre_ingrediente=nombre,id=id,c=c,init=init)
                        ingLista = c.fetchall()
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 6: ## Ingrediente 4
                        index = init +4
                        if index >= len(ingLista):
                            continue
                        nombre,id = ingLista[index]
                        init = detalles_ingredientes(nombre_ingrediente=nombre,id=id,c=c,init=init)
                        ingLista = c.fetchall()
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case 7: ## Ingrediente 5
                        index = init +4
                        if index >= len(ingLista):
                            continue
                        nombre,id = ingLista[index]
                        init = detalles_ingredientes(nombre_ingrediente=nombre,id=id,c=c,init=init)
                        ingLista = c.fetchall()
                        _write_ingredients(number_of_text_boxes=5, list_of_ingredients=ingLista, first_ingredient=init)
                    case _:
                        continue
def detalles_ingredientes(nombre_ingrediente:str, id: int, c:sqlite3.Cursor, init:int ) -> int:
    nextion.write(b"page page5\xFF\xFF\xFF")
    message = f't0.txt="{nombre_ingrediente}"\xFF\xFF\xFF'
    nextion.write(bytes(message,encoding='iso-8859-1'))
    while True:
        estado = nextion.read(7)
        estado = parse_estado(estado)
        if not estado:
            continue
        if estado.touched== False:
            if estado.page == 5:
                match estado.component_id:
                    case 2: ## Eliminar
                        nextion.write(b"page page2\xFF\xFF\xFF")
                        time.sleep(0.01)
                        c.execute("DELETE FROM nevera WHERE id == ?",(id,))
                        connect_nevera.commit()
                        return init -1
                    case 3: ## Volver a la pagina 2 
                        nextion.write(b"page page2\xFF\xFF\xFF")
                        time.sleep(0.01)
                        return init
                    case _:
                        continue

    ## ID de borrar es 2 
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
    diff = fin - init #La cantidad de proingLista = c.fetchall()ductos que mostraremos
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
        event = self.serial.readline().decode('iso-8859-1').strip()

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
def parse_estado(bytestream: bytes) -> State:
    if  len(bytestream) == 7 and bytestream[0] == 101:
        page = int(bytestream[1])
        component_id = int(bytestream[2])
        touched = int(bytestream[3]) == 1

        return State(page=page,component_id=component_id,touched=touched)
    else:
        return None
if __name__ == '__main__':

    #nextion_port = find_nextion_port()
    nextion_port = "/dev/ttyUSB0"
    print(nextion_port)
    # nextion = sr.Serial(nextion_port, 115200)
    nextion = sr.Serial(nextion_port,9600)
    nextion.timeout=3600
    main()

