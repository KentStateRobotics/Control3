import http.server
import functools
import multiprocessing
import threading
import logging
import time
from typing import Optional
import KSRCore.process

logger = logging.getLogger('KSRC.http')

class HttpServer(KSRCore.process.Process):
    def __init__(self, routerQueue: 'multiprocessing.Queue', httpDir: str, port: Optional[int] = 80):
        '''Create and start the simple http server

            `httpDir` is the directory to serve files from
        '''
        super().__init__(routerQueue, daemon=True, name="HTTP")
        self.httpServer = None
        self._port = port
        self._httpDir = httpDir
        self.start()

    def run(self):
        super().run()
        checkStopThread = threading.Thread(daemon=True, target=self.checkStop)
        checkStopThread.start()
        self.httpServer = http.server.HTTPServer(('', self._port), functools.partial(SimplerHandler, directory=self._httpDir))
        self.httpServer.serve_forever()

    def checkStop(self):
        while True:
            time.sleep(.1)
            if self._stopEvent.is_set():
                self.httpServer.shutdown()
                return

class SimplerHandler(http.server.SimpleHTTPRequestHandler):
    def log_error(self, *args):
        logger.error(*args)

    def log_message(self, *args):
        logger.debug(*args)

    def log_request(self, code='-', size='-'):
        logger.debug('Request status: %s', str(code))