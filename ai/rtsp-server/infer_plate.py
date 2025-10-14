from ultralytics import YOLO
import paho.mqtt.client as mqtt
import time
import cv2
import json
import sys
import torch
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cls_model = YOLO('runs/classify/train2/weights/best.pt')  #
plate_list = ["1", "11", "12", "13", "14", "2", "3"]


def crop_and_preprocess(img: np.ndarray, points: list, output_size: int = 224) -> np.ndarray:
    """
    使用旋转框裁剪图像区域，并Resize为指定尺寸，转为归一化Tensor。

    参数:
        img (np.ndarray): OpenCV读取的原图，格式为 HWC, BGR。
        points (np.ndarray): 四点坐标，形状为 (4, 2)，float32类型。
        output_size (int): resize目标尺寸（默认640 -> 输出为 640x640）。

    返回:
        torch.Tensor: 形状为 (1, 3, output_size, output_size)，已归一化。
    """

    # 确保为 float32
    x_coords = [point[0] for point in points]
    y_coords = [point[1] for point in points]

    xmin = min(x_coords) if min(x_coords) >= 0 else 0
    xmax = max(x_coords)
    ymin = min(y_coords) if min(y_coords) >= 0 else 0
    ymax = max(y_coords)

    print(xmin, ymin, xmax, ymax)
    # resize到统一大小
    resized = cv2.resize(img[ymin: ymax, xmin: xmax, ...], (output_size, output_size), interpolation=cv2.INTER_LINEAR)

    return resized


class MQTTClient:
    def __init__(self, broker, port, client_id):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

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
        print(f"Received message: {msg.topic} -> {msg.payload.decode()}")


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

nat_ip = "10.8.106.156"
model = YOLO("./runs/obb/train7/weights/best.pt")  # load a custom model
rtsp_url = f"rtsp://admin:iot_c108c108@{nat_ip}:1554/stream1"
mqtt_client = MQTTClient(nat_ip, 1883, "yolo_server")
mqtt_client.connect()
target_size = (224, 224)

# 创建 VideoCapture 对象
cap = cv2.VideoCapture(rtsp_url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)

# 检查视频流是否打开成功
if not cap.isOpened():
    print("无法打开视频流")
    exit()

count = 0
while True:
    count += 1

    if count % 2 == 0:
        ret, frame = cap.read()
        continue
    else:
        ret, frame = cap.read()

    plate_dict = {}

    if not ret:
        print("无法读取视频帧")
        break

    results = model(frame)  # generator of Results objects

    for r in results:

        cls = list(r.obb.cls.cpu().numpy())

        if len(cls) > 0:
            car_pos_list = []
            car_flag = False
            for i, item in enumerate(cls):
                data = r.obb.xyxyxyxy.cpu().numpy()[i]
                int_data = [[int(value) if value >= 0 else 0 for value in row] for row in data]
                if int(item) == 0:
                    mqtt_client.publish("ai/server/yolo/finger", str(int_data))
                elif int(item) == 1:
                    car_flag = True

                    plate_img = crop_and_preprocess(frame, int_data)
                    results = cls_model.predict(plate_img)

                    # 输出预测结果
                    for result in results:
                        argmax = result.probs.top1
                        plate_number = plate_list[argmax]
                        plate_dict[plate_number] = int_data
                    #     results = plate_model(tensor.to(device))
                    #     results = torch.softmax(results, dim=1).cpu()
                    #     argmax = torch.argmax(results, dim=1).item()
                    # plate_dict[plate_list[argmax]] = int_data
                    # print(results)
                    # print(argmax)
                    # if results[0][argmax] >= 0.15:
                    #     plate_dict[plate_list[argmax]] = int_data

            if car_flag:
                mqtt_client.publish("ai/car_pos", json.dumps(plate_dict))
                print(plate_dict)


    time.sleep(0.03)

# 释放资源
cap.release()
cv2.destroyAllWindows()






