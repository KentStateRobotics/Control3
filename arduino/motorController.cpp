#include"motorController.h"

Motor(uint8_t startStopPin, uint8_t runBreakPin, uint8_t directionPin, 
uint8_t magnitudePin, uint8_t feedbackPin, uint16_t pulsesPerRotation, bool invertDirection){
    this->startStopPin = startStopPin;
    this->runBreakPin = runBreakPin;
    this->directionPin = directionPin;
    this->magnitudePin = magnitudePin;
    this->feedbackPin = feedbackPin;
    this->pulsesPerRotation = pulsesPerRotation;
    thuis->invertDirection = invertDirection;
    pinMode(feedbackPin, INPUT_PULLUP);
    pinMode(startStopPin, OUTPUT);
    pinMode(runBreakPin, OUTPUT);
    pinMode(directionPin, OUTPUT);
    pinMode(magnitudePin, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(feedbackPin), this->onFeedbackPulse, FALLING);
}

void command(bool CW, uint8_t level){
    this->currentLevel = level;
    this->currentDirection = CW;
    if(level == 0){
        digitalOutput(startStopPin, LOW);
    }else if(CW != invertDirection){
        digitalOutput(startStopPin, HIGH);
        digitalOutput(directionPin, HIGH)
    }else if(CW == invertDirection){
        digitalOutput(startStopPin, HIGH);
        digitalOutput(directionPin, LOW)
    }
    analogOutput(magnitudePin, level);
}

uint16_t getPosition(){ //In minutes
    return this->currentPosition;
}
int32_t getDeltaPosition(){ //Change in position in minutes sense last call
    int32_t temp = this->deltaPosition;
    this->deltaPosition = 0;
    return temp;
}

void onFeedbackPulse(){
    if(currentDirection){
        ++deltaPosition;
        currentPosition = currentPosition + 1 % 15600;
    }else{
        --deltaPosition;
        currentPosition = (currentPosition == 0) ? 15600 : currentPosition - 1;
    }
}