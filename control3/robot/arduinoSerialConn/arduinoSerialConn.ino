#ifndef MSG_MODULE
#define MSG_MODULE

#define START '|'
#define ID 1

#include "dnode.hpp"

class msgStuff{
public:
  void sendId();
  void sendMsg(String msg);
private:
  String msgOut = "";
  String msgIn = "";
};

void msgStuff::sendId(){
  Serial.begin(115200);
  Serial.print(ID);
  pinMode(13, OUTPUT);
}

void msgStuff::sendMsg(String msg) {
  Serial.print(msg);
}
#endif
