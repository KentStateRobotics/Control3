#ifndef MSG_MODULE
#define MSG_MODULE

#define START '|'
//#include "dnode.hpp"

class msgStuff{
public:
  void sendId(int ID);
  void sendMsg(String &msg);
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
  int msgLength;        //lngth of message
  String msg = "";      //message with corrected start

  String t = Serial.readString();
  if (t[0] == START){
    msgLength = int(t[1]);
    for (int i = 0; i < msgLength; ++i){
      msg += t[2+i];
    }
    return msg;
  } else{
    return "";
  }
}
/*
void msgStuff::sendMsg(String msg) {
  //Serial.print('|');
  //Serial.print(msg.length());
  Serial.print(msg);
}
*/
#endif
