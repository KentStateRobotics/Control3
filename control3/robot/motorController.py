import struct
import time

#big edian 2 chars
motorStruct = struct.Struct("!cc")

class MotorController:
    """Controls a single motor

    Args:
        motorId (byte): single byte to identify this on the serial connection
        hasFeedback (bool, Optional): Does this motor have a pulse feedback
    """
    def __init__(self, motorId, hasFeedback=False):
        self.motorId = motorId
        self.hasFeedback = hasFeedback
        self.command = 0
        self.signed = signed
        self.deltaDisplacement = 0
        self.oldTime = 0
        self.position = 0 #Rad angle of device
        #TODO serial stuff to find corisponding motor
        #TODO register callback with serial stuff to receive motor feedback
    
    def getCommand(self):
        """Get last command to motor
        """
        return self.command

    def getPosition(self):
        """Returns absolute angle of motor's output
        """
        return self.position

    def getDeltaDisplacement(self):
        """Get time and difference in position from last time this was called
        Returns: 
            float, float: change in time, cumulative change in position sense last call 
        """
        deltaTime = time.time() - self.oldTime
        self.oldTime = time.time()
        return deltaTime, self.deltaDisplacement

    def _receiveFeedback(self, message):
        """Callback to receive feedback from motor controlers
        """
        pass
    
    def command(self, value):
        """Command the motor to move
        Args:
            value (int): [-1,1] value to command
        """
        if -1 > value or value > 1:
            raise ValueError("Motor command must be in the range [-1,1]. " + str(value) + " was given.")
            return
        self.command = value
        value = value * 127 + 127
        #TODO send motorStruct.pack(self.motorId, value))