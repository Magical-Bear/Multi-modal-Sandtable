"""
Author: Bill
Date Created: 2024-08-01
Description: Send instructions as mqtt publisher
"""

from mqtt_class import MQTTClient
import time


class MQTTRouter():
    def __init__(self):
        self.mqtt_client = MQTTClient()
        self.strip_line_list = [90, 60, 60, 60, 60, 60]
        pass

    def all_light_control(self, status):
        print("dj")
        for i in range(7):
            self.mqtt_client.publish("network/light", f'{i}_{status}')
            time.sleep(0.3)
        return "所有路灯开启好了" if status == 1 else "所有路灯关闭好了"

    def each_light_control(self, id, status):
        self.mqtt_client.publish("network/light", f"{id}_{status}")
        return f"{id}号路灯开启好了" if status == 1 else f"{id}号路灯关闭好了"

    def rgb_light_control(self, id, index, rgb):
        self.mqtt_client.publish("network/rgb_light", f"{id}_{index}_{rgb}")

    def send_recording_message(self):
        self.mqtt_client.publish("ai/local/recording", "action.wav")

    def send_car_semantic_position(self, pos):
        self.mqtt_client.publish("express/dest_where", f"0_{pos}")

    def rgb_line_control(self, id, rgb):
        line_length = self.strip_line_list[id]
        if id != 1:
            for i in range(line_length):
                self.rgb_light_control(id, i, rgb)
                time.sleep(0.01)
        else:
            for i in range(line_length-1, -1, -1):
                self.rgb_light_control(id, i, rgb)
                time.sleep(0.01)

    def rgb_line_open(self):
        self.mqtt_client.publish("network/rgb_light", "100_0_[255,0,0]")
        return f"所有灯带打开好了"

    def rgb_line_close(self):
        self.mqtt_client.publish("network/rgb_light", "100_0_[0,0,0]")
        return f"所有灯带关闭好了"
