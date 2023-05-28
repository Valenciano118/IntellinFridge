import sqlite3

class functionsNextion:

    def __init__(self):
        connect = sqlite3.connect('openfoods.sqlite')
    def ingredientes(self, connect):
        c = connect.cursor()
        c.execute('SELECT nombre FROM nevera')
        ingLista = c.fetchall()


    def recetas(self, connect):
        c = connect.cursor()
        c.execute('SELECT nombre FROM recetas')
        recLista = c.fetchall()

    def receta(self, receta, connect):
        c = connect.cursor()
        c.execute('SELECT ingredientes FROM recetas WHERE nombre = ?', receta)
        ingReceta = c.fetchall()