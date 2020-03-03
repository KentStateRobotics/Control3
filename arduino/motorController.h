/* Kent State Robotics 
 * Jared Butcher 3/1/2020
 * motorController.h
 * Control one or move (less than 10) BLH analog motor controllers
 * Only can receive feedback from one motor controller
 * Feedback must be an interrupt capable digital pin
*/

#ifndef _MOTOR_CONTROLLER_2_
#define _MOTOR_CONTROLLER_2_

#include <stdint.h>
#include "Arduino.h"

#define ABS(a) (((a) < 0)? (a) * -1 : (a))

class Motor{
public:
    /* Control one or move (less than 10) BLH analog motor controllers
     * Only can receive feedback from one motor controller
     * 
     * startStopPin - pin no 11, on to move normaly, off to decelerate at manually set rate
     * runBreakPin - pin no 10, on to run motor, off to stop as fast as mechanicly posible (dangerous)
     * directionPin - pin no 9, on for CW, off for CCW
     * magnitudePin - pin VM, 0 - 5v motor power
     * feedbackPin - pin DOUT0, pules high for 0.3ms 30 times per rotation, interrupt capable digital pin
     * pulsesPerRotation - 30 * gear ratio of motor
     * invertDirection - if true invert directionPin
    */
    Motor(uint8_t startStopPin, uint8_t runBreakPin, uint8_t directionPin, 
    uint8_t magnitudePin, uint8_t feedbackPin, uint16_t pulsesPerRotation, bool invertDirection);
    /*Command the movement of the motor
     * forward - CW roate if true, CCW if false
     * level - 0-255, speed to go at
    */
    void command(bool CW, uint8_t level);
    uint16_t getPosition(); //In minutes
    int32_t getDeltaPosition(); //Change in position in minutes sense last call
    void onFeedbackPulse();
private:
    uint8_t startStopPin, runBreakPin, directionPin, magnitudePin, feedbackPin, currentLevel;
    uint16_t pulsesPerRotation, currentPosition;
    int32_t deltaPosition;
    bool invertDirection, currentDirection;
};
#endif