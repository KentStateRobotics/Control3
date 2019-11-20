import serial
import serial.tools.list_ports
import threading

class serialConn():
    serialConns = []
    msgToSend = []
    START = b'|'

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
                #print(self.id)
                self.thread = threading.Thread(target = self.recieveMsg)
                self.thread.start()

    def sendMsg(self, data):
        self.newConn.write(data)

    def recieveMsg(self):
        print("ready to receive")
        while True:
            self.fullMsg = ""
            self.msgIn = self.newConn.read()
            if self.msgIn == self.START:
                self.length = int(self.newConn.read())
                i = 0
                while i < self.length:
                    self.fullMsg += str(self.newConn.read())
                    i += 1
                print("received: " + self.fullMsg)
                break


class msgContainer():
    connected = False
    def __init__(self):
        for p in serial.tools.list_ports.comports():
            if "Arduino" in p[1]:
                self.connected = True
                serialConn.serialConns.append(serialConn(p[0]))

    def queueMsg(self, message, length, dest):
        if not self.connected:
            print("No arduinos connected")
            return
        data = serialConn.START + length + dest  + message
        print("finished message: " + data)
        for p in serialConn.serialConns:
            if p.getId() == dest:
                print("thet message: " + data + ", should have been sent")
                p.sendMsg(data)
