#define ID 1
//#include "arduinoSerialConn.ino"

msgStuff test;
String message = "test1";

void setup() {
  // put your setup code here, to run once:
  //msgStuff test;
  test.sendId();
}

void loop() {
  // put your main code here, to run repeatedly:
  String msg;
  msg = test.recieveMsg();
  Serial.print(msg);
}
