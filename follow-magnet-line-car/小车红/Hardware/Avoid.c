#include "Avoid.h"



void Avoid_Init(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
	
	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_6;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOB, &GPIO_InitStructure);
}

uint8_t Avoid_Get(void)
{
	uint8_t result = 0;
	if (GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_5) == 0)
	{		
		result = 1;
	}
	if (GPIO_ReadInputDataBit(GPIOB, GPIO_Pin_6) == 0)
	{
		result = 2;
	}
	
	return result;
}

