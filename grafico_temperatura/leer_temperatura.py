# -*- coding: utf-8 -*-

def get_temp_sens1():
    tfile = open("/sys/bus/w1/devices/28-0116281195ee/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature1 = temperature / 1000
    temb = str(temperature1) + '  Sensor1'
    return temb


def get_temp_sens2():
    tfile = open("/sys/bus/w1/devices/28-0116286044ee/w1_slave")
    text = tfile.read()
    tfile.close()
    secondline = text.split("\n")[1]
    temperaturedata = secondline.split(" ")[9]
    temperature = float(temperaturedata[2:])
    temperature2 = temperature / 1000
    tem = (str(temperature2) + '  Sensor2')
    return tem
print(str(get_temp_sens1()))
print(str(get_temp_sens2()))
