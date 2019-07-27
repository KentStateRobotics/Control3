import context
import unittest
from unittest import mock
import networking
from networking.message import Message
import networking.messages as messages

source = Message.padString("source", Message.NAME_LENGTH)
topic = Message.padString("topic", Message.NAME_LENGTH)
testMsg = Message({
    'int': 'i'
})

class TestSubscriber(unittest.TestCase):
    
    def test_topicException(self):
        def defineBadSubscriber():
            networking.Subscriber(source, 'a' * Message.NAME_LENGTH * 2, Message.MessageType.publisher.value, testMsg, None)
        self.assertRaises(ValueError, defineBadSubscriber)

    def test_messageTypeException(self):
        def defineBadSubscriber():
            networking.Subscriber(source, topic, Message.MessageType.publisher, testMsg, None)
        self.assertRaises(TypeError, defineBadSubscriber)

    def test_register(self):
        sub = networking.Subscriber(source, topic, Message.MessageType.publisher.value, testMsg, None)
        correctRegisterMessage = messages.SubscriberMsg.getFormat()
        correctRegisterMessage['source'] = source
        correctRegisterMessage['topic'] = topic
        correctRegisterMessage['messageType'] = Message.MessageType.publisher.value
        correctRegisterMessage['remove'] = False
        self.assertEqual(sub.getRegisterMsg(), correctRegisterMessage)
    
    def test_topicMatchAll(self):
        sub = networking.Subscriber('', topic, Message.MessageType.publisher.value, testMsg, None)
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.publisher.value
        header['timestamp'] = 24
        self.assertTrue(sub.topicMatch(header))

    def test_topicMatchFalse(self):
        sub = networking.Subscriber('notClient', topic, Message.MessageType.publisher.value, testMsg, None)
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.publisher.value
        header['timestamp'] = 24
        self.assertFalse(sub.topicMatch(header))
    
    def test_registerTopicMatch(self):
        reg = {
            'source': source,
            'topic': topic,
            'messageType': Message.MessageType.publisher.value,
        }
        header = Message.Header.getFormat()
        header['source'] = source
        header['topic'] = topic
        header['sequence'] = 0
        header['messageType'] = Message.MessageType.publisher.value
        header['timestamp'] = 24
        self.assertTrue(networking.Subscriber.registrationMatch(reg, header))

    def test_received(self):
        f = mock.Mock()
        sub = networking.Subscriber(source, topic, Message.MessageType.publisher.value, testMsg, f)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.publisher.value
        msg['header']['timestamp'] = 24
        sub.received(msg['header'], testMsg.pack(msg))
        f.assert_called_once_with(msg)


class TestPublisher(unittest.TestCase):
    
    def test_topicException(self):
        def defineBadPublisher():
            networking.Publisher(None, source, 'a' * Message.NAME_LENGTH * 2, Message.MessageType.publisher.value, testMsg)
        self.assertRaises(ValueError, defineBadPublisher)

    def test_messageTypeException(self):
        def defineBadPublisher():
            networking.Publisher(None, source, topic, Message.MessageType.publisher, testMsg)
        self.assertRaises(TypeError, defineBadPublisher)

    @mock.patch('time.time', return_value=10)
    def test_publish(self, timePatch):
        core = mock.MagicMock()
        sub = networking.Publisher(core, source, topic, Message.MessageType.publisher.value, testMsg)
        msg = testMsg.getFormat()
        msg['int'] = 456486
        sub.publish(msg)
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.publisher.value
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
            'messageType': Message.MessageType.publisher.value,
            'remove': False
        }
        client.subscribers = [reg, reg]
        msg = testMsg.getFormat()
        msg['int'] = 456486
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.publisher.value
        msg['header']['timestamp'] = 10
        packedMsg = testMsg.pack(msg)
        server.send(msg['header'], packedMsg)
        client.send.assert_called_once_with(packedMsg)

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
        msg['messageType'] = Message.MessageType.publisher.value
        msg['remove'] = False
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.publisher.value
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
        msg['messageType'] = Message.MessageType.publisher.value
        msg['remove'] = False
        msg['header']['source'] = source
        msg['header']['topic'] = topic
        msg['header']['sequence'] = 0
        msg['header']['messageType'] = Message.MessageType.publisher.value
        msg['header']['timestamp'] = 10
        server._recSubRegister(msg)
        msg['remove'] = True
        server._recSubRegister(msg)
        self.assertEqual(0, len(client.subscribers))

if __name__ == '__main__':
    unittest.main()