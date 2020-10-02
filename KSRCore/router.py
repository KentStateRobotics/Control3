import multiprocessing
import threading
import KSRCore.message as message

JOIN_TIMEOUT = .2

class Router(threading.Thread):
    def __init__(self):
        super().__init__(name="Router_Handlers", daemon=True)
        self._queue = multiprocessing.SimpleQueue()
        self._handlers = {}
        self._handlerLock = threading.Lock()
        self._stopEvent = threading.Event()
        self.start()

    def addHandler(self, channel, handler):
        with self._handlerLock:
            self._handlers[channel] = handler

    def removeHandlers(self, channel=None):
        with self._handlerLock:
            if channel is None:
                self._handlers.clear()
            else:
                self._handlers.pop(channel, None)

    def put(self, message):
        self._queue.put(message)

    def stop(self):
        self._stopEvent.set()
        self.join(JOIN_TIMEOUT)

    def run(self):
        while True:
            if not self._queue.empty():
                data = self._queue.get()
                handler = None
                with self._handlerLock:
                    handler = self._handlers.get(message.Message.peekHeader(data)['channel'])
                    if handler:
                        handler(data)
            if self._stopEvent.is_set():
                return
