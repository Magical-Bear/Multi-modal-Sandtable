#ifndef __RFID_H__
#define __RFID_H__

#include "stm32f10x.h"                  // Device header
#include "rc522.h"

//SPI引脚初始化
void GPIO_Config_Init(void);
void RCC_Configuration(void);
void SPI_Config_init(void);
void char_to_hex(uint8_t data);

void RFID_Init(void);
void RFID_GetID(void);
void RFID_Handle(void);

uint8_t RFID_Handle_Track(void);
extern uint8_t	txBuffer[18];

extern uint8_t Stop_Flag;
extern uint8_t Track_Mode;
extern uint8_t Track_Turn;
#endif
