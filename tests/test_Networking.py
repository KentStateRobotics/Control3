import pytest
import time
from unittest.mock import Mock
import KSRCore.networking as networking
import KSRCore.message as message

@pytest.fixture(scope='function')
def createMessages():
    msgFact = message.MessageFactory({
            'num': 'i',
            'blob': 'blob'
        })
    msgFilled = msgFact.createMessage({
        'header':{
            'source': 0x73,
            'destination': 0x00,
            'channel': 0x69,
            'type': 0xa1,
        },
        'num': 456,
        'blob': b'This is a blob'
    })
    return {'factory': msgFact, 'message': msgFilled}

def test_server_start():
    server = networking.Server(6969)
    time.sleep(.3)
    assert server.stop()

def test_base_add_remove_handler():
    server = networking.Server(6968)
    server.addHandler(0x45, Mock())
    assert 0x45 in server._handlers
    server.addHandler(0x55, Mock())
    server.removeHandlers(0x45)
    assert 0x45 not in server._handlers
    assert 0x55 in server._handlers
    server.removeHandlers()
    assert 0x55 not in server._handlers
    server.stop()

def test_base_route(createMessages):
    server = networking.Server(6970)
    mock1 = Mock()
    mock2 = Mock()
    mock3 = Mock()
    server.addHandler(0x69, mock1)
    server.addHandler(0x42, mock2)
    server.addHandler(0xa3, mock3)
    server.put(createMessages['message'].toStruct())
    createMessages['message']['header']['channel'] = 0xa3
    server.put(createMessages['message'].toJson())
    time.sleep(.2)
    server.stop()
    mock1.assert_called_once()
    mock2.assert_not_called()
    mock3.assert_called_once()

def test_router_unhandled(createMessages):
    server = networking.Server(6971)
    server.put(createMessages['message'].toStruct())
    time.sleep(.1)
    server.stop()

def test_send(createMessages):
    client = networking.Client(('localhost', 4567))
    server = networking.Server(4567)
    mock1 = Mock()
    server.addHandler(0x69, mock1)
    createMessages['message']['header']['destination'] = 1
    client.put(createMessages['message'].toStruct())
    time.sleep(.2)
    client.stop()
    server.stop()
    mock1.assert_called_once()
    