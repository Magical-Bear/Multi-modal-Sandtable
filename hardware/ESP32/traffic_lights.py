import machine
import time
from umqttsimple import MQTTClient
import network
from machine import Timer

# 定义红绿灯引脚（顺序：红, 绿, 黄）
traffic_lights = [
    (25, 27, 26),  # 第一组 (红, 绿, 黄)A
    (13, 14, 12),  # 第二组B
    (21, 23, 22),  # 第三组C
    (19, 5, 18),  # 第四组D
    (4, 15, 2)  # 第五组E
]

# 定义每组灯的时长（单位：秒）
light_duration = [
    [25, 20, 3],  # 第一组
    [25, 20, 3],  # 第二组
    [25, 20, 3],  # 第三组
    [25, 20, 3],  # 第四组
    [20, 60, 5]  # 第五组
]

# 初始化红绿灯引脚
lights = []
for group in traffic_lights:
    lights.append([machine.Pin(pin, machine.Pin.OUT) for pin in group])


def on_red(group):
    lights[group][0].on()
    lights[group][1].off()
    lights[group][2].off()


def on_green(group):
    lights[group][0].off()
    lights[group][1].on()
    lights[group][2].off()


def on_yellow(group):
    lights[group][0].off()
    lights[group][1].off()
    lights[group][2].on()


current_light_state_dict = {
    0: {0: light_duration[0][0]},
    1: {0: light_duration[1][0]},
    2: {0: light_duration[2][0]},
    3: {0: light_duration[3][0]},
    4: {0: light_duration[4][0]},
}

function_call_mapping = {
    0: on_red,
    1: on_green,
    2: on_yellow,
}


# 先读取时长，再倒数，倒数完后再重新读取
def light_countdown(self):
    for k, v in current_light_state_dict.items():

        for light_state, count_down in v.items():
            # print(k, light_state, count_down)
            if count_down == 0:
                light_state += 1  # light state change
                new_state = light_state % 3
                current_light_state_dict[k] = {new_state: light_duration[k][new_state]}  # loop
                function_call_mapping[new_state](k)
            else:
                new_state = light_state % 3
                current_light_state_dict[k][light_state] -= 1

        if k == 1 or k == 2:
            for sub_k, sub_v in v.items():
                if sub_k == 0:
                    client.publish(b'network/traffic_info',
                                   str(k) + '_' + str(1) + '_' + str(current_light_state_dict[k][new_state]))
                elif sub_k == 1:
                    client.publish(b'network/traffic_info',
                                   str(k) + '_' + str(0) + '_' + str(current_light_state_dict[k][new_state]))
        else:
            client.publish(b'network/traffic_info',
                           str(k) + '_' + str(new_state) + '_' + str(current_light_state_dict[k][new_state]))
        time.sleep(0.05)


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
    print(topic, msg)
    global light_duration
    if topic == b'network/traffic_set':
        msg_part = [int(item) for item in msg.decode('utf-8').split('_')]
        print(msg_part)
        if msg_part[0] == 1 or msg_part[0] == 2:
            if msg_part[1] == 1:
                light_duration[msg_part[0]][0] = msg_part[2]
            elif msg_part[1] == 0:
                light_duration[msg_part[0]][1] = msg_part[2]
        else:
            light_duration[msg_part[0]][msg_part[1]] = msg_part[2]

    # 修改灯颜色，格式 id_color，颜色为 0 1 2-红绿黄


do_connect('iot', 'c108c108')
client = MQTTClient("ESP32_Traffic_Light_station", "192.168.124.10", 1883)
client.connect()  # 建立连接
client.set_callback(sub_cb)

timer = Timer(0)
timer.init(period=900, mode=Timer.PERIODIC, callback=light_countdown)

for i in range(5):
    on_red(i)

while True:
    client.subscribe('network/traffic_set')
    client.subscribe('network/traffic_set_color')
    time.sleep(1)

