import unittest
from unittest import mock
import networking
from networking.message import Message
import networking.messages as messages
from networking.subscriber import Subscriber
from networking.discovery import Discovery
import networking.service as service
import socket

source = Message.padString("source", Message.NAME_LENGTH)
topic = Message.padString("topic", Message.NAME_LENGTH)
testMsg = Message({
    'int': 'i'
})
testMsgBlob = Message({
    'blob': 'blob'
})

class TestSubscriber(unittest.TestCase):
    
    def test_topicException(self):
        def defineBadSubscriber():
            Subscriber(source, 'a' * Message.NAME_LENGTH * 2, testMsg, None)
        self.assertRaises(ValueError, defineBadSubscriber)

    def test_register(self):
        sub = Subscriber(source, topic, testMsg, None)
        correctRegisterMessage = messages.SubscriberMsg.getFormat()
        correctRegisterMessage['source'] = source
        correctRegisterMessage['topic'] = topic
        correctRegisterMessage['messageType'] = Message.MessageType.PUBLISHER.value
        correctRegisterMessage['remove'] = False
        self.assertEqual(sub.getRegisterMsg(), correctRegisterMessage)
    
    def test_topicMatchAll(self):
        sub = Subscriber('', topic, testMsg, None)
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.PUBLISHER.value
        header['timestamp'] = 24
        self.assertTrue(sub.topicMatch(header))

    def test_topicMatchFalse(self):
        sub = Subscriber('notClient', topic, testMsg, None)
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.PUBLISHER.value
        header['timestamp'] = 24
        self.assertFalse(sub.topicMatch(header))
    
    def test_registerTopicMatch(self):
        reg = {
            'source': source,
            'topic': topic,
            'messageType': Message.MessageType.PUBLISHER.value,
        }
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.PUBLISHER.value
        header['timestamp'] = 24
        self.assertTrue(Subscriber.registrationMatch(reg, header))

    def test_received(self):
        f = mock.Mock()
        sub = Subscriber(source, topic, testMsg, f)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 24
        sub.received(msg['header'], testMsg.pack(msg))
        f.assert_called_once_with(msg)


class TestPublisher(unittest.TestCase):

    def test_messageTypeException(self):
        def defineBadPublisher():
            networking.Publisher(None, source, topic, testMsg)
        self.assertRaises(TypeError, defineBadPublisher)

    @mock.patch('time.time', return_value=10)
    def test_publish(self, timePatch):
        core = mock.MagicMock()
        core.name = b'source'
        sub = networking.Publisher(core, topic, testMsg)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        sub.publish(msg)
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 10
        core.send.assert_called_once_with(msg['header'], testMsg.pack(msg))

class TestServer(unittest.TestCase):

    @mock.patch('networking.Server.Thread')
    def test_send(self, serverThread):
        client = mock.MagicMock()
        server = networking.Server("server", 4242)
        server.clients.append(client)
        reg = {
            'source': source,
            'topic': topic,
            'messageType': Message.MessageType.PUBLISHER.value,
            'remove': False
        }
        client.subscribers = [reg, reg]
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 10
        packedMsg = testMsg.pack(msg)
        server.send(msg['header'], packedMsg)
        client.send.assert_called_once_with(packedMsg)

    @mock.patch('networking.Server.Thread')
    def test_addSubscriber(self, serverThread):
        server = networking.Server("server", 4242)
        sub = server.addSubscriber("source", "topic", testMsg, None)
        self.assertTrue(sub in server.subscribers)
        msg = messages.SubscriberMsg.getFormat()
        msg['source'] = Message.padString("source", Message.NAME_LENGTH)
        msg['topic'] = Message.padString("topic", Message.NAME_LENGTH)
        msg['messageType'] = Message.MessageType.PUBLISHER.value
        msg['remove'] = False
        self.assertEqual(sub.getRegisterMsg(), msg)

    @mock.patch('networking.Server.Thread')
    def test_registerSubscriber(self, serverThread):
        client = mock.MagicMock()
        client.name = source
        client.subscribers = []
        server = networking.Server("server", 4242)
        server.clients.append(client)
        msg = messages.SubscriberMsg.getFormat()
        msg['source'] = Message.padString("a", Message.NAME_LENGTH)
        msg['topic'] = Message.padString("t", Message.NAME_LENGTH)
        msg['messageType'] = Message.MessageType.PUBLISHER.value
        msg['remove'] = False
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 10
        server._recSubRegister(msg)
        self.assertEqual(msg, client.subscribers[0])

    @mock.patch('networking.Server.Thread')
    def test_registerSubscriberRemove(self, serverThread):
        client = mock.MagicMock()
        client.name = source
        client.subscribers = []
        server = networking.Server("server", 4242)
        server.clients.append(client)
        msg = messages.SubscriberMsg.getFormat()
        msg['source'] = Message.padString("a", Message.NAME_LENGTH)
        msg['topic'] = Message.padString("t", Message.NAME_LENGTH)
        msg['messageType'] = Message.MessageType.PUBLISHER.value
        msg['remove'] = False
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 10
        server._recSubRegister(msg)
        msg['remove'] = True
        server._recSubRegister(msg)
        self.assertEqual(0, len(client.subscribers))

