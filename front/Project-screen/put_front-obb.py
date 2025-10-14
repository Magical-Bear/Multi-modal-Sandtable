import time
import cv2
import numpy as np
import ast
import paho.mqtt.client as mqtt
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, Response


app = Flask(__name__)

class MQTTClient:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.car_position_dict = {}

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
        text_list = msg.payload.decode()
        self.car_position_dict.update(ast.literal_eval(text_list))

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
    if isinstance(img, np.ndarray):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype("./simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


# 视频流函数
def generate_video_stream():
    cap = cv2.VideoCapture("rtsp://admin:iot_c108c108@192.168.124.5:554/stream1")
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    mqtt_client = MQTTClient("192.168.124.10", 1883, "yolo_show")
    mqtt_client.connect()
    mqtt_client.subscribe("ai/car_pos")

    while True:
        ret, frame = cap.read()
        if ret:
            if mqtt_client.car_position_dict is not None:
                for i, polyline in mqtt_client.car_position_dict.items():
                    point_list = np.int32(polyline)
                    frame = cv2.polylines(frame, [point_list], True, (100, 100, 255), 7)
                    frame = cv2AddChineseText(frame, f"{i}号小车", polyline[0], textSize=40)


            frame = frame[:, 200:, ...]
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# Flask 路由
@app.route('/')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5200, debug=True)
