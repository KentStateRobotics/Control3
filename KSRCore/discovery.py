'''
discovery
KentStateRobotics Jared Butcher 7/29/2019
'''
import socket
import asyncio
import time
import logging
import KSRCore.logging

discoveryLogger = logging.getLogger('Discovery')

class Discovery:
    '''Used UTP broadcasts to find users running echoAddress
    '''
    RESPONSE = "res".encode()

    def __init__(self, port):
        self.port = port
        self.transport = None

    def find(self, id, tries):
        '''Trys to find user with matching id for the timeout duration
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', self.port))
        sock.settimeout(1)
        retries = 0
        if type(id) == str:
            id = id.encode()
        while True:
            try:
                sock.sendto(id, ('<broadcast>', self.port))
                data, address = sock.recvfrom(1024)
                while data != Discovery.RESPONSE:
                    address = None
                    data, address = sock.recvfrom(1024)
                if not address is None:
                    sock.close()
                    return address[0]
            except socket.timeout:
                retries += 1
                if retries >= tries:
                    discoveryLogger.warn("Failed to receive address from {} in {} atempts".format(id.decode("utf-8"), retries))
                    return None
                else:
                    discoveryLogger.debug("Failed to receive address from {}, retrying".format(id.decode("utf-8")))

    async def echoAddress(self, id, eventLoop):
        '''Run on server in event loop. Will pong pings for the id.
        '''
        self.transport, protocol = await eventLoop.create_datagram_endpoint(
            lambda: Discovery.DiscoveryProtocolFactory(id),
            local_addr=('', self.port),
            family = socket.AF_INET,
            proto=socket.IPPROTO_UDP,
            allow_broadcast=True
        )

    def close(self):
        if not self.transport is None:
            self.transport.close()

    class DiscoveryProtocolFactory:
        def __init__(self, name):
            if type(name) == str:
                self.name = name.encode()
            else:
                self.name = name
        def connection_made(self, transport):
            self.transport = transport
        def datagram_received(self, data, address):
            if type(data) == str:
                data = data.encode('utf-8')
            if self.name == data:
                self.transport.sendto(Discovery.RESPONSE, ('<broadcast>',address[1]))