import context
import networking
from networking import message
from networking import publisher
from networking import messages
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

subRegisterMessage = {
    'source': b'server\x00\x00\x00\x00', 
    'topic': b's2c\x00\x00\x00\x00\x00\x00\x00', 
    'remove': False, 
    'header': {
        'timestamp': None, 
        'source': None, 'topic': None, 
        'messageType': None, 
        'sequence': None
        }
    }
time.sleep(1)

class TestNetworking(unittest.TestCase):
    
    port = 4242

    def setUp(self):
        self.server = networking.NetworkCore("server", TestNetworking.port)
        self.client = networking.NetworkCore("client", TestNetworking.port, "localhost")
        time.sleep(1)
    
    @mock.patch('networking.publisher.Publisher.publish')
    def test_clientSubRegister(self, publish):
        s2cSub = self.client.subscriber("server", "s2c", TestMsg, None)
        publish.assert_called_once_with(subRegisterMessage)

    @mock.patch('networking.networking.NetworkThread.clientSendToServer')
    def test_connect(self, clientSend):
        self.client.registrationPub.publish(subRegisterMessage)
        clientSend.assert_called_once()

    @mock.patch('networking.networking.NetworkThread.clientSendToServer')
    def test_serverRegisterSub(self, clientSend):
        msg = None
        def grabMsg(*args, **kargs):
            nonlocal msg
            msg = args[0]
        clientSend.side_effect = grabMsg
        self.client.registrationPub.publish(subRegisterMessage)
        clientSend.assert_called_once()
        self.server.clients[0].name = message.padString("client", 10)
        self.server.registrationSub.received(msg)
        self.assertEqual(self.server.clients[0].subs[0], messages.SubscriberMsg.unpack(msg)[0])

    def tearDown(self):
        self.server.destory()
        self.client.destory()
        TestNetworking.port += 1


if __name__ == '__main__':
    timeout_decorator.timeout(5, use_signals=False)(unittest.main)()