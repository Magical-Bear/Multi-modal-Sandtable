# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()
import machine
import time
from umqttsimple import MQTTClient
import network
from machine import Timer, UART, Pin, PWM, time_pulse_us

uart_screen = UART(2, 115200)
uart_voice = UART(1, 9600, rx=Pin(2), tx=Pin(4))
servo_pin = Pin(5, Pin.OUT)
pwm = PWM(servo_pin, freq=50)

TRIG_PIN_IN = 13  # 替换为实际引脚编号
ECHO_PIN_IN = 12

TRIG_PIN_OUT = 14  # 替换为实际引脚编号
ECHO_PIN_OUT = 27

trig1 = Pin(TRIG_PIN_IN, Pin.OUT)
echo1 = Pin(ECHO_PIN_IN, Pin.IN)

trig2 = Pin(TRIG_PIN_OUT, Pin.OUT)
echo2 = Pin(ECHO_PIN_OUT, Pin.IN)

distance_in = -1
distance_out = -1  # 全局变量存储距离

triggle_distance_in = 16
triggle_distance_out = 25

buffer_in = []  # 存储最近 5 次 distance_in 的测量值
buffer_out = []  # 存储最近 5 次 distance_out 的测量值
BUFFER_SIZE = 5  # 缓冲区大小

gate_automatic_off = False
gate_time_count = 0

# 设置定时器，每隔100ms测量一次

weather_mapping = {
    "sun": bytes.fromhex("5AA5051001680000"),
    "cloud": bytes.fromhex("5AA5051001680001"),
    "flash": bytes.fromhex("5AA5051001680002"),
    "snow": bytes.fromhex("5AA5051001680003"),
    "rain": bytes.fromhex("5AA5051001680004"),
}

text_addr_mapping = {
    b'screen/welcome_text': "0000",
    b'screen/time_sync': "7002",
    b'screen1/gate': "001E",
    b'screen/weather_text': "003C",
    b'screen/weather': "0168",
    b'screen1/entrance': "00B4",
    b'screen1/exit': "00D2",
    b'screen/at_park': "00F0",
    b'screen1/car_plate': "012C",
    b'screen1/stop_time': "014A",
    b'screen1/car_inspect': "010E",
    b'screen1/environment_temperature': "005A",
    b'screen1/environment_humidity': "0078",
}

song_name_dict = {
    "小轿车": [0x01, 0.5],
    "一路顺风": [0x02, 1.0],
    "时": [0x03, 0.5],
    "未检测到入场记录": [0x04, 1.5],
    "成都锦城学院": [0x05, 1.0],
    "停车场": [0x06, 0.5],
    "本停车场已满": [0x07, 1.0],
    "停车总时长为": [0x08, 1.0],
    "0": [0x09, 0.5],
    "1": [0x0A, 0.5],
    "2": [0x0B, 0.5],
    "3": [0x0C, 0.5],
    "4": [0x0D, 0.5],
    "5": [0x0E, 0.5],
    "6": [0x0F, 0.5],
    "7": [0x10, 0.5],
    "8": [0x11, 0.5],
    "9": [0x12, 0.5],
    "十": [0x13, 0.5],
    "百": [0x14, 0.5],
    "点": [0x15, 0.5],
    "分": [0x16, 0.5],
    "秒": [0x17, 0.5],
    "年": [0x18, 0.5],
    "月": [0x19, 0.5],
    "日": [0x1A, 0.5],
    "星期": [0x1B, 0.5],
    "摄氏度": [0x1C, 0.5],
    "百分之": [0x1D, 0.5],
    "现在时间是": [0x1E, 1.0],
    "温度是": [0x1F, 0.5],
    "湿度是": [0x20, 0.5],
    "叮咚": [0x21, 0.5],
    "整": [0x22, 0.5],
    "今天是": [0x23, 0.5],
    "上午": [0x24, 0.5],
    "下午": [0x25, 0.5],
    "晚上": [0x26, 0.5],
    "负": [0x27, 0.5],
    "开智电子提醒您": [0x28, 1.5],
    "欢迎光临": [0x29, 0.5],
    "超声波测距中": [0x2A, 1.0],
    "最近的障碍物距离是 ": [0x2B, 1.5],
    "厘米": [0x2C, 0.5],
    "米": [0x2D, 0.5],
    "号": [0x2E, 0.5],
    "派是": [0x2F, 0.5],
    "欢迎回来": [0x30, 0.5],
    "您的卡号是 ": [0x31, 1.0],
    "欢迎光临 ": [0x32, 0.5],
    "请出示您的通行卡": [0x33, 1.5],
    "请进": [0x34, 0.5],
    "天黑了请问是否开启自动夜灯模式": [0x35, 2],
    "开启成功": [0x36, 0.5],
    "天亮了关灯": [0x37, 1.0],
    "车牌号": [0x38, 0.5],
    "车型": [0x39, 0.5],
    "公交车": [0x3A, 0.5],
    "进场车": [0x3B, 0.5],
    "跑车": [0x3C, 0.5]
}


def measure_distance1(timer_in):
    global distance_in, distance_out

    # 测量第一个传感器的距离
    trig1.value(0)
    time.sleep_us(2)
    trig1.value(1)
    time.sleep_us(10)
    trig1.value(0)
    duration1 = time_pulse_us(echo1, 1, 30000)

    if duration1 < 0:
        distance_in = -1
    else:
        distance_in = (duration1 * 0.0343) / 2

    buffer_in.append(distance_in)
    if len(buffer_in) > BUFFER_SIZE:
        buffer_in.pop(0)

    # 测量第二个传感器的距离
    trig2.value(0)
    time.sleep_us(2)
    trig2.value(1)
    time.sleep_us(10)
    trig2.value(0)
    duration2 = time_pulse_us(echo2, 1, 30000)

    if duration2 < 0:
        distance_out = -1
    else:
        distance_out = (duration2 * 0.0343) / 2

    buffer_out.append(distance_out)
    if len(buffer_out) > BUFFER_SIZE:
        buffer_out.pop(0)

    trigger_event()


