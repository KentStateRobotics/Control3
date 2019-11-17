from serialConn import *
import serial
import serial.tools.list_ports
import threading

testMsg = msgContainer()
testMsg.__init__
testMsg.queueMsg("testPy", "6", "1")