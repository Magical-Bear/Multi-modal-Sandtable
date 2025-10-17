#include "stm32f10x.h"                  // Device header
#include "PWM.h"

/*
PB0,PB1---·½ÏòÒý½Å




*/


void Motor_Init(void)
{
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOB, ENABLE);
	
	GPIO_InitTypeDef GPIO_InitStructureB;
	
	GPIO_InitStructureB.GPIO_Mode = GPIO_Mode_Out_PP;
	GPIO_InitStructureB.GPIO_Pin = GPIO_Pin_10 | GPIO_Pin_11;
	GPIO_InitStructureB.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOB, &GPIO_InitStructureB);
	
	GPIO_InitTypeDef GPIO_InitStructureA;
	GPIO_InitStructureA.GPIO_Mode = GPIO_Mode_Out_PP;
	GPIO_InitStructureA.GPIO_Pin = GPIO_Pin_11 | GPIO_Pin_12;
	GPIO_InitStructureA.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructureA);
	
	PWM_Init();
}

void Motor1_SetSpeed(int8_t Speed)
{
	if (Speed >= 0)
	{
		GPIO_SetBits(GPIOB, GPIO_Pin_10);
		GPIO_ResetBits(GPIOB, GPIO_Pin_11);
		PWM_SetCompare3(Speed);

	}
	else
	{
		GPIO_ResetBits(GPIOB, GPIO_Pin_10);
		GPIO_SetBits(GPIOB, GPIO_Pin_11);
		PWM_SetCompare3(-Speed);

	}
}

void Motor2_SetSpeed(int8_t Speed)
{
	if (Speed >= 0)
	{
		GPIO_SetBits(GPIOA, GPIO_Pin_11);
		GPIO_ResetBits(GPIOA, GPIO_Pin_12);

		PWM_SetCompare4(Speed);
	}
	else
	{
		GPIO_ResetBits(GPIOA, GPIO_Pin_11);
		GPIO_SetBits(GPIOA, GPIO_Pin_12);

		PWM_SetCompare4(-Speed);
	}
}

void Motor_Control(int16_t Speed_L, int16_t Speed_R)
{
	Motor1_SetSpeed(Speed_L);
	Motor2_SetSpeed(-Speed_R);
}

//float KP=1.0;
//float KD=0.2;

float KP=0.5;
float KD=0.1;
int16_t LastError=0;

int16_t PlacePID(int16_t error)
{
    int16_t Actual;

    Actual = ( KP*error ) + KD* (error - LastError);

    LastError = error;

    return Actual;
}


