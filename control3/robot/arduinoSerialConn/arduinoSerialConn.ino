#ifndef MSG_MODULE
#define MSG_MODULE

#define START '|'
//#include "dnode.hpp"

class msgStuff{
public:
  void sendId(int ID);
  void sendMsg(String msg);
  String recieveMsg();
private:
  bool sentId = false;
  String msgOut = "";
  String msgIn = "";
};

void msgStuff::sendId(int ID){
  Serial.begin(115200);
  while(!Serial);
  Serial.println(ID);
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
  
  //need to send lenght speratly from rest
  //use serial.write()
  Serial.print('|');
  Serial.print(msg.length());
  Serial.print(/*+ hwCode+*/ msg);
}
#endif
