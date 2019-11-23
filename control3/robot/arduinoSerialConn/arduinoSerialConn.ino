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
  int msgLength;        //lngth of message
  String msg = "";      //message with corrected start

  char t = Serial.read();
  if (t == START){
    msgLength = Serial.parseInt()-1;
    msg = Serial.readString();
    //Serial.print(msgLength);
    //for (int i = 0; i < msgLength; ++i){
    //  t = Serial.read();
    //  Serial.print(' ');
    //  Serial.print(t);
    //  msg += t;
    //}
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
