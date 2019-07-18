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
            for client in clients:
                if client.name == target:
                    client.send(message)
        else:
            self.conn.send(message)

    def destory(self);
        self.alive = False
        for client in self.clients:
            client.destory()

class NetworkThread(threading.Thread):
    def __init__(self, core):
        self.alive = True
        self.core = core
        threading.Thread.__init__(self)

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        if self.core.host is None:
            self.server = self.loop.run_until_complete(websockets.server.serve(self._recNewConn, host='', port=self.core.port, loop=self.loop))
        else:
            uri = "ws://" + self.core.host + ":" + self.core.port
            self.conn = websockets.connect(uri)
            self.loop.run_until_complete(self._clientRead())

    async _recNewConn(self, conn, url):
        client = networkClient(self, conn)
        self.clients.append(client)
        await client.read()
    
    async _clientRead(self):
        while self.alive:
            try:
                await message = self.conn.recv()
            except websockets.exceptions.ConnectionClosed:
                print("disconnected from server, trying to reconnect")
                self.run()


class NetworkClient:
    def __init__(self, core, conn):
        self.core = core
        self.conn = conn
        self.name = ""
        self.alive = True
        self.loop = asyncio.get_event_loop()

    async def read(self):
        while self.alive:
            try:
                await message = self.conn.recv()
            except websockets.exceptions.ConnectionClosed:
                self._destory()

    def send(self, message):
        asyncio.run_coroutine_threadsafe(self.conn.send(message), self.loop)

    def destory(self):
        self.alive = False
        self.core.clients.remove(self)

