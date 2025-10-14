from machine import Pin, PWM
import time
import machine
import network
from umqttsimple import MQTTClient
import dht

# 初始引脚
pins = [12, 13, 14, 16, 17, 18, 19]
pin_instance = [machine.Pin(pin, machine.Pin.OUT) for pin in pins]
for pin in pin_instance:
    pin.off()

station_id = 1
device_client_id = f"network_sensor_{station_id}"

def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to network...")
        wlan.connect('iot', 'c108c108')
        while not wlan.isconnected():
            pass
    print('Network config:', wlan.ifconfig())


def get_temp_hum():
    try:
        d.measure()  # 触发传感器进行一次测量
        temp = d.temperature()
        hum = d.humidity()
    except:
        temp, hum = 24, 60
    return temp, hum


def message_callback(topic, msg):
    print("Received message:", msg.decode())
    try:
        # 解析 id 和 state
        id_state = msg.decode().split('_')
        id = int(id_state[0])
        state = int(id_state[1])
        pinner = pin_instance[id]
        if state == 0:
            pinner.value(0)
        else:
            pinner.value(1)

    except (IndexError, ValueError) as e:
        print("Invalid message format:", e)
        return


if __name__ == "__main__":
    do_connect()

    c = MQTTClient(device_client_id, "192.168.124.10", 1883, keepalive=60)
    c.set_callback(message_callback)  # 设置消息回调函数
    c.connect()
    c.subscribe("network/light")
    try:
        d = dht.DHT11(machine.Pin(23))
    except:
        time.sleep(1)
        d = dht.DHT11(machine.Pin(23))
    start_time = time.time() + 4

    while True:
        if time.time() - start_time >= 5:
            temp, hum = get_temp_hum()
            c.publish("network/temp_info", f"{station_id}_{temp}")
            c.publish("network/humi_info", f"{station_id}_{hum}")
            start_time = time.time() + 4

        c.check_msg()  # 检查是否有消息并调用回调函数


