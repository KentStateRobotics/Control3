#define ID 2
//#include "arduinoSerialConn.ino"

msgStuff test;
String message = "this is a test message\n";

void setup() {
  // put your setup code here, to run once:
  //msgStuff test;
  test.sendId();
}

void loop() {
  // put your main code here, to run repeatedly:
  test.sendMsg(message);
}