class TestClient(unittest.TestCase):

    @mock.patch('time.time', return_value=1)
    @mock.patch('networking.Client.Thread')
    @mock.patch('networking.Client.send')
    def test_addSubscriber(self, send, clientThread, time):
        client = networking.Client("client", 4242, host="127.0.0.1")
        sub = client.addSubscriber(source, topic, testMsg, None)
        self.assertTrue(sub in client.subscribers)
        msg = messages.SubscriberMsg.getFormat()
        msg['source'] = source
        msg['topic'] = topic
        msg['messageType'] = Message.MessageType.PUBLISHER.value
        msg['remove'] = False
        msg['header']['source'] = client.name
        msg['header']['topic'] = Message.padString(Subscriber.REGISTRATION_TOPIC, Message.NAME_LENGTH)
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 1
        send.assert_called_once_with(msg['header'], messages.SubscriberMsg.pack(msg))

    @mock.patch('time.time', return_value=1)
    @mock.patch('networking.Client.Thread')
    @mock.patch('networking.Client.send')
    def test_rmoveSubscriber(self, send, clientThread, time):
        client = networking.Client("client", 4242, host="127.0.0.1")
        sub = client.addSubscriber(source, topic, testMsg, None)
        client.removeSubscriber(sub)
        self.assertFalse(sub in client.subscribers)
        msg = messages.SubscriberMsg.getFormat()
        msg['source'] = source
        msg['topic'] = topic
        msg['messageType'] = Message.MessageType.PUBLISHER.value
        msg['remove'] = True
        msg['header']['source'] = client.name
        msg['header']['topic'] = Message.padString(Subscriber.REGISTRATION_TOPIC, Message.NAME_LENGTH)
        msg['header']['sequence'] = 1
        msg['header']['messageType'] = Message.MessageType.PUBLISHER.value
        msg['header']['timestamp'] = 1
        send.assert_called_with(msg['header'], messages.SubscriberMsg.pack(msg))

class TestDiscovery(unittest.TestCase):

    def setUp(self):
        self.sockMock = mock.MagicMock()
        self.port = 4242
        self.id = b'id'
        self.address = "192.168.0.69"
        self.discovery = Discovery(self.port)
        self.discoveryProtocolFactory = Discovery.DiscoveryProtocolFactory(self.id)
        self.serverSockMock = mock.MagicMock()
        self.discoveryProtocolFactory.connection_made(self.serverSockMock)

    def test_findSend(self):
        self.sockMock.recvfrom.return_value = (Discovery.RESPONSE, (self.address, self.port))
        @mock.patch('socket.socket', return_value=self.sockMock)
        def inTestFind(socket):
            address = self.discovery.find(self.id, 1)
            self.sockMock.sendto.assert_called_once_with(self.id, ('<broadcast>', self.port))
        inTestFind()

    def test_findReturn(self):
        self.sockMock.recvfrom.return_value = (Discovery.RESPONSE, (self.address, self.port))
        @mock.patch('socket.socket', return_value=self.sockMock)
        def inTestFind(socket):
            address = self.discovery.find(self.id, 1)
            self.assertEqual(address, self.address)
        inTestFind()

    def test_findIterations(self):
        self.sockMock.recvfrom.side_effect = socket.timeout()
        @mock.patch('socket.socket', return_value=self.sockMock)
        def inTestFind(socket):
            address = self.discovery.find(self.id, 5)
            self.assertEqual(5, self.sockMock.recvfrom.call_count)
        inTestFind()

    def test_receive(self):
        self.discoveryProtocolFactory.datagram_received(self.id, (self.address, self.port))
        self.serverSockMock.sendto.assert_called_once_with(Discovery.RESPONSE, ('<broadcast>', self.port))

    def test_receiveNegitive(self):
        self.discoveryProtocolFactory.datagram_received("AHHHH", (self.address, self.port))
        self.serverSockMock.sendto.assert_not_called()

class TestService(unittest.TestCase):

    @mock.patch('time.time', return_value=1)
    def test_response(self, time):
        networkCore = mock.MagicMock()
        networkCore.name = source
        networkCore.addSubscriber.side_effect = Subscriber
        def testMsgIncrement(msg):
            msg['blob'] = "A" + str(msg['int'] + 1)
            return msg

        incrementService = service.Service(networkCore, source, topic, testMsg, testMsgBlob, testMsgIncrement)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.REQUEST.value
        msg['header']['timestamp'] = 1
        incrementService.sub.received(msg['header'], testMsg.pack(msg))
        msg['header']['messageType'] = Message.MessageType.RESPONSE.value
        msg.pop('int')
        msg['blob'] = "A456487"
        networkCore.send.assert_called_once_with(msg['header'], testMsgBlob.pack(msg))

    @mock.patch('time.time', return_value=1)
    def test_requestSend(self, timeSpoof):
        networkCore = mock.MagicMock()
        networkCore.addSubscriber.side_effect = Subscriber
        networkCore.name = source
        callback = mock.MagicMock()
        testProxyService = service.ServiceClient(networkCore, source, topic, testMsg, testMsg, callback)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.REQUEST.value
        msg['header']['timestamp'] = 1
        testProxyService.call(msg)
        networkCore.send.assert_called_once_with(msg['header'], testMsg.pack(msg))

    @mock.patch('time.time', return_value=1)
    def test_requestCallback(self, timeSpoof):
        networkCore = mock.MagicMock()
        networkCore.addSubscriber.side_effect = Subscriber
        networkCore.name = source
        callback = mock.MagicMock()
        testProxyService = service.ServiceClient(networkCore, source, topic, testMsg, testMsg, callback)
        def changeMsgTypeAndSend(header, msg):
            msg = testMsg.unpack(msg)[0]
            msg['header']['messageType'] = Message.MessageType.RESPONSE.value
            testProxyService.sub.received(msg['header'], testMsg.pack(msg))

        networkCore.send.side_effect = changeMsgTypeAndSend
        msg = testMsg.getFormat()
        msg['int'] = 7
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['timestamp'] = 1
        testProxyService.call(msg)
        msg['header']['messageType'] = Message.MessageType.RESPONSE.value
        callback.assert_called_once_with(msg)


if __name__ == '__main__':
    unittest.main()