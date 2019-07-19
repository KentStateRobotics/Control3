import message
import messages

test = messages.Test2.getFormat()

test['test']['num'] = 15
test['test']['string'] = b'hello'
test['test']['blob'] = b'hello but of variable length :)'
test['header']['sender'] = b'me'
test['header']['topic'] = b'testPub'
test['header']['messageType'] = message.MessageType.request.value
test['header']['sequence'] = 1
test['ahh'] = 177
test['bhh'] = 242
test['blob'] = b'The second blob AHHHHHHHH'

print(test)

data = messages.Test2.pack(test)

print(data)

out, d = messages.Test2.unpack(data)

print(out)