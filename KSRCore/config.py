import logging
import sys

#TODO: Config file

DEFAULT_PORT = 4242
DISCOVERY_ID = "Default"

def initLogging(level=20, filepath=None):
    detailedFormat = logging.Formatter('%(asctime)s|%(name)-16s|%(levelname)-8s|%(message)s')
    rootLogger = logging.getLogger()
    rootLogger.setLevel(level if level else 20)
    stdHandler = logging.StreamHandler(stream=sys.stdout)
    stdHandler.setFormatter(detailedFormat)
    rootLogger.addHandler(stdHandler)
    if not filepath is None:
        fileHandler = logging.FileHandler(filepath)
        fileHandler.setFormatter(detailedFormat)
        rootLogger.addHandler(fileHandler)

