#!/usr/bin/env python
'''
networking
KentStateRobotics Jared Butcher 7/17/2019
'''
import websockets
import threading
import struct
import socket
import asyncio

class NetworkCore:
    def __init__(self, name, port, host=None):
        self.running = True
        self.name = name
        self.host = host
        self.port = port
        self.alive = True
        self.clients = []
        self.thread = NetworkThread(self)
        self.thread.start()

    def send(self, message, target):
        if self.host is None:
            for client in self.clients:
                if client.name == target:
                    client.send(message)
        else:
            print(self.thread.conn)
            if not self.thread.conn is None:
                asyncio.run_coroutine_threadsafe(self.thread.conn.send(message), self.thread.loop)

    def destory(self):
        self.alive = False
        for client in self.clients:
            client.destory()
        if not self.thread is None:
            self.thread.alive = False
            self.thread.loop.call_soon_threadsafe(self.thread.loop.stop)
            self.thread.join()
            

class NetworkClient:
    def __init__(self, core, conn):
        self.core = core
        self.conn = conn
        self.name = "client"
        self.alive = True
        self.loop = asyncio.get_event_loop()

    async def read(self):
        while self.alive:
            try:
                message = await self.conn.recv()
                print("REC:")
                print(message)
            except websockets.exceptions.ConnectionClosed:
                self.destory()

    def send(self, message):
        asyncio.run_coroutine_threadsafe(self.conn.send(message), self.loop)

    def destory(self):
        self.alive = False
        self.core.clients.remove(self)

class NetworkThread(threading.Thread):
    def __init__(self, core):
        self.alive = True
        self.core = core
        threading.Thread.__init__(self)

    def run(self):
        print("Networking thread started")
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        if self.core.host is None:
            self.server = self.loop.run_until_complete(websockets.server.serve(self._recNewConn, host='', port=self.core.port, loop=self.loop))
        else:
            self.uri = "ws://" + self.core.host + ":" + str(self.core.port)
            while self.alive:
                try:
                    self.loop.run_until_complete(self._clientConnectAndRead())
                except websockets.exceptions.ConnectionClosed:
                    self.conn = None
                    print("disconnected, atempting to reconnect")
        self.loop.run_forever()

    async def _recNewConn(self, conn, url):
        print("Received new Connection Request")
        client = NetworkClient(self.core, conn)
        self.core.clients.append(client)
        await client.read()
    
    async def _clientConnectAndRead(self):
        try:
            async with websockets.connect(self.uri) as self.conn:
                print("Connection established")
                while self.alive:
                    message = await self.conn.recv()
                    print("REC:")
                    print(message)
        except (ConnectionRefusedError, ConnectionResetError) as e:
            print(e)
            
    
    def _stopAndReconnect(self):
        self.loop.stop()
        self.loop.run_until_complete(self._clientConnectAndRead())
        self.loop.run_forever()





