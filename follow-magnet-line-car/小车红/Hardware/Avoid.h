#ifndef __AVOID_H__
#define __AVOID_H__

#include "stm32f10x.h"                  // Device header

void Avoid_Init(void);

uint8_t Avoid_Get(void);

extern 	uint8_t avoid_l;
extern 	uint8_t avoid_r;
#endif
