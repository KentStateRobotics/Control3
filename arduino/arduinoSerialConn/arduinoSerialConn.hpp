#ifndef MSG_MODULE
#define MSG_MODULE

#include <arduino.h>

#ifndef START_CHAR
#define START_CHAR
  #define START '|'
  #define SECONDSTART '~'
#endif

class msgStuff{
  private: 
    bool sentId = false;
    String msgOut = "";
    String msgIn = "";
  
  public:
    void sendId(int);
    int recieveMsg(char[], int);
    void sendMsg(char[], int);
    void hdwCode(char[]);
};

#endif
