#!/usr/bin/python2
# -*- coding: utf-8 -*-

import time
import sys
import sqlite3 as bd
from datetime import date, timedelta
import os

# import de matplotib
import matplotlib
matplotlib.use('Agg')  # para poder guardar el grafico como imagen
import numpy as np
import matplotlib.pyplot as plt
from pylab import *  # para que funcione xticks


reload(sys)
sys.setdefaultencoding("utf-8")

# -------- En la primera parte obtenemos la temperatura y humedad de los sensores.------------#
print 'Entramos en la primera parte... y empezamos'

# Obtiene temperatura y humedad de los sensor
try:
    def get_temp_sens1():
        tfile = open("/sys/bus/w1/devices/28-0116281195ee/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature1 = temperature / 1000
        temb = str(temperature1)
        return temb
    
    
    def get_temp_sens2():
        tfile = open("/sys/bus/w1/devices/28-0116286044ee/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature2 = temperature / 1000
        tem = (str(temperature2))
        return tem
    
    
    print(str(get_temp_sens1()))
    print(str(get_temp_sens2()))
except:
    print('fallo')

temp_int = get_temp_sens1()
temp_ext = get_temp_sens2()

# ---------------En la segunda parte guarda los valores en la base de datos.-------------#

# Obtenemos fecha
fecha = str(date.today())

# Obtener hora
hora = str(time.strftime('%H'))

# Obtenemos fecha de ayer
ayer = str(date.today() - timedelta(days=1))
print 'Obtenemos las variables relativas a timedata:'
print 'fecha: ' + str(fecha) + ' hora: ' + str(hora) + 'fecha de ayer: ' + str(ayer)

# Conectamos  a la base de datos y abrimos el cursor para trabajar con ella
conexion_bd = bd.connect('/home/pi/python/grafico_temperatura/base_temp.sql')
cursor = conexion_bd.cursor()

# Crea los elementos que tendra la tabla
tabla = """
            CREATE TABLE IF NOT EXISTS temperatura(
            fecha DATE NOT NULL,
            hora TIME NOT NULL,
            temp_int FLOAT NOT NULL,
            temp_ext FLOAT NOT NULL)
                    """

cursor.execute(tabla)

# Crea el orden de los datos que se introduciran
datos = (fecha, hora, temp_int, temp_ext)

# Guarda los datos en la correspondiente celda de la tabla
tabla = """
    INSERT INTO temperatura (fecha, hora, temp_int, temp_ext)
    VALUES (?, ?, ?, ?)
    """



cursor.execute(tabla, datos)

# Cierra la bd, la tabla y el cursor
cursor.close()
conexion_bd.commit()
conexion_bd.close()

print 'Se han añadido los valores a la base de datos'
print

# --------- la tercera parte crea la grafica y el informe ----------#

# Si son las 00 ejecuta el script que crea el grafico y el informe del dia
if hora == '00':
    print 'Comienza a generar el grafico y el informe'
    # Conecta con la base de datos
    conexion_bd = bd.connect('/home/pi/python/grafico_temperatura/base_temp.sql')
    
    # Abrimos el cursor para trabajar con la B.D.
    cursor = conexion_bd.cursor()
    
    # Trabaja con la tabla temperatura
    tabla = "SELECT * FROM temperatura"
    
    # Crea las listas horas y temperaturas
    horas = []
    temperatura_i = []
    temperatura_e = []
    todas_horas = []
    
    # Recorre la tabla y si la celda primera "line[0]", que es la fecha,
    # coincide con la de ayer añade el valor a la lista correspondiente
    # y asi se crean las listas con los datos que haran la grafica
    # Se recorren todas celdas horas del 0 al 23, si alguna hora no esta,
    # entra en el except y no añade nada a la lista
    if cursor.execute(tabla):
        filas = cursor.fetchall()
        try:
            for fila in filas:
                for i in range(0, 24):
                    if fila[1] == i and fila[0] == ayer:
                        horas.append(fila[1])
                        temperatura_i.append(fila[2])
                        temperatura_e.append(fila[3])
        except:
            pass
        print 'Listas de datos creada con exito'
    
    # Abre el archivo informe.txt, escribe la tablas con los nombres de los contenidos, cierra informe
    informe = open('/home/pi/python/grafico_temperatura/informe.txt', 'w')
    informe.write(str(ayer) + '\n' + '\n' + "hora" + '     ' + 'Int' + '          ' + 'ext' + '\n')
    informe.close()
    if cursor.execute(tabla):
        filas = cursor.fetchall()
        for fila in filas:
            informe = open('/home/pi/python/grafico_temperatura/informe.txt', 'a')
            if fila[0] == ayer:
                if fila[1] < 10:
                    todas_horas.append(fila[1])
                    informe.write(str(fila[1]) + '        ' + str(fila[2]) + '         ' + str(fila[3]) + '\n')
                    informe.close()
                else:
                    todas_horas.append(fila[1])
                    informe.write(str(fila[1]) + '       ' + str(fila[2]) + '         ' + str(fila[3]) + '\n')
                    informe.close()
        print 'Informe generado con exito'
    
    cursor.close()
    conexion_bd.commit()
    conexion_bd.close()
    
    print 'Lista de las horas: ' + str(horas)
    print 'Lista de temperatura interior' + str(temperatura_i)
    print 'Lista de temperatura exterior' + str(temperatura_e)
    print 'Lista con todas las horas' + str(todas_horas)
    time.sleep(3)
    
    # Hacemos la grafica
    x = np.array(horas)  # Definimos en el eje x las horas
    y = np.array(temperatura_i)  # Definimos en el eje y la temperatura interior
    o = np.array(temperatura_e)  # Definimos en el eje y la temperatura exterior
    
    maxi = max(temperatura_e)
    mini = min(temperatura_e)
    
    plt.xlim(0, 24)  # Los valores del eje y variarán entre 0 y 25 (horas)
    plt.ylim(0, 50)  # Los valores del eje y variarán entre 0 y 50 (grados)
    
    plt.xticks(2 * arange(13))  # Definimos el eje x del 1 al 25 en intervalos de 2
    plt.yticks(2 * arange(22))  # Definimos el eje y del 0 al 43 en intervalos de 2
    
    plt.grid()  # Rejilla de grafico
    plt.xlabel('Hora', size=25)  # Ponemos etiqueta al eje x
    plt.ylabel(u'Grados', size=25)  # Ponemos etiqueta al eje y
    plt.title(ayer + '\n' + str(maxi) + ' Maximo' + '  <---------->  ' + str(mini) + ' Minimo', size=12)
    
    # quitamos las lineas de arriba y derecha del grafico
    ax = plt.axes()
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.plot(x, y, label="Temperatura interior", linewidth=1, color='blue')  # Creamos el grafico interior
    plt.plot(x, o, label="Temperatura exterior", linewidth=1, color='red')  # Creamos el grafico exterior
    fig = matplotlib.pyplot.gcf()
    plt.legend()
    
    plt.savefig('/home/pi/python/grafico_temperatura/grafico.png', dpi=125)  # Guardamos el grafico en png
    
    print 'grafico creado con exito'
    
    informe = open('/home/pi/python/grafico_temperatura/informe.txt', 'a')
    informe.write('La temperatura maxima ha sido ' + str(maxi) + '\n' +
                  'Temperatura minima ha sido de ' + str(mini))
    informe.close()
    
    # Movemos el informe y la grafica a su carpeta correspondiente
    os.system('sudo mkdir  /home/pi/python/grafico_temperatura/imforme_y_grafico/' + str(ayer))
    print 'Movemos?'
    
    os.system('sudo mv /home/pi/python/grafico_temperatura/informe.txt' + ' ' +
              '/home/pi/python/grafico_temperatura/imforme_y_grafico/' + str(ayer) + '/' + 'informe_del__' + str(
                 ayer) + '.txt')
    print 'ya'
    os.system('sudo mv /home/pi/python/grafico_temperatura/grafico.png' + ' ' +
              '/home/pi/python/grafico_temperatura/imforme_y_grafico/' + str(ayer) + '/'
              + 'grafico_del__' + str(ayer) + '.png')
    
    print 'Grafico e informe movido a su carpeta'
    
else:
    print 'No son las 00 horas'
