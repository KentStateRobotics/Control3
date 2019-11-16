#ifndef MSG_MODULE
#define MSG_MODULE

#define START '|'
#define ID 1

//#include "dnode.hpp"

class msgStuff{
public:
  void sendId();
  void sendMsg(String msg);
  String recieveMsg();
private:
  String msgOut = "";
  String msgIn = "";
};

void msgStuff::sendId(){
  Serial.begin(115200);
  Serial.print(ID);
  pinMode(13, OUTPUT);
}

String msgStuff::recieveMsg() {
  char msgIn;           //messages recieved from USB
  int msgLength;        //lngth of message
  String msg = "";      //message with corrected start
  int charNum;          //length of message
  int i;                //iterable

  while (true){
    msgIn = Serial.read();
    if (msgIn == START){
      msg += msgIn;
      msgLength = Serial.read();
      int i = 0;
      while (i <= msgLength) {
        msg += Serial.read();
        ++i;
      }
      break;
    }
  }
  return msg;
}

void msgStuff::sendMsg(String msg) {
  //String hwCode = "";
  //switch to select hwCode
  msg = '/' + msg.length() /*+ hwCode*/+ msg;
  Serial.print(msg);
}
#endif
