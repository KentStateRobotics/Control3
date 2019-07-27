import context
import networking

try:
    server = networking.Server("server", 4242)
    client = networking.Client("client", 4242, "127.0.0.1")
    input()
    server.close()
    client.close()
except (KeyboardInterrupt, Exception):
    server.close()
    client.close()



