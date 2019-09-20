from networking.discovery import Discovery
import threading
import asyncio

port = 4342

loop = asyncio.get_event_loop()
discoEcho = Discovery(port)
try:
    print("Starting Server")
    coro = loop.run_until_complete(discoEcho.echoAddress("server", loop))
    loop.run_forever()
except KeyboardInterrupt:
    print("Stopping Server")
    discoEcho.close()
    loop.stop()

