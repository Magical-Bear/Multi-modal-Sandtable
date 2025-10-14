import machine
import time
from umqttsimple import MQTTClient
import network
from machine import Timer, UART, Pin, PWM

# 定义红外避障模块的引脚
obstacle_pin_in = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
obstacle_pin_out = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)

# 记录红外避障模块状态和触发时间
obstacle_in_state = False
obstacle_in_released = True
obstacle_out_state = False
obstacle_out_released = True

# 初始化舵机
servo_pin = Pin(5, Pin.OUT)
pwm = PWM(servo_pin, freq=50)

# 初始化串口
uart_screen = UART(2, 115200)
uart_voice = UART(1, 9600, rx=Pin(2), tx=Pin(4))

# 其他配置和映射保持不变
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
    b'screen2/gate': "001E",
    b'screen/weather_text': "003C",
    b'screen/weather': "0168",
    b'screen2/entrance': "00B4",
    b'screen2/exit': "00D2",
    b'screen/at_park': "00F0",
    b'screen2/car_plate': "012C",
    b'screen2/stop_time': "014A",
    b'screen2/car_inspect': "010E",
    b'screen2/environment_temperature': "005A",
    b'screen2/environment_humidity': "0078",
}

song_name_dict = {
    "0": [0x01, 0.5],
    "1": [0x02, 0.5],
    "2": [0x03, 0.5],
    "3": [0x04, 0.5],
    "4": [0x05, 0.5],
    "5": [0x06, 0.5],
    "6": [0x07, 0.5],
    "7": [0x08, 0.5],
    "8": [0x09, 0.5],
    "9": [0x0A, 0.5],
    "十": [0x0B, 0.5],
    "百": [0x0C, 0.5],
    "点": [0x0D, 0.5],
    "分": [0x0E, 0.5],
    "秒": [0x0F, 0.5],
    "年": [0x10, 0.5],
    "月": [0x11, 0.5],
    "日": [0x12, 0.5],
    "星期": [0x13, 1],
    "摄氏度": [0x14, 1],
    "百分之": [0x15, 1],
    "现在时间是": [0x16, 2],
    "温度是": [0x17, 1],
    "湿度是": [0x18, 1],
    "叮咚": [0x19, 1],
    "整": [0x1A, 0.5],
    "今天是": [0x1B, 1],
    "上午": [0x1C, 1],
    "下午": [0x1D, 1],
    "晚上": [0x1E, 1],
    "负": [0x1F, 0.5],
    "开智电子提醒您": [0x20, 2.5],
    "欢迎光临": [0x21, 0.1],
    "超声波测距中": [0x22, 2],
    "最近的障碍物距离是": [0x23, 2.5],
    "厘米": [0x24, 1],
    "米": [0x25, 0.5],
    "号": [0x26, 0.5],
    "派是": [0x27, 1],
    "欢迎回来": [0x28, 1],
    "您的卡号是": [0x29, 2],
    "欢迎光临": [0x2A, 1],
    "请出示您的通行卡 ": [0x2B, 2.5],
    "请进": [0x2C, 1],
    "天黑了请问是否开启自动夜灯模式": [0x2D, 3],
    "开启成功": [0x2E, 1],
    "天亮了关灯": [0x2F, 2],
    "车牌号": [0x30, 1],
    "车型": [0x31, 1],
    "公交车": [0x32, 1],
    "进场车": [0x33, 1],
    "跑车": [0x34, 1],
    "小轿车": [0x35, 1],
    "一路顺风": [0x36, 1],
    "时": [0x37, 0.5],
    "未检测到入场记录": [0x38, 2.1],
    "成都锦城学院": [0x39, 1.6],
    "停车场": [0x3A, 1],
    "本停车场已满": [0x3B, 1.6],
    "停车总时长为": [0x3C, 1.6]
}


# 检查红外避障模块的状态并更新
def check_obstacle(obstacle_pin, state):
    return False if obstacle_pin.value() else True


# 检查两个红外避障模块的状态并更新
def check_obstacles():
    global obstacle_in_state, obstacle_in_released, obstacle_out_state, obstacle_out_released
    if obstacle_out_released and obstacle_in_released:
        obstacle_in_state = check_obstacle(obstacle_pin_in, obstacle_in_state)
        obstacle_out_state = check_obstacle(obstacle_pin_out, obstacle_out_state)
        if obstacle_in_state and obstacle_in_released:
            client.publish(b'screen2/car_in', str(10.2))
            obstacle_in_released = False

        if obstacle_out_state and obstacle_out_released:
            client.publish(b'screen2/car_out', str(12.2))
            obstacle_out_released = False


# 舵机控制函数
def turn_to_90():
    pwm.duty_u16(3277)  # 1.5ms脉宽 (50Hz下对应大约90度)
    time.sleep(1)  # 等待舵机转动完成


def turn_to_0():
    pwm.duty_u16(6554)  # 1ms脉宽 (50Hz下对应0度)
    time.sleep(1)  # 等待舵机转动完成


# MQTT相关函数保持不变
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
    client.subscribe('screen2/voice_message')  # 订阅温度信息
    client.subscribe('screen2/gate_status')  # 订阅温度信息
    client.subscribe('screen2/triggle_in_distance')
    client.subscribe('screen2/triggle_out_distance')
    client.subscribe('screen2/lock_released')
    for k, v in text_addr_mapping.items():
        client.subscribe(k.decode("utf-8"))


def do_connect(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
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
    global triggle_distance_in, triggle_distance_out, obstacle_out_released, obstacle_in_released
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
    elif topic == b'screen2/voice_message':
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
    elif topic == b'screen2/gate_status':
        status = int(msg.decode('utf-8'))
        if status:
            turn_to_90()  # 转90度
        else:
            turn_to_0()  # 转90度
    elif topic == b'screen2/triggle_in_distance':
        triggle_distance_in = int(msg.decode('utf-8'))

    elif topic == b'screen2/triggle_out_distance':
        triggle_distance_out = int(msg.decode('utf-8'))

    elif topic == b"screen2/lock_released":
        state = int(msg.decode('utf-8'))
        if state == 1:
            obstacle_out_released = True
        else:
            obstacle_in_released = True

    elif topic == b'screen/time_sync':
        text = msg.decode("utf-8")
        try:
            text = eval(text)
            prefix = bytes.fromhex("5AA50f107002")
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


# 初始化舵机位置
turn_to_0()
# 连接网络
do_connect('iot', 'c108c108')
# 初始化MQTT客户端
client = MQTTClient("ESP32_Screen2", "192.168.124.10", 1883)
client.connect()
client.set_callback(sub_cb)
# 初始化定时器
timer = Timer(0)
timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_task)

# 创建定时器对象，每100毫秒调用一次 check_obstacles 函数
obstacle_timer = machine.Timer(-1)
obstacle_timer.init(period=50, mode=machine.Timer.PERIODIC, callback=lambda t: check_obstacles())
# 主循环
while True:
    pass





