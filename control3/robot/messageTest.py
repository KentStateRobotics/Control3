import serialConn
import serial
import serial.tools.list_ports
import threading

def start ():
    for p in serial.tools.list_ports.comports():
        if "Arduino" in p[1]:
            #serialConn.serialConns.append(serialConn(p[0]))
            print(p[0])
start()