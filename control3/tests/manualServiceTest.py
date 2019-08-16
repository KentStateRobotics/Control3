import context
import networking
from networking import service
from networking.message import Message 

blobMsg = Message({
    'blob':'blob'
})

def printMsg(msg):
    print("Client received: " + msg['blob'].decode())

def increment(msg):
    msg['blob'] += b' but some more'
    return msg

try:
    server = networking.Server("server", 4242, 4243)
    client = networking.Client("client", 4242, discoveryPort=4243, discoveryId="server")
    serverService = service.Service(server, "server", "increment", blobMsg, blobMsg, increment)
    #clientProxy = service.ProxyService(client, "server", "increment", blobMsg, blobMsg, printMsg)
    clientBlockProxy = service.ProxyServiceBlocking(client, "server", "increment", blobMsg, blobMsg)
    while True:
        instuff = input()
        msg = blobMsg.getFormat()
        msg['blob'] = instuff
        msg = clientBlockProxy.call(msg, 2)
        print("Client received: " + msg['blob'].decode())
except (KeyboardInterrupt):
    pass
finally:
    server.close()
    client.close()



