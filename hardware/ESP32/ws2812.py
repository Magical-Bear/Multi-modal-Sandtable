from machine import Pin, PWM
import time
import machine
import network
from umqttsimple import MQTTClient
import neopixel
import random


# 初始化NeoPixel对象
# np0 = neopixel.NeoPixel(machine.Pin(12), 30)
line_length_list = [90, 60, 60, 60, 60, 60]
pin_port_list = [12, 13, 14, 27, 26, 33]
np_list = [neopixel.NeoPixel(machine.Pin(pin_port_list[i]), line_length_list[i]) for i in range(len(pin_port_list))]
is_color_status = False


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect('iot', 'c108c108')
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())


def clear_all_light():
    for i, np_object in enumerate(np_list):
        clear_light(np_object, i)


def all_light(r):
    global is_color_status
    if r == 255:
        is_color_status = True
        rgb_model()
    elif r == 0:
        is_color_status = False
        clear_all_light()


def rgb_model():
    if is_color_status is True:
        r = random.randint(1, 255)
        g = random.randint(1, 255)
        b = random.randint(1, 255)
        for i in range(90):
            set_color(np_list[0], i, r, g, b)
            time.sleep(0.005)
        for i in range(60):
            set_color(np_list[1], 59 - i, r, g, b)
            set_color(np_list[2], i, r, g, b)
            set_color(np_list[3], i, r, g, b)
            set_color(np_list[4], i, r, g, b)
            time.sleep(0.005)
        for i in range(60):
            set_color(np_list[5], i, r, g, b)
            time.sleep(0.005)


def set_color(np, index, r, g, b):
    np[index] = (r, g, b)
    np.write()


def clear_light(np, index):
    line_len = line_length_list[index]
    for i in range(line_len):
        np[i] = (0, 0, 0)
    np.write()


def message_callback(topic, msg):
    print("Received message:", msg.decode())
    try:
        global is_color_status
        # 解析 id 和 state
        id_state = msg.decode().split('_')
        line_id = int(id_state[0])
        light_id = int(id_state[1])
        r, g, b = id_state[2].replace('[', '').replace("]", "").split(',')
        r, g, b = int(r), int(g), int(b)
        if line_id == 100:

            all_light(r)
        elif r >= 0:
            if is_color_status:
                clear_all_light()
                is_color_status = False
            set_color(np_list[line_id], light_id, r, g, b)
        elif r < 0:
            if is_color_status:
                clear_all_light()
                is_color_status = False
            clear_light(np_list[line_id], light_id)

    except (IndexError, ValueError) as e:
        print("Invalid message format:", e)
        return


if __name__ == "__main__":
    do_connect()
    clear_all_light()
    device_client_id = "ESP32-rgb"  # 替换为您的客户端ID
    c = MQTTClient(device_client_id, "192.168.124.10", 1883, keepalive=60)
    c.set_callback(message_callback)  # 设置消息回调函数
    c.connect()
    c.subscribe("network/rgb_light")

    start_time = time.time()
    while True:
        c.check_msg()  # 检查是否有消息并调用回调函数
        rgb_model()
        if time.time() - start_time >= 10:
            c.publish(b"network/alive", "True")
            start_time = time.time()







