from KSRCore.message import Message
import pytest
from unittest import mock

@pytest.fixture(scope='module')
def testMessages():
    messages = {
        'testMsg': Message({
            'num': 'i',
            'blob': 'blob'
        }),
        'headerFormat': {
            'timestamp': None,
            'source': None,
            'destination': None,
            'messageType': None
        }
    }
    messages['testNestedMsg'] = Message({
            'num': 'i',
            'test': messages['testMsg']
        })
    return messages

def test_message_headerForm(testMessages):
    assert testMessages['headerFormat'] == Message.Header._createDict(False)

def test_message_form(testMessages):
    correctFormat = {
        'header': testMessages['headerFormat'],
        'num': None,
        'blob': None
    }
    assert testMessages['testMsg'].getFormat() == correctFormat

def test_message_nestedForm(testMessages):
    correctFormat = {
        'header': testMessages['headerFormat'],
        'num': None,
        'test': {
            'num': None,
            'blob': None
        }
    }
    testMessages['testNestedMsg'].getFormat() == correctFormat

def test_message_structPack(testMessages):
    structMsg = Message({
        'int': 'i',
        'double': 'd',
        'chars': '5s',
        'pascal': '50p'
    })
    msg = structMsg.getFormat()
    msg['int'] = 5
    msg['double'] = 32322342425.5
    msg['chars'] = b'there'
    msg['pascal'] = b'VarLength string'
    msg['header']['source'] = b'sc'
    msg['header']['destination'] = b'dc'
    msg['header']['timestamp'] = 703452.5
    msg['header']['messageType'] = b'c'
    data = structMsg.pack(msg)
    unpackedData = structMsg.unpack(data)[0]
    assert msg == unpackedData

def test_message_blob(testMessages):
    structMsg = Message({
        'int': 'i',
        'blob': 'blob'
    })
    msg = structMsg.getFormat()
    msg['int'] = 543
    msg['blob'] = str.encode('A rather not too short message or something')
    msg['header']['source'] = b'sc'
    msg['header']['destination'] = b'dc'
    msg['header']['timestamp'] = 703452.5
    msg['header']['messageType'] = b'c'
    data = structMsg.pack(msg)
    unpackedData = structMsg.unpack(data)[0]
    assert msg == unpackedData
