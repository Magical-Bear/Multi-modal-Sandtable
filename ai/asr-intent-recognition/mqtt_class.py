"""
Author: Bill
Date Created: 2024-08-01
Description: Instance mqtt object and subscribe messages from sensors
"""
import paho.mqtt.client as mqtt
import time
import threading

class MQTTClient:
    _instance_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super(MQTTClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, broker="127.0.0.1", port=1883, client_id="speech_local"):
        if not hasattr(self, "_initialized"):
            self.broker = broker
            self.port = port
            self.client_id = client_id
            self.client = mqtt.Client(client_id, protocol=mqtt.MQTTv311)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            self.mqtt_message_cache = {}
            self.mqtt_message_cache["humidity"] = {"network/humi_info": None}
            self.mqtt_message_cache["temperature"] = {"network/temp_info": None}
            self.mqtt_message_cache["finger_pos"] = {"ai/server/yolo/finger": None}
            self.mqtt_message_cache["car_pos"] = {"ai/server/yolo/car": None}
            self.mqtt_message_cache["traffic_info"] = {"network/traffic_info": [None] * 5}
            self.mqtt_message_cache["asr_info"] = {"ai/server/text_list": None}
            self.mqtt_message_cache["wwd_info"] = {"ai/local/wwd": None}
            self.mqtt_message_cache["plate_pos"] = {"ai/car_pos": None}

            self._initialized = True
            self.runnable()

    def parse_traffic_light(self, message: str):
        message = [int(item) for item in message.split("_")]
        self.mqtt_message_cache["traffic_info"]["network/traffic_info"][message[0]] = [message[1], message[2]]

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
        except Exception as e:
            print(f"Connection failed: {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected successfully")
        else:
            print(f"Connect failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected, trying to reconnect...")
        self.connect()

    def on_message(self, client, userdata, msg):
        # print(f"Received message: {msg.topic} -> {msg.payload.decode()}")
        for k, v in self.mqtt_message_cache.items():
            if msg.topic == list(v.keys())[0] and msg.topic != "network/traffic_info" and msg.topic != "ai/car_pos":
                v[msg.topic] = msg.payload.decode()
            elif msg.topic == "network/traffic_info":
                self.parse_traffic_light(msg.payload.decode())
            elif msg.topic == "ai/car_pos":
                message = eval(msg.payload.decode())
                if self.mqtt_message_cache["plate_pos"]["ai/car_pos"] is None:
                    self.mqtt_message_cache["plate_pos"]["ai/car_pos"] = message
                else:
                    self.mqtt_message_cache["plate_pos"]["ai/car_pos"] = message


        # print(self.mqtt_message_cache)

    def publish(self, topic, payload):
        try:
            self.client.publish(topic, payload)
        except Exception as e:
            print(f"Publish failed: {e}")

    def subscribe(self, topic):
        try:
            self.client.subscribe(topic)
        except Exception as e:
            print(f"Subscribe failed: {e}")

    def runnable(self):
        self.connect()
        for k, v in self.mqtt_message_cache.items():
            self.subscribe(list(v.keys())[0])

# 使用单例模式
# mqtt_client = MQTTClient()
# while True:
#     time.sleep(1)