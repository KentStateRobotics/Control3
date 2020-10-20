import logging
import sys

def initLogging(level=20, filepath=None):
    detailedFormat = logging.Formatter('%(asctime)s|%(name)-10s|%(levelname)-8s|%(processName)-10s|%(threadName)-10s|%(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level if level else 20)
    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(detailedFormat)
    rootLogger.addHandler(stdHandler)
    if not filepath is None:
        fileHandler = logging.FileHandler(filepath)
        fileHandler.setFormatter(detailedFormat)
        rootLogger.addHandler(fileHandler)