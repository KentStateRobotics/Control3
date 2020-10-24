import multiprocessing
import logging
import KSRCore.networking
import KSRCore.logging

processLogger = logging.getLogger(KSRCore.logging.REMOTE_LOGGER + '.Process')

class Process(multiprocessing.Process):
    """Like the normal process, but setups the logger to pass logs to the main process.
        MUST CALL super().run() IN INHERITED CLASS
        Please try to stop on `self.stopEvent`
    """
    def __init__(self, routerQueue: 'multiprocessing.Queue', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.routerQueue = routerQueue
        self._stopEvent = multiprocessing.Event()
        
    def run(self):
        '''Must call in inherited class
        '''
        KSRCore.logging.addRemoteHandler(self.routerQueue)

    def stop(self):
        self._stopEvent.set()
        self.join(.3)
        if self.is_alive():
            processLogger.warn(f'Process {self.name} did not shutdown quietly')
            self.terminate()
