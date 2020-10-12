import time

def wait(poll, timeout=1, increment=.1):
    startTime = time.time()
    while startTime - time.time() < timeout:
        if poll():
            return True
        time.sleep(increment)
    return False
