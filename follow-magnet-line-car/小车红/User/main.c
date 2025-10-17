#include "stm32f10x.h" // Device header
#include "Delay.h"
#include "OLED.h"
#include "Motor.h"
#include "Key.h"
#include "AD.h"
#include "Timer.h"
#include "RFID.h"
#include "Avoid.h"
#include "Serial.h"

extern int lamp_flag[];
int Stop;
 
 
uint8_t KeyNum;
int8_t Speed = 40;
// uint16_t AD0, AD1, AD2, AD3;
uint16_t Num;
uint8_t AD_Flag=0;
uint8_t Control_Flag=0;
int16_t TurnPWM;

uint8_t RFID_Flag=0;
uint8_t Avoid_Flag=0;
uint8_t Avoid_result=0;

char lcd_string [20];

uint16_t TIM_1s=0;
uint8_t TIM_20ms=0;

int main(void)
{
	OLED_Init();
	Motor_Init();
	AD_Init();
	Timer_Init();
	RFID_Init();
	Avoid_Init();
	Serial_Init();
	
//	OLED_ShowChinese(24,0,"é”¦åŸŽç‰©è”ç½‘");
//	OLED_ShowChinese(24,32,"å·");
//	OLED_ShowString(40,32," AQ123P",8);
//	OLED_Update();
	
	// Key_Init();
	while (1)
	{
//		OLED_ShowNum(1,1,Serial,1);
//		OLED_ShowNum(2,1,Colour,1);
//		OLED_ShowNum(3,1,Time,2);
//		OLED_ShowNum(4,1,lamp_flag[0],1);
//		OLED_ShowNum(4,3,lamp_flag[1],1);
//		OLED_ShowNum(4,5,lamp_flag[2],1);
//		OLED_ShowNum(4,8,Stop,1);
			UART_Proc();	

		if(lamp_flag[0]==1)
		{

			if(Serial==3&&Colour==0)
			{
				  Stop=1;
				  Serial=0;
				  Colour=0;
			}
				if(Serial==3&&(Colour==1||Colour==2))
			{
				  Stop=0;
				  Serial=0;
				  Colour=0;				
				  lamp_flag[0]=0;
			}				
		}
		if(lamp_flag[1]==1)
		{

			if((Serial==2||Serial==1)&&Colour==0)
			{
				  Stop=1;
				  Serial=0;
				  Colour=0;
			}
				if((Serial==2||Serial==1)&&(Colour==1||Colour==2))
			{
				  Stop=0;
				  Serial=0;
				  Colour=0;
				  lamp_flag[1]=0;
			}				
		}
		if(lamp_flag[2]==1)
		{

			if(Serial==4&&Colour==0)
			{
				  Stop=1;
				  Serial=0;
				  Colour=0;
			}
				if(Serial==4&&(Colour==1||Colour==2))
			{
				  Stop=0;
				  Serial=0;
				  Colour=0;
				  lamp_flag[2]=0;
			}				
		}
		
		
		if(AD_Flag==1)
		{
			AD_GetAll();
			AD_Normalnize();
//			if(Track_Mode==1&&(Track_Turn%3==0))//0 ×ßÄÚÈ¦
//			{
//				error= -40;
//			}
//				if(Track_Mode==1&&(Track_Turn%3==2))//0 ×ßÄÚÈ¦
//			{
//				error= 60;
//			}
			if(Track_Mode==1)
			{
				if((RFID_Handle_Track()-1)==0)//×ó
					error= 80;
				if((RFID_Handle_Track()-1)==1)//ÖÐ
					error= 20;
				if((RFID_Handle_Track()-1)==2)//ÓÒ
					error= -40;
				
			}
			
			else {
			error=((AD1-AD2)*100/(AD1+AD2));
			}
			
			TurnPWM=PlacePID(error);
			AD_Flag=0;
		}
		

		if(Control_Flag==1)
		{
			

			if(Stop_Flag==1||Avoid_result!=0||  Stop==1)
			{
				Motor_Control(0,0);
			}
			 else if(lamp_flag[0]==1||lamp_flag[1]==1||lamp_flag[2]==1)
			 {
         	Motor_Control(Speed-TurnPWM-20,Speed+TurnPWM-20);
			 }				 
			else{
			Motor_Control(Speed-TurnPWM,Speed+TurnPWM);
			//Motor_Control(30,30);
				}
			
			Control_Flag=0;
		}
		
		if(RFID_Flag==1)
		{
			RFID_GetID();
			//RFID_Get();
			RFID_Handle();	

			
			
			
			RFID_Flag=0;
		}
		
		if(Avoid_Flag==1)
		{				
			Avoid_result=Avoid_Get();
			
		}
		
		
		

		sprintf(lcd_string, "%d %d %d", txBuffer[5],txBuffer[6],txBuffer[7]);
		OLED_ShowString(0,0,(char*)lcd_string,8);
		 OLED_Update();
		
// 		 OLED_ShowNum(1, 1, AD0, 3);
// 		 OLED_ShowNum(2, 1, AD1, 3);
// 		 OLED_ShowNum(3, 1, AD2, 3);
// 		 OLED_ShowNum(4, 1, AD3, 3);
		

// //		 OLED_ShowNum(1, 5, AD0_real, 4);
// //		 OLED_ShowNum(2, 5, AD1_real, 4);
// //		 OLED_ShowNum(3, 5, AD2_real, 4);
// //		 OLED_ShowNum(4, 5, AD3_real, 4);
		 
		
		
// 		 OLED_ShowSignedNum(1, 5, LastError, 4);
// 		 OLED_ShowSignedNum(2, 5,error-LastError , 4);
// //		 OLED_ShowSignedNum(2, 5,((-25)-(-23))*0.5 , 4);

// 		 OLED_ShowSignedNum(1, 12, error, 4);
// 		 OLED_ShowSignedNum(2, 12,TurnPWM , 4);
//		OLED_ShowNum(2, 12, Track_Mode, 3);
//		OLED_ShowNum(3, 12, Stop_Flag, 1);
//OLED_ShowNum(3, 12, Track_Turn, 3);
		
// 		OLED_ShowNum(4, 12, Num, 5);//Avoid_result
		
//		 OLED_ShowNum(2, 5, avoid_l, 3);
//		 OLED_ShowNum(3, 5, RFID_Handle_Track(), 3);
		 
//		 OLED_ShowNum(4, 5, Avoid_result, 3);
// 		 OLED_ShowSignedNum(4, 12, Speed, 3);

		 

		//		KeyNum = Key_GetNum();
		//		if (KeyNum == 1)
		//		{
		//			Speed += 20;
		//			if (Speed > 100)
		//			{
		//				Speed = -100;
		//			}
		//		}

	}
}

void TIM2_IRQHandler(void)//10ms
{
	if (TIM_GetITStatus(TIM2, TIM_IT_Update) == SET)
	{
		TIM_20ms++;
		TIM_1s++;
		if(TIM_1s==300) 
			{
			Stop_Flag=0;
			TIM_1s=0;
			}
		
		if(TIM_20ms==80) 
		{
			Track_Mode=0;
//			Avoid_result=0;
		  TIM_20ms=0;
		
		}
		
		Avoid_Flag=1;

		Num++;

		AD_Flag=1;

		Control_Flag=1;
		
		RFID_Flag=1;
		
		


		TIM_ClearITPendingBit(TIM2, TIM_IT_Update);
	}
}
