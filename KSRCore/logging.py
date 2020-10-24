from typing import Optional
import logging
import sys

BASE_LOGGER = 'KSRC'
REMOTE_LOGGER = 'REMOTE'

def addBaseHandlers(level: Optional[int] = 20, filepath: Optional[str] = None):
    detailedFormat = logging.Formatter('%(asctime)s|%(name)-16s|%(levelname)-8s|%(message)s')
    logger = logging.getLogger(BASE_LOGGER)
    logger.setLevel(level if level else 20)
    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(detailedFormat)
    logger.addHandler(stdHandler)
    if not filepath is None:
        fileHandler = logging.FileHandler(filepath)
        fileHandler.setFormatter(detailedFormat)
        logger.addHandler(fileHandler)


def addRemoteHandler(routerQueue: 'multiprocessing.Queue') -> 'KSRCore.networking.RemoteLoggingHandler':
    logger = logging.getLogger(REMOTE_LOGGER)
    remoteFormat = logging.Formatter('%(message)s')
    handler = RemoteLoggingHandler(routerQueue)
    logger.addHandler(handler)


class RemoteLoggingHandler(logging.Handler):
    """
    This handler packs events into a logging message and sends them to the routing queue
    """

    def __init__(self, routerQueue: 'multiprocessing.Queue'):
        logging.Handler.__init__(self)
        self.routerQueue = routerQueue

    def enqueue(self, record):
        msg = logMessage.createMessage({'level': record.levelno, 'name': record.name.encode('utf-8'), 'message': record.msg})
        msg.setHeader(0, 1, Channels.NETWORKING.value, NetworkingTypes.LOG.value)
        self.routerQueue.put(msg.toStruct())


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
