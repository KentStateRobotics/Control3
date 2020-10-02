import multiprocessing
import threading
import message

class Router():
    def __init__(self):
        self._queue = multiprocessing.SimpleQueue()
        self._handlers = {}
        self._handlerLock = threading.Lock()
        self._handlerThread = threading.Thread(target=)

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

    def _runHander(self):
        if not self._queue.empty():
            message = self._queue.get()
            handler = None
            with self._handlerLock:
                handler = self._handlers[message.Message.peekHeader(message)]
