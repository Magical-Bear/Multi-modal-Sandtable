import machine
import time
from umqttsimple import MQTTClient
import network
from machine import Timer, UART, Pin

uart_screen = UART(2, 115200)
uart_voice = UART(1, 9600, rx=Pin(2), tx=Pin(4))

light_status_list = [False, False, False, False, False, False, False, False]
traffic_light_status = {}
traffic_light_init_status = [0, 0, 0]

light_mapping = {
    0: {
        True: bytes.fromhex("5AA5051000240001"),
        False: bytes.fromhex("5AA5051000240000")
    },
    1: {
        True: bytes.fromhex("5AA5051000280001"),
        False: bytes.fromhex("5AA5051000280000")
    },
    2: {
        True: bytes.fromhex("5AA5051000250001"),
        False: bytes.fromhex("5AA5051000250000")
    },
    3: {
        True: bytes.fromhex("5AA5051000290001"),
        False: bytes.fromhex("5AA5051000290000")
    },
    4: {
        True: bytes.fromhex("5AA5051000260001"),
        False: bytes.fromhex("5AA5051000260000")
    },
    5: {
        True: bytes.fromhex("5AA50510002A0001"),
        False: bytes.fromhex("5AA50510002A0000")
    },
    6: {
        True: bytes.fromhex("5AA5051000270001"),
        False: bytes.fromhex("5AA5051000270000")
    },
    7: {
        True: bytes.fromhex("5AA50510002B0001"),
        False: bytes.fromhex("5AA50510002B0000")
    }
}

traffic_light_dict = {
    0: {
        0: bytes.fromhex("5AA50510001E0000"),
        1: bytes.fromhex("5AA50510001E0002"),
        2: bytes.fromhex("5AA50510001E0001")
    },
    1: {
        0: bytes.fromhex("5AA50510001F0000"),
        1: bytes.fromhex("5AA50510001F0002"),
        2: bytes.fromhex("5AA50510001F0001")
    },
    2: {
        0: bytes.fromhex("5AA5051000200000"),
        1: bytes.fromhex("5AA5051000200002"),
        2: bytes.fromhex("5AA5051000200001")
    },
}

traffic_light_countdown_dict = {
    0: bytes.fromhex("5AA50510002100"),
    1: bytes.fromhex("5AA50510002200"),
    2: bytes.fromhex("5AA50510002300")
}

enter_count = 0


def update_strip_status(msg):
    global light_status_list
    try:
        id_state = msg.split('_')
        line_id = int(id_state[0])
        light_id = int(id_state[1])
        r, g, b = id_state[2].replace('[', '').replace("]", "").split(',')
        r, g, b = int(r), int(g), int(b)
        if line_id == 100 and r == 255:
            uart_screen.write(light_mapping[7][True])
            light_status_list[7] = True
        elif line_id == 100 and r == 0:
            uart_screen.write(light_mapping[7][False])
            light_status_list[7] = False
    except:
        pass


MAX_DATA_LENGTH = 8  # 或根据需要设置最大数据长度
TIMEOUT = 0.1  # 超时设置，单位：秒


# 接收数据的循环
def receive_data():
    global light_status_list
    received_data = b''  # 初始化空字节串

    start_time = time.time()  # 记录开始时间

    while True:
        if uart_screen.any():  # 检查是否有数据接收
            chunk = uart_screen.read()  # 读取当前数据
            received_data += chunk  # 累加数据

        # 检查接收数据是否已满或超时
        if len(received_data) >= MAX_DATA_LENGTH or (time.time() - start_time) > TIMEOUT:
            break  # 数据接收完成或超时，退出循环
    # 打印接收到的数据长度和内容
    if len(received_data) != 8:
        return
    int_val = int.from_bytes(received_data[7:], "big")
    if int_val < 32 or int_val > 39:
        return
    index = int_val - 32
    light_status_list[index] = not light_status_list[index]
    if index <= 6:
        status = int(light_status_list[index])
        client.publish(b'network/light', f"{index}_{status}")
    elif index == 7:
        if light_status_list[index]:
            client.publish(b'network/rgb_light', f"100_0_[255, 0, 0]")
        else:
            client.publish(b'network/rgb_light', f"100_0_[0, 0, 0]")


def parser_traffic_lights(msg):
    global traffic_light_init_status
    group, color, countdown = [int(item) for item in msg.split("_")]
    countdown = 40 if countdown > 40 else countdown
    if group == 4:
        if color != traffic_light_init_status[0]:
            light_picture = traffic_light_dict[0][color]
            uart_screen.write(light_picture)
            traffic_light_init_status[0] = color
        bytes = countdown.to_bytes(1, 'big')
        uart_screen.write(traffic_light_countdown_dict[0] + bytes)
    elif group in [1, 2]:
        if color != traffic_light_init_status[1]:
            light_picture = traffic_light_dict[1][color]
            uart_screen.write(light_picture)
            traffic_light_init_status[1] = color
        bytes = countdown.to_bytes(1, 'big')
        uart_screen.write(traffic_light_countdown_dict[1] + bytes)
    elif group in [0, 3]:
        if color != traffic_light_init_status[2]:
            light_picture = traffic_light_dict[2][color]
            uart_screen.write(light_picture)
            traffic_light_init_status[2] = color
        bytes = countdown.to_bytes(1, 'big')
        uart_screen.write(traffic_light_countdown_dict[2] + bytes)


def update_icon(msg):
    global light_status_list
    try:
        light_object = [int(item) for item in msg.split("_")]
        operator = bool(light_object[1])
        if 0 <= light_object[0] < 7:
            light_status_list[light_object[0]] = operator
            uart_screen.write(light_mapping[light_object[0]][operator])
    except:
        pass


def receive_gb2312_to_uart(str_encode, addr):
    prefix = bytes.fromhex("5AA5")
    str_encode_len = len(str_encode)
    frame_len = str_encode_len + 5
    prefix += frame_len.to_bytes(1, 'big') + bytes.fromhex("10") + addr + str_encode + bytes.fromhex("0000")
    return prefix


def subscribe_list():
    client.subscribe('network/light')
    client.subscribe('network/rgb_light')
    client.subscribe('network/traffic_info')
    client.subscribe('screen/traffic_boardcast')


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


def sub_cb(topic, msg):
    global enter_count
    enter_count += 1
    msg = msg.decode("utf-8")
    # print(topic, msg)
    if topic == b'network/light':
        update_icon(msg)
    elif topic == b'network/rgb_light':
        update_strip_status(msg)
    elif topic == b'network/traffic_info':
        parser_traffic_lights(msg)
    elif topic == b'screen/traffic_boardcast':
        try:
            addr = "002C"
            str_encode = bytes.fromhex(msg)
            print(str_encode)
            prefix = receive_gb2312_to_uart(str_encode, bytes.fromhex(addr))
            uart_screen.write(prefix)
        except:
            pass


def timer_task(self):
    client.publish(b'screen3/on_live', f"1")
    subscribe_list()


do_connect('iot', 'c108c108')
client = MQTTClient("ESP32_Screen3", "192.168.124.10", 1883)  # ID 地址 端口
for i in range(len(light_mapping)):
    uart_screen.write(light_mapping[i][False])

client.connect()  # 建立连接
client.set_callback(sub_cb)
timer = Timer(0)
timer.init(period=2000, mode=Timer.PERIODIC, callback=timer_task)
subscribe_list()
while True:
    # parser_serial_receive()
    receive_data()





















