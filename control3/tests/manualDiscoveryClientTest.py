import context
from networking.discovery import Discovery
import threading
import asyncio

port = 4342


clientDiscovery = Discovery(port)
print(clientDiscovery.find("server", 5))
