import time
import struct
from enum import Enum
import math


messageHeader = struct.Struct('<BB') #(motorId, messageId)
class MESSAGES(Enum):
    oMotorCommand = 0, struct.Struct('<BB')  #output, Motor command (direction, value)
    oRequest = 1, struct.Struct('<B') #output, Request value (otherMessageId)
    iDeltaPosition = 2, struct.Struct('<i') #Delta position (deltaPosition)
    iAbsPosition = 3, struct.Struct('<H') #Abs positon (position)

class MotorController:
    """Controls one or more motor controllers over a serial connection
    Can only receive feedback from one motor controller

    Args:
        serialDevice (int): id of the serial device 
        motorSerialConns (msgContainer): the serial connections to the motor controllers
        motorId (byte): single byte to identify this on the serial connection
    """
    def __init__(self, serialDeviceId, motorSerialConns, motorId):
        self._motorId = motorId
        self._motorSerialConns = motorSerialConns
        self._serialDeviceId = serialDeviceId
        self._command = 0
        self._position = 0
        self._deltaPosition = 0
        self._posTime = time.time()
        self._deltaPosTime = time.time()
        self._lastDeltaPosTime = time.time()
        self._motorSerialConns.addFunct(self._receiveFeedback)
    
    def getCommand(self):
        """Get last command to motor
        """
        return self._command

    def queryPosition(self):
        """Sends message to serial device to request current position
        """
        msg = self.packMessage(MESSAGES.oRequest, MESSAGES.iAbsPosition.value[0])
        self._motorSerialConns.queueMsg(msg, self._serialDeviceId)
        

    def queryDeltaPosition(self):
        """Sends message to serial device to request change in position sense last request
        """
        msg = self.packMessage(MESSAGES.oRequest, MESSAGES.iDeltaPosition.value[0])
        self._motorSerialConns.queueMsg(msg, self._serialDeviceId)

    def getPosition(self):
        """Returns (radians, time) 
            last absolute angle of motor's output and the time it was received
        """
        return self._position, self._posTime

    def getDeltaPosition(self):
        """Returns (radians, time) 
            last change in the angle of motor's output and the time it was received
        """
        return self._deltaPosition, self._deltaPosTime

    def getVelocity(self):
        """Returns (radians/s) adv roational speed between last two queryDeltaPosition calls
        """
        return self.deltaPos / (self._deltaPosTime - self._lastDeltaPosTime)

    def _receiveFeedback(self, message):
        """Callback to receive feedback from motor controlers
        """
        header = messageHeader.unpack_from(message)
        if(header[0] == self._motorId):
            if(header[1] == MESSAGES.iAbsPosition.value[0]):
                body = MESSAGES.iAbsPosition.value[1].unpack_from(message, messageHeader.size)
                self._position = body[0] / 10800 * math.pi
                self._posTime = time.time()
            elif(header[1] == MESSAGES.iDeltaPosition.value[0]):
                body = MESSAGES.iDeltaPosition.value[1].unpack_from(message, messageHeader.size)
                self._deltaPosition = body[0] / 10800 * math.pi
                self._deltaPosTime = time.time()


    
    def command(self, value):
        """Command the motor to move
        Args:
            value (int): [-1,1] value to command
        """
        if -1 > value or value > 1:
            raise ValueError("Motor command must be in the range [-1,1]. " + str(value) + " was given.")
            return
        self._command = value
        message = self.packMessage(MESSAGES.oMotorCommand, int(value < 0), int(abs(value) * 255))
        self._motorSerialConns.queueMsg(message, self._serialDeviceId)

    def packMessage(self, message, *args):
        return messageHeader.pack(self._motorId, message.value[0]) + message.value[1].pack(*args)
