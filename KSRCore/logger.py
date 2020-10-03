import logging
import sys

def init(filepath=None):
    detailedFormat = logging.Formatter('%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(threadName)-10s %(message)s')
    rootLogger = logging.getLogger()
    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(detailedFormat)
    rootLogger.addHandler(stdHandler)
    if not filepath is None:
        fileHandler = logging.FileHandler("KSRCoreLog")
        fileHandler.setFormatter(detailedFormat)
        rootLogger.addHandler(fileHandler)