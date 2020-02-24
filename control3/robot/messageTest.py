from serialConn import msgContainer
import serialConn

def foo(self, msg):
    return("this is a test:",msg)

testMsg = msgContainer()
#testMsg.queueMsg("qwertyuiop", 1)
testMsg.addFunc(foo)