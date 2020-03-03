from serialConn import msgContainer
import serialConn

def foo(msg):
    print("this is a test of callbacks:",msg)
def bar(msg):
    print("this is a second test of callbacks:",msg)
testMsg = msgContainer()
testMsg.addFunc(foo)
testMsg.addFunc(bar)
testMsg.queueMsg("qwertyuiop", 1)
