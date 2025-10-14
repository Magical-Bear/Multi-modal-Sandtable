import json
import re
import requests
from shapely.geometry import Point, Polygon
import paho.mqtt.client as mqtt
from mqtt_sub_topics import mqtt_subscribe_info
import datetime


class Tokenizer:
    def __init__(self) -> None:
        with open("static_assets/vocab.txt", "r", encoding="utf-8") as f:
            vocab = f.read().split("\n")
            self.vocab_dict = {k: len(k) for k in vocab}

    def insert_unit(self, text: str) -> str:
        pattern = r'\d{2,}'
        matches = re.findall(pattern, text)

        for match in matches:
            if len(match) == 2:  # 两位数
                if match[1] != '0':
                    text = text.replace(match, match[0] + '十' + match[1])
                else:
                    text = text.replace(match, match[0] + '十')
            elif len(match) == 3:  # 三位数
                text = text.replace(match, match[0] + '百' + match[1] + '十' + match[2])
        return text

    def tokenize(self, text: str) -> str:
        unit_text = self.insert_unit(text)
        max_token_len = max(self.vocab_dict.values())
        sentence_len = len(unit_text)
        tokenized, index = [], 0
        max_len = max_token_len if sentence_len > max_token_len else sentence_len

        while index < sentence_len:
            for word_len in range(max_len, 0, -1):
                if unit_text[index:index + word_len] in self.vocab_dict:
                    tokenized.append(unit_text[index:index + word_len])
                    index += word_len
                    break
                elif word_len == 1:
                    tokenized.append(unit_text[index:index + 1])
                    index += word_len
                    break
        return tokenized

# point in polygon
def check_point_in_polygon(point: list[int, int], polygon_data: list[list[int, int]]) -> bool:
    polygon = Polygon(polygon_data)
    point_obj = Point(point)
    return polygon.contains(point_obj)

# rotate to xy center
def convert_xyxyxyxy_to_center_xy(obb: list[list[int]]) -> list[int, int]:
    left_top = obb[0]
    right_button = obb[2]
    center_x = (left_top[0] + right_button[0]) // 2
    center_y = (left_top[1] + right_button[1]) // 2
    return [center_x, center_y]

# closest surface
def closest_polygon(point: list[int, int], polygons: dict) -> list[str, float]:
    point = Point(point)
    min_distance = float('inf')
    closest_poly = None

    for name, vertices in polygons.items():
        polygon = Polygon(vertices)
        distance = point.distance(polygon)
        if distance < min_distance:
            min_distance = distance
            closest_poly = name

    return [closest_poly, min_distance]

# str to gb2312 to send
def str_to_gb2312(text: str) -> str:
    encoded = text.encode("gb2312")
    return encoded.hex()

# point surface relations
def point_close_surface(self, point: list[int, int], surface: dict, threshold=1000) -> any:
    closest_poly, distance = closest_polygon(point, surface)
    # print(closest_poly, distance)
    if distance < threshold:
        return closest_poly
    return None

# get current_time
def get_current_time() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# compute time delta
def compute_time_delta(record_time: str) -> str:
    current_time = datetime.datetime.now()
    record_time = datetime.datetime.strptime(record_time, "%Y-%m-%d %H:%M:%S")
    delta = current_time - record_time
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # 构建中文格式的字符串
    return f"{days}日{hours}时{minutes}分{seconds}秒"

def api_fetch_city_weather(city_name: str = "成都") -> tuple:
    apiUrl = 'http://apis.juhe.cn/simpleWeather/query'
    requestParams = {
        'key': '019055838245e553174542efe65cf351',
        'city': city_name,
    }

    reduce_weather_condition = {
        "sun": ["晴"],
        "cloud": ["云", "阴", "雾"],
        "flash": ["电"],
        "snow": ["雪", "雹"],
        "rain": ["雨"],
    }

    with open("static_assets/weather.text", "r", encoding="utf-8") as f:
        weather_line = f.read().split("\n")

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    today_weather_is_fetched = True if len([True for date_weather in weather_line if current_date in json.loads(date_weather)]) == 1 else False
    if today_weather_is_fetched is False:
        try:
            response = requests.get(apiUrl, params=requestParams).json()
            if "reason" in response and response["reason"] == "查询成功!":
                results = response.get("result")
                future = results.get("future")
                weather_icon_reduce = [k for k, v in reduce_weather_condition.items() if results.get("realtime", {}).get("info", "").strip()[-1] in v][0]
                weather_text = f"天气：{results.get('realtime').get('info')} {future[0].get('temperature')}"
        except:
            weather_icon_reduce = "cloud"
            weather_text = "天气：阴 18/28℃"
    else:
        saved_weather = [json.loads(date_weather) for date_weather in weather_line if current_date in json.loads(date_weather)][0].get(current_date)
        weather_icon_reduce = saved_weather.get("weather_icon")
        weather_text = saved_weather.get("weather_text")

    # new weather save
    if weather_icon_reduce and weather_text and today_weather_is_fetched is False:
        save_dict = {current_date: {"weather_icon": weather_icon_reduce, "weather_text": weather_text}}
        with open("static_assets/weather.text", "a", encoding="utf-8") as f:
            f.write(f"\n{json.dumps(save_dict, ensure_ascii=False)}")

    # fetch failed use last record
    elif (weather_text is None or weather_icon_reduce is None) and today_weather_is_fetched is False:
        weather_icon_reduce = json.loads(weather_line[-1]).get("weather_icon")
        weather_text = json.loads(weather_line[-1]).get("weather_text")

    return weather_icon_reduce, weather_text

# MQTT class
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
            print("connected")
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
        msg_info = msg.payload.decode()
        try:
            msg_info = eval(msg_info)
        except Exception as e:
            pass
        if msg.topic in mqtt_subscribe_info and isinstance(msg_info, float):
            mqtt_subscribe_info[msg.topic][0] = msg_info
            mqtt_subscribe_info[msg.topic][1] = True
        elif msg.topic == "ai/car_pos" and isinstance(msg_info, dict):
            mqtt_subscribe_info["ai/car_pos"].update(msg_info)
        # print(mqtt_subscribe_info)



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

mqtt_client = MQTTClient("192.168.124.10", 1883, "plate_client")
mqtt_client.connect()
for topic, payload in mqtt_subscribe_info.items():
    mqtt_client.subscribe(topic)

def mqtt_publish(topic: str, payload: str) -> None:
    mqtt_client.publish(topic, payload)


if __name__ == "__main__":
    car_pos_example = {
        "3": [(200, 200), (250, 200), (250, 250), (200, 250)]
    }
    mqtt_publish("wei/scanner_id", "hello")

    while True:
        pass





