import time
import cv2
import numpy as np
import ast
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont


class MQTTClient:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.message_arrive = None
        self.car_position_list =None

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
        if msg.topic == "ai/server/yolo/car":
            text_list = msg.payload.decode()
            self.car_position_list = ast.literal_eval(text_list)





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

def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype(
        "./simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)



# list_str = "[[]]"
# processed_list = ast.literal_eval(list_str)

cap = cv2.VideoCapture("rtsp://admin:iot_c108c108@192.168.124.5:554/stream1")



# Predict with the model

h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
print(h, w)

mqtt_client = MQTTClient("192.168.124.10", 1883, "yolo_show")
mqtt_client.connect()
mqtt_client.subscribe("ai/server/yolo/car")

while True:
    ret, frame = cap.read()
    start_time = time.time()
    if ret:
        if mqtt_client.car_position_list is not None:
            for i, polyline in enumerate(mqtt_client.car_position_list):
                point_list = np.int32(polyline)
                frame = cv2.polylines(frame, [point_list], True, (100, 100, 255), 7)
                frame = cv2AddChineseText(frame, f"{i}号小车", polyline[0],  textSize=40)
        # results = model(frame)
        # for result in results:
        #     for polyline in result.obb.xyxyxyxy:
        #         point_list = np.int32(polyline.numpy())
        #         img = cv2.polylines(frame, [point_list], 1, (100, 100, 255), 5)
                # print(point_list)
        # fps = round(1 / (time.time() - start_time), 2)
        # cv2.putText(frame, f"FPS: {fps}", (600, 400), 2, 2, (255, 0, 255), -1)
        frame = frame[:, 200:, ...]
        cv2.imshow("demo", frame)
        cv2.waitKey(1)


cv2.destroyAllWindows()
cap.release()
