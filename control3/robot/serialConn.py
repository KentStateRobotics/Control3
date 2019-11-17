import serial
import serial.tools.list_ports
import threading

class serialConn():
    serialConns = []
    msgToSend = []
    START = '|'

    def __init__(self, ports):
        self.id = ""
        self.port = ports
        self.newConn = serial.Serial(port = self.port, baudrate = 115200)
        self.thread = threading.Thread(target = self.findId)
        #self.thread = threading.Thread(target = self.sendMsg)
        self.thread.start()

    def getId(self):
        return self.id

    def findId(self):
        print("id pre:")
        while self.id == "":
            self.id = self.newConn.read()
            if self.id != "":
                print("recived id")
                print(self.id)

    def sendMsg(self, data):
        self.newConn.write(data)


class msgContainer():
    def __init__(self):
        for p in serial.tools.list_ports.comports():
            if "Arduino" in p[1]:
                serialConn.serialConns.append(serialConn(p[0]))
                print(p[0])

    def queueMsg(self, message, length, dest):
        data = serialConn.START + dest + length + message
        print("finished message: " + data)
        #serialConn.msgToSend.append(data)
        for p in serialConn.serialConns:
            if p.getId() == dest:
                print("thet message: " + data + ", should have been sent")
                p.sendMsg(data)
