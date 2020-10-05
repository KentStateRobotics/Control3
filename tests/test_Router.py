import pytest
import time
from unittest.mock import Mock
from KSRCore.message import MessageFactory, Message
from KSRCore.router import Router

@pytest.fixture(scope='module')
def createMessages():
    msgFact = MessageFactory({
            'num': 'i',
            'blob': 'blob'
        })
    msgFilled = msgFact.createMessage({
        'header':{
            'timestamp': 424.5,
            'source': 0x73,
            'destination': 0xa0,
            'channel': 0x69,
            'type': 0xa1,
        },
        'num': 456,
        'blob': b'This is a blob'
    })
    return {'factory': msgFact, 'message': msgFilled}

def test_router_create_destory():
    router = Router()
    assert router.is_alive()
    router.stop()
    assert not router.is_alive()

def test_router_add_remove_handler():
    router = Router()
    router.addHandler(0x45, Mock())
    assert 0x45 in router._handlers
    router.addHandler(0x55, Mock())
    router.removeHandlers(0x45)
    assert 0x45 not in router._handlers
    assert 0x55 in router._handlers
    router.removeHandlers()
    assert 0x55 not in router._handlers

def test_router_route(createMessages):
    router = Router()
    mock1 = Mock()
    mock2 = Mock()
    mock3 = Mock()
    router.addHandler(0x69, mock1)
    router.addHandler(0x42, mock2)
    router.addHandler(0xa3, mock3)
    router.put(createMessages['message'].toStruct())
    createMessages['message']['header']['channel'] = 0xa3
    router.put(createMessages['message'].toJson())
    time.sleep(.1)
    router.stop()
    mock1.assert_called_once()
    mock2.assert_not_called()
    mock3.assert_called_once()

def test_router_unhandled(createMessages):
    router = Router()
    router.put(createMessages['message'].toStruct())
    time.sleep(.1)
    router.stop()