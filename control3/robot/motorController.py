import struct

#big edian 2 chars
motorStruct = struct.Struct("!cc")

class MotorController:
    """Controls a single motor

    Args:
        motorId (byte): single byte to identify this on the serial connection
        hasFeedback (bool, Optional): Does this motor have a pulse feedback
        signed (bool, Optional): Can this motor move backwards, will it accept negitive move commands
    """
    def __init__(self, motorId, hasFeedback=False, signed=True):
        self.motorId = motorId
        self.hasFeedback = hasFeedback
        self.command = 0
        self.signed = signed
        #TODO serial stuff to find corisponding motor
    
    def getCommand():
        return self.command
    
    def command(value):
        """Command the motor to move
        Args:
            value (int): [-1,1] if singed or [0,1] if unsinged. Sends a command.
        """
        if -1 > value or value > 1:
            raise ValueError("Motor command must be in the range [-1,1]. " + str(value) + " was given.")
        elif (not self.signed) and value < 0:
            raise ValueError("Unsinged motor command must be in the range [0,1]. " + str(value) + " was given.")
        self.command = value
        if self.signed:
            value = value * 127 + 127
        else:
            value = value * 255
        #TODO send motorStruct.pack(self.motorId, value))