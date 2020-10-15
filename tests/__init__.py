import time

def wait(poll, timeout=1, increment=.1):
    startTime = time.time()
    while time.time() - startTime < timeout:
        if poll():
            return True
        time.sleep(increment)
    return False
