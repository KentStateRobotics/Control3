#include "arduinoSerialConn.hpp"
  void msgStuff::sendId(int _ID){
    Serial.begin(115200);
    while(!Serial);
    Serial.println(_ID);
  }
  
  int msgStuff::recieveMsg(char arr[], int maxSize) {
    int msgLength;
    
    byte t = Serial.read();
    if (t == START){
      msgLength = Serial.parseInt();
      while(!Serial.available()) 
          delay(1);
      Serial.read();
      if(msgLength > maxSize) 
        return -1;
      for(int i = 0; i < msgLength; i++){
        while(!Serial.available()) 
          delay(1);
        int tmp = Serial.read();
        if(tmp != -1){
          arr[i] = (char)tmp;
        }else return -1;
      }
      return msgLength;
    } else{
      return -1;
    }
  }

  void msgStuff::sendMsg(char msg[], int lngth) {
    Serial.print(START);
    Serial.print(lngth);
    Serial.print(SECONDSTART);
    for(int i = 0; i < lngth; i++){
      Serial.print(msg[i]);
    }
    Serial.print('\n');
  }
