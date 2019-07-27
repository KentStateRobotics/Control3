import context
from networking.message import Message
import unittest
from unittest import mock

class TestPadString(unittest.TestCase):
    
    def test_Empty(self):
        self.assertEqual(Message.padString('', 3), b'\x00\x00\x00')

    def test_Short(self):
        self.assertEqual(Message.padString('hi', 3), b'hi\x00')

    def test_Pre(self):
        self.assertEqual(Message.padString('\x00i', 3), b'\x00i\x00')
    
    def test_Long(self):
        self.assertEqual(Message.padString('hello', 3), b'hel')

    def test_Bytes(self):
        self.assertEqual(Message.padString(b'i', 3), b'i\x00\x00')

class TestMessage(unittest.TestCase):
    def setUp(self):
        self.testMsg = Message({
            'num': 'i',
            'blob': 'blob'
        })
        self.testNestedMsg = Message({
            'num': 'i',
            'test': self.testMsg
        })
        self.headerFormat = {
                'timestamp': None,
                'source': None,
                'topic': None,
                'messageType': None,
                'sequence': None
            }

    def test_headerForm(self):
        self.assertEqual(self.headerFormat, Message.Header._createDict(False))

    def test_form(self):
        correctFormat = {
            'header': self.headerFormat,
            'num': None,
            'blob': None
        }
        self.assertEqual(self.testMsg.getFormat(), correctFormat)

    def test_nestedForm(self):
        correctFormat = {
            'header': self.headerFormat,
            'num': None,
            'test': {
                'num': None,
                'blob': None
            }
        }
        self.assertEqual(self.testNestedMsg.getFormat(), correctFormat)

    def test_structPack(self):
        structMsg = Message({
            'int': 'i',
            'double': 'd',
            'chars': '5s'
        })
        msg = structMsg.getFormat()
        msg['int'] = 5
        msg['double'] = 32322342425.5
        msg['chars'] = Message.padString("hi", 5)
        msg['header']['source'] = Message.padString("source", Message.NAME_LENGTH)
        msg['header']['topic'] = Message.padString("topic", Message.NAME_LENGTH)
        msg['header']['timestamp'] = 703452.5
        msg['header']['sequence'] = 53
        msg['header']['messageType'] = Message.MessageType.update.value
        data = structMsg.pack(msg)
        unpackedData = structMsg.unpack(data)[0]
        self.assertEqual(msg, unpackedData)

    def test_blob(self):
        structMsg = Message({
            'int': 'i',
            'blob': 'blob'
        })
        msg = structMsg.getFormat()
        msg['int'] = 543
        msg['blob'] = b'A rather not too short message or something'
        msg['header']['source'] = Message.padString("source", Message.NAME_LENGTH)
        msg['header']['topic'] = Message.padString("topic", Message.NAME_LENGTH)
        msg['header']['timestamp'] = 703452.5
        msg['header']['sequence'] = 53
        msg['header']['messageType'] = Message.MessageType.update.value
        data = structMsg.pack(msg)
        unpackedData = structMsg.unpack(data)[0]
        self.assertEqual(msg, unpackedData)


if __name__ == '__main__':
    unittest.main()