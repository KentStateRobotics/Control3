import Message from message

NAME_LENGTH = 10

MessageType = Message({
    publisher: 0,
    request: 1,
    response: 2,
    update: 3
})

Header = Message("Header", {
    timeStamp: "time",
    sender: str(NAME_LENGTH) + "s",
    topic: str(NAME_LENGTH) + "s",
    messageType: "c",
    sequence: "I"
})

Test = Message("Test", {
    header: Header,
    num: "i",
    string: "10s"
    blob: "blob"
})