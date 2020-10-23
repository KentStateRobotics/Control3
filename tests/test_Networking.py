import pytest
import time
from unittest.mock import Mock
import KSRCore.networking as networking
import KSRCore.message as message
import tests

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
    time.sleep(.1)
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
    assert tests.wait(lambda: mock1.called)
    assert tests.wait(lambda: mock3.called)
    server.stop()
    mock2.assert_not_called()

def test_router_unhandled(createMessages):
    server = networking.Server(6971)
    server.put(createMessages['message'].toStruct())
    time.sleep(.1)
    server.stop()

def test_id():
    client = networking.Client(('localhost', 4567))
    server = networking.Server(4567)
    assert tests.wait(lambda: client.id is not None)
    assert client.id in server._clients

def test_send(createMessages):
    server = networking.Server(4562)
    client = networking.Client(('localhost', 4562))
    mock1 = Mock()
    server.addHandler(0x69, mock1)
    createMessages['message']['header']['destination'] = 1
    client.put(createMessages['message'].toStruct())
    assert tests.wait(lambda: mock1.called)
    client.stop()
    server.stop()

def test_send_relay(createMessages):
    server = networking.Server(4569)
    client = networking.Client(('localhost', 4569))
    client2 = networking.Client(('localhost', 4569))
    mock1 = Mock()
    client2.addHandler(0x69, mock1)
    assert tests.wait(lambda: client2.id is not None)
    createMessages['message']['header']['destination'] = client2.id
    client.put(createMessages['message'].toStruct())
    assert tests.wait(lambda: mock1.called)
    client.stop()
    client2.stop()
    server.stop()

def test_discovery():
    server = networking.Server(4571)
    client = networking.Client(('', 4571))
    assert not client.isConnected()
    assert tests.wait(lambda: client.isConnected)