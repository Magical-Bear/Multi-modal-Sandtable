#ifndef __MOTOR_H
#define __MOTOR_H

void Motor_Init(void);
void Motor1_SetSpeed(int8_t Speed);
void Motor2_SetSpeed(int8_t Speed);
void Motor_Control(int16_t Speed_L, int16_t Speed_R);
int16_t PlacePID(int16_t error);

extern float KP;
extern float KD;
extern int16_t LastError;

#endif
