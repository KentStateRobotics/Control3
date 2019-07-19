from message import Message

Test = Message({
    'num': 'i',
    'string': '10s',
    'blob': 'blob'
})

Test2 = Message({
    'ahh': 'i',
    'bhh': 'i',
    'test': Test,
    'blob': 'blob'
})