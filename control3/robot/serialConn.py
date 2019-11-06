import serial
import serial.tools.list_ports
import threading
    

class serialConn():
    serialConns = []
    msgToSend = []
    START = '|'

    def _init_(self, port):
        self.id = ""
        self.port = port
        self.newConn = serial.Serial(port = self.port, baudrate = 115200)
        self.thread = threading.Thread(target = self.findId)
        self.thread = threading.Thread(target = self.sendMsg)
        self.thread.start()

    def findId(self):
        print("id pre:")
        while self.id == "":
            self.id = self.newConn.read()
            if self.id != "":
                print("recived id")
                print(self.id)

    def sendMsg(self, data):
        # runs in new thread and is constantly running
        # checks if the dest(arduinio id) is of the object
        # if same ID, will send to arduino and remove from the list
        
        while True:
            # needs to check if there is something in the messages queue 
            if self.msgToSend[0] != "": 
                if data[1] == self.id:
                    self.newConn.write(data)
                    self.msgToSend.pop(0)

    def queueMsg(self, message, length, dest):
        data = self.START + dest + length + message
        self.msgToSend.append(data)
