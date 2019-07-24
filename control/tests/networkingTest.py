import context
import networking
from networking import message
import unittest
from unittest import mock
import timeout_decorator
import time

TestMsg = message.Message({
    'num': 'i'
})

TestNestedMsg = message.Message({
    'num': 'i',
    'test': TestMsg,
    'blob': 'blob'
})

class TestNetworking(unittest.TestCase):
    
    

    def test_serverSendClientReceive(self):
        server = networking.NetworkCore("server", 4242)
        client = networking.NetworkCore("client", 4242, "127.0.0.1")
        s2cPub = server.publisher("s2c", TestMsg)
        s2cCallback = mock.Mock()
        s2cSub = client.subscriber("server", "s2c", TestMsg, s2cCallback)
        msg = TestMsg.getFormat()
        msg['num'] = 42
        s2cPub.publish(msg)
        time.sleep(.5)
        s2cCallback.assert_called_once_with(msg)

if __name__ == '__main__':
    timeout_decorator.timeout(3, use_signals=False)(unittest.main)()