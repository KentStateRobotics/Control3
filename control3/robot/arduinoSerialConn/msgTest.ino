#define ID int(1)
//#include "arduinoSerialConn.ino"

msgStuff test;

void setup() {
  test.sendId(ID);
}

void loop() {
  // put your main code here, to run repeatedly:
  String msgIn = test.recieveMsg();
  if (msgIn != ""){
    test.sendMsg(msgIn);
  }
  test.sendMsg("test");
}
 
void msgStuff::sendMsg(String msg) {
  Serial.print('|');
  Serial.print(msg.length());
  Serial.print(msg);
}
