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
                self.thread = threading.Thread(target = self.recieveMsg)

    def sendMsg(self, data):
        self.newConn.write(data)

    def recieveMsg(self):
        print("ready to receive")
        msgIn = self.newConn.read()
        fullMsg = ""
        if msgIn == self.START:
            length = self.newConn.read() - 48
            i = 0
            while i < length:
                fullMsg += msgIn
        print("received: ")
        print(fullMsg)


class msgContainer():
    def __init__(self):
        for p in serial.tools.list_ports.comports():
            if "Arduino" in p[1]:
                serialConn.serialConns.append(serialConn(p[0]))
                print(p[0])

    def queueMsg(self, message, length, dest):
        data = serialConn.START+ length + dest  + message
        print("finished message: " + data)
        #serialConn.msgToSend.append(data)
        for p in serialConn.serialConns:
            if p.getId() == dest:
                print("thet message: " + data + ", should have been sent")
                p.sendMsg(data)
