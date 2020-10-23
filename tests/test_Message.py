from KSRCore.message import MessageFactory, Message
import pytest
from unittest import mock

@pytest.fixture(scope='module')
def testMessageFactory():
    messages = {
        'testMsg': MessageFactory({
            'num': 'i',
            'blob': 'blob'
        }),
        'headerFormat': {
            'source': None,
            'destination': None,
            'channel': None,
            'type': None
        }
    }
    messages['testNestedMsg'] = MessageFactory({
            'num': 'i',
            'test': messages['testMsg']
        })
    return messages

@pytest.fixture(scope='module')
def testMessages():
    messages = {
        'testMsg': MessageFactory({
            'num': 'i',
            'blob': 'blob'
        }),
        'headerFormat': {
            'source': None,
            'destination': None,
            'channel': None,
            'type': None
        }
    }
    messages['testNestedMsg'] = MessageFactory({
            'num': 'i',
            'test': messages['testMsg']
        })
    messages['headerMsg'] = MessageFactory({})
    messages['filledHeader'] = messages['headerMsg'].createMessage({
        'header':{
            'source': 0x73,
            'destination': 0xab,
            'channel': 0x66,
            'type': 0x89
        }
    })
    messages['filledTestMsg'] = messages['testMsg'].createMessage({
        'header':{
            'source': 0x73,
            'destination': 0xab,
            'channel': 0x99,
            'type': 0xa1,
        },
        'num': 456,
        'blob': b'This is a blob'
    })
    return messages

def test_messageFactory_headerForm(testMessageFactory):
    assert testMessageFactory['headerFormat'] == MessageFactory._Header._createDict(False)

def test_messageFactory_form(testMessageFactory):
    correctFormat = {
        'header': testMessageFactory['headerFormat'],
        'num': None,
        'blob': None
    }
    assert testMessageFactory['testMsg'].getFormat() == correctFormat

def test_messageFactory_nestedForm(testMessageFactory):
    correctFormat = {
        'header': testMessageFactory['headerFormat'],
        'num': None,
        'test': {
            'num': None,
            'blob': None
        }
    }
    testMessageFactory['testNestedMsg'].getFormat() == correctFormat

def test_messageFactory_structPack(testMessageFactory):
    structMsg = MessageFactory({
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
    msg['header']['source'] = 0x73
    msg['header']['destination'] = 0xcd
    msg['header']['channel'] = 0x74
    msg['header']['type'] = 0x73
    data = structMsg._pack(msg)
    unpackedData = structMsg._unpack(data[1:])[0]
    assert msg == unpackedData

def test_messageFactory_blob(testMessageFactory):
    structMsg = MessageFactory({
        'int': 'i',
        'blob': 'blob'
    })
    msg = structMsg.getFormat()
    msg['int'] = 543
    msg['blob'] = str.encode('A rather not too short message or something')
    msg['header']['source'] = 0x73
    msg['header']['destination'] = 0xcd
    msg['header']['channel'] = 0x74
    msg['header']['type'] = 0x73
    data = structMsg._pack(msg)
    unpackedData = structMsg._unpack(data[1:])[0]
    assert msg == unpackedData

def test_message_Struct(testMessages):
    data = testMessages['filledHeader'].toStruct()
    header = testMessages['headerMsg'].loads(data)
    assert header == testMessages['filledHeader']

def test_message_JSON(testMessages):
    data = testMessages['filledHeader'].toJson()
    header = testMessages['headerMsg'].loads(data)
    assert header == testMessages['filledHeader']

def test_message_JSON_nested(testMessages):
    msg = testMessages['testNestedMsg'].createMessage()
    msg['header'] = testMessages['filledHeader']['header']
    msg['num'] = 435
    msg['test'] = testMessages['testMsg'].createMessage({
        'num': 987876,
        'blob': 'This is a string entry'
    })
    data = msg.toJson()
    msg2 = testMessages['testNestedMsg'].loads(data)
    assert msg == msg2

def test_message_struct_nested(testMessages):
    msg = testMessages['testNestedMsg'].createMessage()
    msg['header'] = testMessages['filledHeader']['header']
    msg['num'] = 435
    msg['test'] = testMessages['testMsg'].createMessage({
        'num': 987876,
        'blob': b'This is a string entry'
    })
    data = msg.toStruct()
    msg2 = testMessages['testNestedMsg'].loads(data)
    assert msg == msg2

def test_peek_header_struct(testMessages):
    data = testMessages['filledTestMsg'].toStruct()
    assert Message.peekHeader(data) == testMessages['filledTestMsg']['header']

def test_peek_header_JSON(testMessages):
    data = testMessages['filledTestMsg'].toJson()
    assert Message.peekHeader(data) == testMessages['filledTestMsg']['header']
    
def test_p_string():
    testMsgFact = MessageFactory({'a': '255p', 'c': 'i', 'b': '16p'})
    testInst = testMsgFact.createMessage({'a': b'This is a string', 'c': 56, 'b': b'bytes'})
    testInst.setHeader(0,0,0,0)
    data = testInst.toStruct()
    recovered = testMsgFact.loads(data)
    assert recovered['a'] == b"This is a string"
    assert recovered['b'] == b'bytes'
    assert recovered['c'] == 56

def test_message_setSource(testMessages):
    msg = testMessages['filledTestMsg']
    data = msg.toStruct()
    data = Message.setSource(data, 0x11)
    out = testMessages['testMsg'].loads(data)
    assert out['header']['destination'] == msg['header']['destination']
    assert out['header']['source'] == 0x11
    data = msg.toJson()
    data = Message.setSource(data, 0x12)
    out = testMessages['testMsg'].loads(data)
    assert out['header']['destination'] == msg['header']['destination']
    assert out['header']['source'] == 0x12