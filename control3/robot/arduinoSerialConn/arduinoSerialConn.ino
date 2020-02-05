#define ID 1
#include "arduinoSerialConn.cpp"

msgStuff test;

void setup() {
  test.sendId(ID);
}

int i;
void loop() {
  // put your main code here, to run repeatedly:
  //char msgToSend[] = {'t','e','s','t','\n'};
  char msg[80];
  int msgLength = test.recieveMsg(msg, 80);
  if (msgLength != -1){
    test.sendMsg(msg, msgLength);
  }
  //for (i; i < 50; ++i)
  //  test.sendMsg(msgToSend, 5);
}
