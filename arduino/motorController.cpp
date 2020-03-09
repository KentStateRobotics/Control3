#include"motorController.h"

Motor(uint8_t startStopPin, uint8_t runBreakPin, uint8_t directionPin, 
uint8_t magnitudePin, uint8_t feedbackPin, uint16_t pulsesPerRotation, 
uint16_t maxSpeed, bool invertDirection){
    this->startStopPin = startStopPin;
    this->runBreakPin = runBreakPin;
    this->directionPin = directionPin;
    this->magnitudePin = magnitudePin;
    this->feedbackPin = feedbackPin;
    this->pulsesPerRotation = pulsesPerRotation;
    this->invertDirection = invertDirection;
    this->speedMode = false;
    this->maxSpeed = maxSpeed;
    pinMode(feedbackPin, INPUT_PULLUP);
    pinMode(startStopPin, OUTPUT);
    pinMode(runBreakPin, OUTPUT);
    pinMode(directionPin, OUTPUT);
    pinMode(magnitudePin, OUTPUT);
    attachInterrupt(digitalPinToInterrupt(feedbackPin), this->onFeedbackPulse, FALLING);
}

void setValue(bool foward, uint8_t level){
    this->currentLevel = level;
    this->currentDirection = foward;
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

void setSpeed(bool foward, uint16_t speed){
    if(speed < this->maxSpeed){
        this->targetSpeed = speed;
        this->setValue(foward, (uint8_t)((float)speed / (float)this->maxSpeed * 255));
    }
}

void loopSpeedFeedback(){
    //TODO, feedback to percisely regulate speed if in speed mode
    if(this->speedMode){

    }
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