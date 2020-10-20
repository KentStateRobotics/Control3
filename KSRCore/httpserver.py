import http.server
import functools
import threading
import logging

logger = logging.getLogger('KSRC.http')

class HttpServer(threading.Thread):
    def __init__(self, httpDir, port=80, logLevel=40):
        super().__init__(daemon=True)
        self.httpServer = None
        self._port = port
        self._httpDir = httpDir
        self._logLevel=logLevel if logLevel else 40
        self.start()

    def run(self):
        self.httpServer = http.server.HTTPServer(('', self._port), functools.partial(SimplerHandler, directory=self._httpDir))
        self.httpServer.serve_forever()

    def stop(self):
        shutdownThread = threading.Thread(target=self.httpServer.shutdown, daemon=True)
        shutdownThread.start()
        shutdownThread.join(.2)
        self.join(.1)
        if self.is_alive:
            logger.warning("Http server thread failed to close")
            return False
        return True

class SimplerHandler(http.server.SimpleHTTPRequestHandler):
    def log_error(self, *args):
        logger.error(*args)

    def log_message(self, *args):
        logger.debug(*args)

    def log_request(self, code='-', size='-'):
        logger.debug('Request status: %s', str(code))