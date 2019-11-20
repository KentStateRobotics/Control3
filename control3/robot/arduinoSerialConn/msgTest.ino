#define ID int(1)
//#include "arduinoSerialConn.ino"

msgStuff test;
//String message = "test1";

void setup() {
  test.sendId(ID);
}

void loop() {
  // put your main code here, to run repeatedly:
  String msg = "|4test";
  delay(500);
  test.sendMsg(msg);
}
