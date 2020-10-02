'''
message
KentStateRobotics Jared Butcher 7/26/2019
Message Types:
    Struct Types:
        Format  C-Type              Python-Type     Size
        x       pad byte            NA              1
        c       char                bytes           1
        b       signed char         int             1
        B       unsigned char       int             1
        ?       bool                bool            1
        h       short               int             2
        H       unsigned short      int             2
        i       int                 int             4
        I       unsigned int        int             4
        l       long                int             4
        L       unsigned long       int             4
        q       long long           int             8
        Q       unsigned long long  int             8
        e       half                float           2
        f       float               float           4
        d       double              float           8
        s       char[]              bytes           Fixed size n used as "ns"
        p       char[]              bytes           <= 255 Pascal string sized n used as "np"
    Variable Length Types:
        blob    char[]              bytes           variable
'''
import struct
from collections import UserDict
from enum import Enum
import json

class MessageFactory:
    '''Used to define messages that can be converted to and from bytes for exchange

    messageDefinition - a dicitonary of keys and data types or other MessageFactories
    '''

    '''Standared Message Header is automaticly added to the top level of all Messages
    '''
    _Header = None

    def __init__(self, messageDefinition, includeHeader=True):
        self.definition = messageDefinition
        self.structFormat = "!"
        self.includeHeader = includeHeader
        self.structKeys = []
        self.messageKeys = []
        self.blobKeys = []
        for key,value in messageDefinition.items():
            if type(value) is str:
                if value == "blob":
                    self.blobKeys.append(key)
                else:
                    self.structKeys.append(key)
                    self.structFormat += value
            else:
                self.messageKeys.append(key)
        self.struct = struct.Struct(self.structFormat)
        self.dictFormat = self._createDict()

    def pack(self, values, topLevel=True):
        '''Returns bytes of the dictionary values packed according to this Messages definition

        topLevel - if True include a header
        '''
        topLevel = topLevel and self.includeHeader
        structValues = []
        data = bytes()
        if topLevel:
            data += b's' #Mark as struct as opposed to json
            data += MessageFactory._Header.pack(values['header'], topLevel=False)
        for key in self.structKeys:
            structValues.append(values[key])
        try:
            data += self.struct.pack(*structValues)
        except struct.error as e:
            print("Error occured while packing: " + str(structValues))
            print("Into: " + str(self.definition))
            raise e
        for key in self.messageKeys:
            data += self.definition[key].pack(values[key], topLevel=False)
        for key in self.blobKeys:
            data += len(values[key]).to_bytes(4, "big")
            if type(values[key]) == str:
                data += values[key].encode()
            else:
                data += values[key]
        return data

    def unpack(self, data, topLevel=True):
        '''Unpacks the bytes into a dictionary according to this Messages definition.
        Returns dictionary of unpacked values, remaining bytes

        data - bytes to unpack

        topLevel - does this level have a header
        '''
        topLevel = topLevel and self.includeHeader
        outDict = self._createDict(topLevel=topLevel)
        if topLevel:
            outDict['header'], data = MessageFactory._Header.unpack(data[1:], topLevel=False)
        structValues = self.struct.unpack_from(data)
        for i in range(len(structValues)):
            outDict[self.structKeys[i]] = structValues[i]
        data = data[self.struct.size:]
        for key in self.messageKeys:
            outDict[key], data = self.definition[key].unpack(data, topLevel=False)
        for key in self.blobKeys:
            size = int.from_bytes(data[:4], "big")
            data = data[4:]
            outDict[key] = data[:size]
            data = data[size:]
        return outDict, data

    def _createDict(self, topLevel=True):
        '''Internal function to generate an empty format dictionary
        '''
        topLevel = topLevel and self.includeHeader
        outDict = {}
        for key,value in self.definition.items():
            if type(value) is str:
                outDict[key] = None
            else:
                outDict[key] = value._createDict(topLevel=False)
        if topLevel:
            outDict['header'] = MessageFactory._Header._createDict(topLevel=False)
        return outDict

    def getFormat(self):
        '''Returns a copy of this Factory's format dictionary. To be filled and packed.
        '''
        return self.dictFormat.copy()

    def createMessage(self, initalValues=None):
        '''Returns an empty Message to be filled
        '''
        if initalValues is None:
            return Message(self, self.getFormat())
        else:
            return Message(self, initalValues)

    def loads(self, data):
        if data[0] == ord('s'):
            return Message(self, self.unpack(data)[0])
        elif data[0] == '{':
            return Message(self, json.loads(data))
        else:
            print("Failed to load message data")

class Message(UserDict):
    def __init__(self, factory, initalValues):
        super().__init__(initalValues)
        self._factory = factory

    def toStruct(self):
        return self._factory.pack(self)

    def toJson(self):
        print(self.data)
        return json.dumps(self.data, cls=JSONBytesEncoder)

    @staticmethod
    def peekHeader(data):
        '''Static function that removes and unpacks a messages header
        '''
        return MessageFactory._Header.loads(data)

    def getFormat(self):
        '''Returns a copy of this Messages format dictionary. To be filled and packed.
        '''
        return self._factory.getFormat()

class JSONBytesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return json.JSONEncoder.default(self, obj)

MessageFactory._Header = MessageFactory({
    'timestamp': 'f',
    'source': 'B',
    'channel': 'B',
    'type': 'B'
}, includeHeader=False)