def trigger_event():
    global triggle_distance_in, triggle_distance_out
    in_count = sum(1 for d in buffer_in if d != -1 and d <= triggle_distance_in)
    out_count = sum(1 for d in buffer_out if d != -1 and d <= triggle_distance_out)

    if in_count >= 2:
        client.publish(b'screen1/car_in', str(min(buffer_in)))
    if out_count >= 2:
        client.publish(b'screen1/car_out', str(min(buffer_out)))


def turn_to_90():
    pwm.duty_u16(3277)  # 1.5ms脉宽 (50Hz下对应大约90度)
    time.sleep(1)  # 等待舵机转动完成


# 归零
def turn_to_0():
    pwm.duty_u16(6554)  # 1ms脉宽 (50Hz下对应0度)
    time.sleep(1)  # 等待舵机转动完成


def receive_gb2312_to_uart(str_encode, addr):
    prefix = bytes.fromhex("5AA5")
    str_encode_len = len(str_encode)
    frame_len = str_encode_len + 5
    prefix += frame_len.to_bytes(1, 'big') + bytes.fromhex("10") + addr + str_encode + bytes.fromhex("0000")
    return prefix


def subscribe_list():
    client.subscribe('screen/weather')
    client.subscribe('network/temp_info')  # 订阅温度信息
    client.subscribe('network/humi_info')
    client.subscribe('screen1/voice_message')  # 订阅温度信息
    client.subscribe('screen1/gate_status')  # 订阅温度信息
    client.subscribe('screen1/triggle_in_distance')
    client.subscribe('screen1/triggle_out_distance')
    for k, v in text_addr_mapping.items():
        client.subscribe(k.decode("utf-8"))


def do_connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        # 网络未连接
        wlan.connect(ssid, password)
        i = 1
        while not wlan.isconnected():
            print(f"正在连接网络：{ssid}...{i}s")
            time.sleep(1)
            i += 1
    print('网络已连接，IP:', wlan.ifconfig()[0])


def open_gate():
    global gate_automatic_off
    if uart_screen.any():  # 检查是否有数据接收
        received_data = uart_screen.read()
        turn_to_90()
        gate_automatic_off = True


def sub_cb(topic, msg):
    global triggle_distance_in, triggle_distance_out
    print(topic, msg)
    if topic == b'screen/weather':
        weather = msg.decode('utf-8')  # 解码消息
        if weather in weather_mapping:
            uart_screen.write(weather_mapping[weather])  # 发送到 UART
    elif topic == b'network/humi_info':
        temp = int(msg.decode("utf-8").split("_")[1])
        prefix = bytes.fromhex("5AA50510016B00")
        prefix += temp.to_bytes(1, 'big')
        uart_screen.write(prefix)
    elif topic == b'network/temp_info':
        temp = int(msg.decode("utf-8").split("_")[1])
        prefix = bytes.fromhex("5AA50510016A00")
        prefix += temp.to_bytes(1, 'big')
        uart_screen.write(prefix)
    elif topic == b'screen1/voice_message':
        play_list = eval(msg.decode("utf-8"))
        for voice_token in play_list:
            prefix = bytes.fromhex("7EFF06030000")
            voice_info_list = song_name_dict.get(voice_token)
            if voice_info_list:
                index = voice_info_list[0].to_bytes(1, 'big')
                prefix += index + bytes.fromhex("EF")
                uart_voice.write(prefix)
                print(prefix)
                time.sleep(voice_info_list[1])
            else:
                print(f"Text '{text}' not found in song_name_dict")
    elif topic == b'screen1/gate_status':
        status = int(msg.decode('utf-8'))
        if status:
            turn_to_90()  # 转90度
        else:
            turn_to_0()  # 转90度
    elif topic == b'screen1/triggle_in_distance':
        triggle_distance_in = int(msg.decode('utf-8'))

    elif topic == b'screen1/triggle_out_distance':
        triggle_distance_out = int(msg.decode('utf-8'))

    elif topic == b'screen/time_sync':
        text = msg.decode("utf-8")
        try:
            text = eval(text)
            prefix = bytes.fromhex("5AA509107002")
            for item in text:
                prefix += bytes.fromhex("00") + item.to_bytes(1, 'big')
            uart_screen.write(prefix)
        except:
            pass

    elif topic in text_addr_mapping:
        text = msg.decode("utf-8")
        try:
            addr = text_addr_mapping.get(topic)
            str_encode = bytes.fromhex(text)
            prefix = receive_gb2312_to_uart(str_encode, bytes.fromhex(addr))
            uart_screen.write(prefix)
        except:
            pass


def timer_task(self):
    global gate_automatic_off, gate_time_count
    try:
        subscribe_list()
        open_gate()
        if gate_automatic_off:
            gate_time_count += 1
        if gate_time_count == 25:
            turn_to_0()
            gate_automatic_off = False
            gate_time_count = 0
    except:
        pass


turn_to_0()
do_connect('iot', 'c108c108')
client = MQTTClient("ESP32_Screen1", "192.168.124.10", 1883)  # ID 地址 端口
client.connect()  # 建立连接
client.set_callback(sub_cb)
timer = Timer(0)
timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_task)
timer_in = Timer(-1)
timer_in.init(period=100, mode=Timer.PERIODIC, callback=measure_distance1)
while True:
    pass


















