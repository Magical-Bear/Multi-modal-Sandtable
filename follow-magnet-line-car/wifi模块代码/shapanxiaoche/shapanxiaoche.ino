#include <ArduinoMqttClient.h>  // 引入MQTT客户端库
#include <WiFiManager.h>        // 引入WiFi管理库
#include <ArduinoJson.h>        // 引入ArduinoJson库，用于处理JSON消息
#include <ESP8266WiFi.h>        // 本程序使用ESP8266WiFi库
 
const char* ssid     = "iot";      // 连接WiFi名（此处使用taichi-maker为示例）
                                            // 请将您需要连接的WiFi名填入引号中
const char* password = "c108c108";          // 连接WiFi密码（此处使用12345678为示例）
                                            // 请将您需要连接的WiFi密码填入引号中

WiFiClient wifiClient;           // 创建WiFi客户端对象
MqttClient mqttClient(wifiClient); // 创建MQTT客户端对象

const char broker[] = "192.168.124.10";  // 定义MQTT代理服务器的IP地址
int port = 1883;                         // MQTT代理服务器的端口号

const char inTopic[] = "network/traffic_info"; // 订阅的MQTT消息主题
String inputString = "";  // 用于存储接收到的MQTT消息

void setup() {
  // 初始化串口并等待端口打开
  Serial.begin(9600);  

 /*WiFiManager wifiManager;
    
  // 自动连接WiFi，若没有连接则启动热点
  wifiManager.autoConnect("AutoConnectAP");

  // 输出连接WiFi后的信息
  Serial.println(""); 
  Serial.print("ESP8266 Connected to ");
  Serial.println(WiFi.SSID());              // 输出连接的WiFi名称
  Serial.print("IP address:\t");
  Serial.println(WiFi.localIP());           // 输出ESP8266的IP地址 */

  WiFi.begin(ssid, password);                  // 启动网络连接
  //Serial.print("Connecting to ");              // 串口监视器输出网络连接信息
  //Serial.print(ssid);
  //Serial.println(" ...");  // 告知用户NodeMCU正在尝试WiFi连接
  
  int i = 0;                                   // 这一段程序语句用于检查WiFi是否连接成功
  while (WiFi.status() != WL_CONNECTED) {      // WiFi.status()函数的返回值是由NodeMCU的WiFi连接状态所决定的。 
    delay(1000);                               // 如果WiFi连接成功则返回值为WL_CONNECTED                       
    Serial.print(i++); 
    Serial.print(' ');      // 此处通过While循环让NodeMCU每隔一秒钟检查一次WiFi.status()函数返回值
  }                                            // 同时NodeMCU将通过串口监视器输出连接时长读秒。
                                               // 这个读秒是通过变量i每隔一秒自加1来实现的。
                                               
  Serial.println("");                          // WiFi连接成功后
  //Serial.println("Connection established!");   // NodeMCU将通过串口监视器输出"连接成功"信息。
  //Serial.print("IP address:    ");             // 同时还将输出NodeMCU的IP地址。这一功能是通过调用
  //Serial.println(WiFi.localIP());              // WiFi.localIP()函数来实现的。该函数的返回值即NodeMCU的IP地址。


  // 配置MQTT客户端
  mqttClient.setId("MQTT_FX_Client");    // 设置MQTT客户端ID
  mqttClient.setUsernamePassword("", ""); // 设置MQTT的用户名和密码（此处为空）

  // 尝试连接MQTT代理服务器
  //Serial.print("Attempting to connect to the MQTT broker: ");
  //Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    // 如果连接失败，输出错误信息并进入死循环
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());
    while (1);  // 进入死循环，程序不再执行
  }

  //Serial.println("You're connected to the MQTT broker!"); // 成功连接后输出信息
  //Serial.println();

  // 设置接收到消息时的回调函数
  mqttClient.onMessage(onMqttMessage);

  // 订阅MQTT主题
  //Serial.print("Subscribing to topic: ");
  //Serial.println(inTopic);
  //Serial.println();

  int subscribeQos = 1; // 设置订阅的QoS等级

  mqttClient.subscribe(inTopic, subscribeQos); // 订阅主题

  //Serial.print("Waiting for messages on topic: ");
  //Serial.println(inTopic);
  //Serial.println();
}

void loop() {
  mqttClient.poll();  // 检查是否有MQTT消息到达
}

// MQTT消息回调函数
void onMqttMessage(int messageSize) {
  // 接收到消息时打印消息的主题及相关信息

  // 使用Stream接口打印消息内容
  while (mqttClient.available()) {
    char inChar = (char)mqttClient.read(); // 读取MQTT消息中的字符
    inputString += inChar;  // 将字符追加到inputString中

    // 如果接收到的消息大小等于预期的消息大小，则处理消息
    if (inputString.length() == messageSize) {
     /* DynamicJsonDocument json_msg(1024);  // 创建JSON文档，用于解析接收到的消息
      DynamicJsonDocument json_item(1024); // 创建JSON文档，用于解析嵌套的内容

      // 解析接收到的JSON消息
      deserializeJson(json_msg, inputString);*/

       Serial.println('@'+inputString);

      inputString = "";  // 清空inputString，为下一次接收消息做准备
    }
  }
}