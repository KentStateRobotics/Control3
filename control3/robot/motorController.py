import time
import struct

messageHeader = struct.Struct('<cc') #(motorId, messageId)
MESSAGES = {
    oMotorCommand: (0, struct.Struct('<cc')),  #output, Motor command (direction, value)
    oRequest: (1, struct.Struct('<c')), #output, Request value (otherMessageId)
    iDeltaPosition: (2, struct.Struct('<i')), #Delta position (deltaPosition)
    iAbsPosition: (3, struct.Struct('<H')) #Abs positon (position)
}

class MotorController:
    """Controls one or more motor controllers over a serial connection
    Can only receive feedback from one motor controller

    Args:
        serialDevice (int): id of the serial device 
        motorSerialConns (msgContainer): the serial connections to the motor controllers
        motorId (byte): single byte to identify this on the serial connection
    """
    def __init__(self, serialDeviceId, motorSerialConns, motorId):
        self.motorId = motorId
        self.motorSerialConns = motorSerialConns
        self.serialDeviceId = serialDeviceId
        self.command = 0
        self.postion = 0
        self.deltaPosition = 0
        self.posTime = time.time()
        self.deltaPosTime = time.time()
        self.lastDeltaPosTime = time.time()
        motorSerialConns.addFunct(self._receiveFeedback)
    
    def getCommand(self):
        """Get last command to motor
        """
        return self.command

    def queryPosition(self):
        """Sends message to serial device to request current position
        """
        msg = self.packMessage(MESSAGES.oRequest, MESSAGES.iPosition[0])
        self.motorSerialConns.queueMsg(msg, self.serialDeviceId)
        

    def queryDeltaPosition(self):
        """Sends message to serial device to request change in position sense last request
        """
        msg = self.packMessage(MESSAGES.oRequest, MESSAGES.iDeltaPosition[0])
        self.motorSerialConns.queueMsg(msg, self.serialDeviceId)

    def getPosition(self):
        """Returns (radians, time) 
            last absolute angle of motor's output and the time it was received
        """
        return self.position, self.posTime

    def getDeltaPosition(self):
        """Returns (radians, time) 
            last change in the angle of motor's output and the time it was received
        """
        return self.deltaPos, self.deltaPosTime

    def getVelocity(self):
        """Returns (radians/s) adv roational speed between last two queryDeltaPosition calls
        """
        return self.deltaPos / (self.deltaPosTime - self.lastDeltaPosTime)

    def _receiveFeedback(self, message):
        """Callback to receive feedback from motor controlers
        """
        if()
    
    def command(self, value):
        """Command the motor to move
        Args:
            value (int): [-1,1] value to command
        """
        if -1 > value or value > 1:
            raise ValueError("Motor command must be in the range [-1,1]. " + str(value) + " was given.")
            return
        self.command = value
        message = self.packMessage(MESSAGES.oMotorCommand, int(value < 0), abs(value) * 255)
        self.motorSerialConns.queueMsg(message, self.serialDeviceId)

    def packMessage(self, message, *args):
        return messageHeader.pack(self.motorId, message[0]) + message[1].pack(*args)
