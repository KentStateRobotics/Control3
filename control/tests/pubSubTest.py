import context
import networking
from networking.message import Message 

strMsg = Message({
    'str':'blob'
})

def printMsg(msg):
    print("Client received: " + msg['str'].decode('utf-8'))

try:
    server = networking.Server("server", 4242)
    client = networking.Client("client", 4242, "127.0.0.1")
    clientPub = networking.Publisher(client, None, 'send', Message.MessageType.publisher.value, strMsg)
    clientSub = client.addSubscriber(server.name, 'rec', Message.MessageType.publisher.value, strMsg, printMsg)
    serverPub = networking.Publisher(server, None, 'rec', Message.MessageType.publisher.value, strMsg)
    def echoMsg(msg):
        print("Server PUBSUB received: " + msg['str'].decode('utf-8'))
        msg['str'] = msg['str'] + " but Echoed".encode()
        serverPub.publish(msg)
    serverSub = server.addSubscriber(client.name, 'send', Message.MessageType.publisher.value, strMsg, echoMsg)
    while True:
        instuff = input()
        msg = strMsg.getFormat()
        msg['str'] = instuff
        clientPub.publish(msg)
except (KeyboardInterrupt):
    pass
finally:
    server.close()
    client.close()



