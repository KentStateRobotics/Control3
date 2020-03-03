import serial
import serial.tools.list_ports
import threading

class serialConn():
    # this class is used to facilitate communication to arduino
    # the class has a static list of all instance of its self
    # the ID member variable of each class is used to identify which one it is connected to

    serialConns = []
    functionsToCall = []
    readyToSend = False
    START = '|'
    SECONDSTART = '~'

    def __init__(self, ports):
        # constructer of the serialConn class
        # iniltializes variables needed to connect to and ID connected arduinos
        # starts the findId function in new thread to recieve ID from arduino
        self.id = ""
        self.port = ports
        self.newConn = serial.Serial(port = self.port, baudrate = 115200, timeout = 1)
        self.thread = threading.Thread(target = self.findId)
        self.thread.start()

    def getId(self):
        # returns the ID for the instance of the object
        return self.id

    def findId(self):
        # this function runs in another thread to asynchonusly recive ID sent arduino
        # once the ID is recieved it sets the static varible readyToSend to true
        # allows seneding of messages since a connection has been established
        # also starts recieveMsg function in new thread when connection is established

        print("id pre:")
        while self.id == "":
            self.id = self.newConn.read()
            if self.id != "":
                print("recived id: ", self.id)
                self.thread = threading.Thread(target = self.recieveMsg)
                self.thread.start()
                serialConn.readyToSend = True

    def addFunction(self, func):
        self.functionsToCall.append(func())

    def removeFunction(self, func):
        for p in self.functionsToCall:
            if p == func:
                self.functionsToCall.remove(p)
            else:
                print("Function not in list")

    def callFunctions(self, argv):
        for p in self.functionsToCall:
            p(argv)


    def sendMsg(self, data):
        # takes the message that is passed to it and sends it over serial connection
        self.newConn.write(data)

    def recieveMsg(self):
        # this function runs in a new thread and will constantly listen to serial connection
        # when the start character is recived, it will then read the length
        # using length it will then read in length number of characters to get the message

        print("ready to receive")
        while True:
            msgIn = ""
            msgIn = (self.newConn.readline()).decode('utf-8')
            if msgIn != "":
                msgStart = msgIn.find(serialConn.SECONDSTART,0,len(msgIn)-1) + 1
                finMsg = msgIn[msgStart:len(msgIn)-1]
                self.callFunctions(finMsg)
                print("final recieved:", finMsg, '\n')


class msgContainer():
    # this class is used to handle the creation and message sending of the serialConn class

    connected = False
    def __init__(self):
        # this constuctor will check for connected arduinos
        # for each arduino connected it will create new instance of serialConn
        # every new instance will be added to the list of instances in serialConn

        for p in serial.tools.list_ports.comports():
            if "Arduino" in p[1]:
                self.connected = True
                serialConn.serialConns.append(serialConn(p[0]))
        if not self.connected:
            print("No ardunios connected")

    def addFunc(self, func):
        serialConn.functionsToCall.append(func)

    def queueMsg(self, message, dest):
        # this function will take a message and its target arduino
        # the instance of serialConn assigned to that arduino is found with its ID
        # this function will then pass the formatted message (START-length-msg) 
        #   to the correct instance of serialConn
        # will not send if no connection has been established or ID has not bee recieved
        
        if not self.connected:
            print("nothing connected")
            return
        else:
            while not serialConn.readyToSend:
                pass
            for p in serialConn.serialConns:
                if int(p.getId()) == dest:
                    p.sendMsg(serialConn.START.encode())
                    test = len(message)
                    test2 = str(test)
                    p.sendMsg(test2.encode())
                    p.sendMsg(serialConn.SECONDSTART.encode())
                    p.sendMsg(message.encode())
                    print("should have sent:", serialConn.START, len(message), message)