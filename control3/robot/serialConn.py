import serial
import serial.tools.list_ports
import threading

class serialConn():
    serialConns = []
    msgToSend = []
    readyToSend = False
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
            self.id = int(self.newConn.read())
            if self.id != "":
                print("recived id: ", self.id)
                serialConn.readyToSend = True
                self.thread = threading.Thread(target = self.recieveMsg)
                self.thread.start()

    def sendMsg(self, data):
        self.newConn.write(data.encode())

    def recieveMsg(self):
        print("ready to receive")
        while True:
            self.fullMsg = ""
            self.msgIn = self.newConn.readline()
            print(self.msgIn)
            if self.msgIn == self.START:
                self.length = int(self.newConn.read())
                i = 0
                while i < self.length:
                    self.fullMsg += self.newConn.read().decode('utf-8')
                    i += 1
                print("received: ", self.fullMsg)
                break


class msgContainer():
    connected = False
    def __init__(self):
        for p in serial.tools.list_ports.comports():
            if "Arduino" in p[1]:
                self.connected = True
                serialConn.serialConns.append(serialConn(p[0]))
        if not self.connected:
            print("No ardunios connected")

    def queueMsg(self, message, length, dest):
        if not self.connected:
            return
        else:
            while not serialConn.readyToSend:
                pass
            data = serialConn.START.decode('utf-8') + length + message
            print("finished message: " + data)
            for p in serialConn.serialConns:
                if p.getId() == dest:
                    print("that message: " + data + ", should have been sent")
                    p.sendMsg(data)
