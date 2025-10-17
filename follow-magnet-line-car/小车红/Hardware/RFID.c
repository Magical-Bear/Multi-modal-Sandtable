#include "RFID.h"
#include "Motor.h"
#include "Delay.h"

//SPI引脚初始化
void GPIO_Config_Init(void)
{
///////////////SPI1  CS引脚初始化////////////////////////////////////////////
	GPIO_InitTypeDef  GPIO_InitStructure;

	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);	 //使能PA端口时钟使能
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_4;				 //PA4 端口配置
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_Out_PP; //推挽输出
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;	//IO口速度为50MHz
	GPIO_Init(GPIOA, &GPIO_InitStructure);					 //根据设定参数初始化GPIOA4
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_AFIO, ENABLE);	 //AF时钟使能

///////////////SPI1引脚初始化/////////////////////////////////////////////////
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_5 | GPIO_Pin_7;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_6;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

}

void RCC_Configuration(void)
{
  /* PCLK2 = HCLK/2 */
  RCC_PCLK2Config(RCC_HCLK_Div2); 
  RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1 | RCC_APB2Periph_GPIOA , ENABLE);
}

//SPI1配置初始化
void SPI_Config_init(void)
{
	SPI_InitTypeDef   SPI_InitStructure;
	SPI_InitStructure.SPI_Direction = SPI_Direction_2Lines_FullDuplex;
  SPI_InitStructure.SPI_Mode = SPI_Mode_Master;
  SPI_InitStructure.SPI_DataSize = SPI_DataSize_8b;
  SPI_InitStructure.SPI_CPOL = SPI_CPOL_Low;
  SPI_InitStructure.SPI_CPHA = SPI_CPHA_1Edge;
  SPI_InitStructure.SPI_NSS = SPI_NSS_Soft;
  SPI_InitStructure.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_4;
  SPI_InitStructure.SPI_FirstBit = SPI_FirstBit_MSB;
  SPI_InitStructure.SPI_CRCPolynomial = 7;
  SPI_Init(SPI1, &SPI_InitStructure);
	SPI_Cmd(SPI1, ENABLE);

}

uint8_t retstr[10];
// char number to string hex (FF) (Only big letters!)
void char_to_hex(uint8_t data) {
	uint8_t digits[] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
	
	if (data < 16) {
		retstr[0] = '0';
		retstr[1] = digits[data];
	} else {
		retstr[0] = digits[(data & 0xF0)>>4];
		retstr[1] = digits[(data & 0x0F)];
	}
}

void RFID_Init(void)
{
 GPIO_Config_Init();
 RCC_Configuration();
 SPI_Config_init();
 MFRC522_Init();
}

uint8_t	txBuffer[18] = "00000000";
uint8_t		str[MFRC522_MAX_LEN];	
uint8_t 	k;
uint8_t 	i;
uint8_t 	j;
uint8_t 	b;
uint8_t		lastID[4];
void RFID_GetID(void)
{
	if (!MFRC522_Request(PICC_REQIDL, str)) {//寻卡
			 if (!MFRC522_Anticoll(str)) {//获得卡序列号
			 	j = 0;
			 	b = 0;
			 	for (i=0; i<4; i++) if (lastID[i] != str[i]) j = 1;								// 如果读到ID不同，需要显示更新
			 	if (j) {
				
			 		for (i=0; i<4; i++) lastID[i] = str[i];
			 		for (i=0; i<4; i++) {
			 			char_to_hex(str[i]);
			 			txBuffer[b] = retstr[0];//序列号存在txBuffer中
			 			b++;
			 			txBuffer[b] = retstr[1];
			 			b++;
			 		}										
			 	}

			 }
		}

}

int lamp_flag[3];
	
uint8_t Stop_Flag=0;
uint8_t Track_Mode=0;
uint8_t Track_Turn=0;
void RFID_Handle(void)
{
			if(txBuffer[5]==66&&txBuffer[6]==70&&txBuffer[7]==69)//停车场
			{
				
			Stop_Flag=1;
			txBuffer[5]=0;
			txBuffer[6]=0;
			txBuffer[7]=0;
			}
			
			if(txBuffer[5]==53&&txBuffer[6]==69&&txBuffer[7]==57)//停车场
			{
				
			Stop_Flag=1;
			txBuffer[5]=0;
			txBuffer[6]=0;
			txBuffer[7]=0;
			}
			
			if(txBuffer[5]==51&&txBuffer[6]==65&&txBuffer[7]==56)//路灯5
			{
				 lamp_flag[2]=1;
				 txBuffer[5]=0;
				 txBuffer[6]=0;
				 txBuffer[7]=0;
			}
			
			if((txBuffer[5]==66||txBuffer[5]==51)&&(txBuffer[6]==67||txBuffer[6]==68)&&(txBuffer[7]==55||txBuffer[7]==49))//路灯3 0
			{
				 lamp_flag[0]=1;
				 txBuffer[5]=0;
				 txBuffer[6]=0;
				 txBuffer[7]=0;
			}
			
			if((txBuffer[5]==56||txBuffer[5]==57)&&txBuffer[6]==67&&(txBuffer[7]==50||txBuffer[7]==69))//路灯1 2
			{
				 lamp_flag[1]=1;
				 txBuffer[5]=0;
				 txBuffer[6]=0;
				 txBuffer[7]=0;
			}
			
			if(txBuffer[5]==49&&txBuffer[6]==51&&txBuffer[7]==68)//交叉路口 旧txBuffer[5]==49&&txBuffer[6]==51&&txBuffer[7]==68；新txBuffer[5]==68&&txBuffer[6]==65&&txBuffer[7]==49
			{
				
				Motor_Control(60,30);
				delay_ms(200);
			txBuffer[5]=0;
			txBuffer[6]=0;
			txBuffer[7]=0;

			}
			
			if(txBuffer[5]==51&&txBuffer[6]==65&&txBuffer[7]==51)//交叉路口 旧txBuffer[5]==49&&txBuffer[6]==51&&txBuffer[7]==68；新txBuffer[5]==68&&txBuffer[6]==65&&txBuffer[7]==49
			{
				
				Motor_Control(40,40);
				delay_ms(300);
			txBuffer[5]=0;
			txBuffer[6]=0;
			txBuffer[7]=0;
				
			}
			


}

uint8_t RFID_Handle_Track(void)
{
		uint8_t result=0;
	
			if(txBuffer[5]==49&&txBuffer[6]==51&&txBuffer[7]==68)//交叉路口
			{
				Track_Mode=1;
				Track_Turn++;	
			txBuffer[5]=0;
			txBuffer[6]=0;
			txBuffer[7]=0;

			}

			
			if(Track_Turn%4==1)
			{
				result=1;//左
			}
			
			if(Track_Turn%4==2)
			{
				result=2;//中
			}
			if(Track_Turn%4==3)
			{
				result=3;//右
			}
			
			return result;


}

