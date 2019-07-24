import context
from networking import message
import unittest
from unittest import mock



class TestPadString(unittest.TestCase):
    
    def test_Empty(self):
        self.assertEqual(message.padString('', 3), b'\x00\x00\x00')

    def test_Short(self):
        self.assertEqual(message.padString('hi', 3), b'hi\x00')

    def test_Pre(self):
        self.assertEqual(message.padString('\x00i', 3), b'\x00i\x00')
    
    def test_Long(self):
        self.assertEqual(message.padString('hello', 3), b'hel')

class TestMessage(unittest.TestCase):
    def setUp(self):
        self.testMsg = message.Message({
            'num': 'i',
            'blob': 'blob'
        })
        self.testNestedMsg = message.Message({
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
        self.assertEqual(self.headerFormat, message.Header._createDict(False))

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
        structMsg = message.Message({
            'int': 'i',
            'double': 'd',
            'chars': '5s'
        })
        msg = structMsg.getFormat()
        msg['int'] = 5
        msg['double'] = 32322342425.5
        msg['chars'] = message.padString("hi", 5)
        msg['header']['source'] = message.padString("source", message.NAME_LENGTH)
        msg['header']['topic'] = message.padString("topic", message.NAME_LENGTH)
        msg['header']['timestamp'] = 703452.5
        msg['header']['sequence'] = 53
        msg['header']['messageType'] = message.MessageType.update.value
        data = structMsg.pack(msg)
        unpackedData = structMsg.unpack(data)[0]
        self.assertEqual(msg, unpackedData)


if __name__ == '__main__':
    unittest.main()