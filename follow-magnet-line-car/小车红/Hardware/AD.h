#ifndef __AD_H
#define __AD_H

void AD_Init(void);
uint16_t AD_GetValue(uint8_t ADC_Channel);

void AD_GetAll(void);
void AD_Normalnize(void);
uint16_t cha_bi_he(float value1,float value2);
extern uint16_t AD0, AD1, AD2, AD3;
extern uint16_t AD0_real, AD1_real, AD2_real, AD3_real;

extern uint16_t AD0_MAX;
extern uint16_t AD1_MAX;
extern uint16_t AD2_MAX;
extern uint16_t AD3_MAX;

extern uint16_t AD0_MIN;
extern uint16_t AD1_MIN;
extern uint16_t AD2_MIN;
extern uint16_t AD3_MIN;

extern int16_t error;
#endif
