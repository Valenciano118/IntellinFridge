import logging
import sqlite3

import serial
from nextion import Nextion, EventType


class functionsNextion:

    def __init__(self):
        connect = sqlite3.connect('openfoods.sqlite')
        self.client = Nextion(r'\Device\USBPDO-0', 9600, self.event_handler)

    async def event_handler(self, type_, data):
        if type_ == EventType.STARTUP:
            print('We have booted up!')
        elif type_ == EventType.TOUCH:
            print('A button (id: %d) was touched on page %d' % (data.component_id, data.page_id))

        logging.info('Event %s data: %s', type, str(data))

    async def run(self):
        await self.client.connect()

        # await client.sleep()
        # await client.wakeup()

        # await client.command('sendxy=0')

        print(await self.client.get('sleep'))
        print(await self.client.get('field1.txt'))

    def mostrar_lista(self, init, fin, lista):
        if fin > len(lista)-1:
            fin = len(lista)-1
        for i in range(init, fin):
            await self.client.set('field'+str(i+1)+'.txt', lista[i])

    def ingredientes(self, connect, init, fin):
        c = connect.cursor()
        c.execute('SELECT nombre FROM nevera')
        ingLista = c.fetchall()
        self.mostrar_lista(init, fin, ingLista)


    def recetas(self, connect, init, fin):
        c = connect.cursor()
        c.execute('SELECT nombre FROM recetas')
        recLista = c.fetchall()
        self.mostrar_lista(init, fin, recLista)


    def receta(self, receta, connect):
        c = connect.cursor()
        c.execute('SELECT ingredientes FROM recetas WHERE nombre = ?', receta)
        ingReceta = c.fetchall()
        c = 0
        for i in ingReceta:
            await self.client.set('field' + str(c + 1) + '.txt', i) #Es c+1 porque el primer txt es el titulo del panel
            c = c+1