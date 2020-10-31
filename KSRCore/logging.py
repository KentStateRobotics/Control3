from typing import Optional
import logging
import sys
import copy
import KSRCore.networking as networking

SHORT_FORMAT = logging.Formatter('%(message)s')
LONG_FORMAT = logging.Formatter('%(asctime)s|%(name)-16s|%(levelname)-8s|%(processName)-8s|%(message)s')

def initLogging(routerQueue: 'multiprocessing.Queue', level: Optional[int] = 20, filepath: Optional[str] = None):
    networking.localLogger.propagate = False
    networking.localLogger.setLevel(level if level else 20)
    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(SHORT_FORMAT)
    networking.localLogger.addHandler(stdHandler)
    forceFormatHandler = ForceFormatHandler()
    forceFormatHandler.setFormatter(LONG_FORMAT)
    networking.networkingLogger.addHandler(forceFormatHandler)
    networking.networkingLogger.setLevel(level if level else 20)
    if not filepath is None:
        fileHandler = logging.FileHandler(filepath)
        fileHandler.setFormatter(SHORT_FORMAT)
        logger.addHandler(fileHandler)
    initProcessLogging(routerQueue, level)

def initProcessLogging(routerQueue: 'multiprocessing.Queue', level: Optional[int] = 0):
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level if level else 20)
    remoteHandler = RemoteLoggingHandler(routerQueue)
    remoteHandler.setFormatter(LONG_FORMAT)
    rootLogger.addHandler(remoteHandler)

class RemoteLoggingHandler(logging.Handler):
    """
    This handler packs events into a logging message and sends them to the routing queue
    """

    def __init__(self, routerQueue: 'multiprocessing.Queue'):
        logging.Handler.__init__(self)
        self.routerQueue = routerQueue

    def enqueue(self, record):
        msg = networking.logMessage.createMessage({'level': record.levelno, 'message': record.msg})
        msg.setHeader(0, 1, networking.Channels.NETWORKING.value, networking.NetworkingTypes.LOG.value)
        self.routerQueue.put(msg.toJson())

    def prepare(self, record):
        msg = self.format(record)
        # bpo-35726: make copy of record to avoid affecting other handlers in the chain.
        record = copy.copy(record)
        record.message = msg
        record.msg = msg
        record.args = None
        record.exc_info = None
        record.exc_text = None
        return record

    def emit(self, record):
        try:
            self.enqueue(self.prepare(record))
        except Exception:
            self.handleError(record)

class ForceFormatHandler(logging.Handler):
    def emit(self, record):
        if self.format:
            msg = self.format(record)
            record.message = msg
            record.msg = msg
            record.args = None
            record.exc_info = None
            record.exc_text = None