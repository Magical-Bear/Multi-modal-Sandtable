import base64
import json
import time
import datetime
import os
import requests
from utils import Tokenizer, get_current_time, compute_time_delta, str_to_gb2312, mqtt_publish, check_point_in_polygon, convert_xyxyxyxy_to_center_xy, api_fetch_city_weather, check_point_in_polygon
from mqtt_sub_topics import mqtt_subscribe_info


class Car:
    def __init__(self):
        with open("static_assets/road_boundary.json", "r", encoding="UTF8") as f:
            self.polygon = json.load(f)
        with open("static_assets/car_plate_mapping.json", "r", encoding="UTF8") as f:
            self.plate = json.load(f)
        self.road_car_num_dict = {k: 0 for k, _ in self.polygon.items()}
        self.road_car_plate_dict = {k: [] for k, _ in self.polygon.items()}
        self.road_car_name_dict = {k: [] for k, _ in self.polygon.items()}

    def front_parser_pos(self, plate_dict: dict[list]):
        for k, v in plate_dict.items():
            center = convert_xyxyxyxy_to_center_xy(v)
            for name, polygon in self.polygon.items():
                if check_point_in_polygon(center, polygon):
                    self.road_car_num_dict[name] += 1
                    self.road_car_plate_dict[name].append(k)
                    self.road_car_name_dict[name].append(self.plate[k]["type"])

    def get_area_plate(self):
        pass

    def get_car_in_which_road(self, plate):
        pass

    def get_car_location(self):
        pass

    def get_car_name(self):
        pass

    def get_car_color(self):
        pass

    def get_car_in_which_road(self):
        pass

    def clear_road_info(self):
        self.road_car_num_dict = {k: 0 for k, _ in self.polygon.items()}
        self.road_car_plate_dict = {k: [] for k, _ in self.polygon.items()}
        self.road_car_name_dict = {k: [] for k, _ in self.polygon.items()}

    def get_road_car_num(self):
        return self.road_car_num_dict

    def get_road_car_name(self):
        return self.road_car_name_dict

    def get_road_car_plate(self):
        return self.road_car_plate_dict

    def traffic_notice_boardcast(self, plate_dict: dict[list]):
        self.clear_road_info()
        self.front_parser_pos(plate_dict)
        # self.road_car_num_dict["广严大道"] = 3
        # self.road_car_name_dict["广严大道"] = ["公交车", "跑车", "公交车"]
        notice_str = " "
        for k, v in self.road_car_num_dict.items():
            if v == 0:
                continue
            collet_car_type = list(set(self.road_car_name_dict[k]))
            type_num_dict = {car_type: sum(1 for name in self.road_car_name_dict[k] if name == car_type) for car_type in collet_car_type}
            notice_str += f"{k}有"
            for k, v in type_num_dict.items():
                notice_str += f"{v}辆{k}、"
            notice_str = notice_str[:-1]
            notice_str += ","
        if notice_str == " ":
            return
        notice_str = notice_str[:-1] if len(notice_str) >= 24 else f"{notice_str[:-1]}请注意运行"
        mqtt_publish("screen/traffic_boardcast", str_to_gb2312(notice_str))


class UpdateScreen:
    def __init__(self):
        self.welcome_text = "物联网工程系欢迎您"
        self.weather_icon = None
        self.weather_text = None
        self.screen1_in, self.screen2_in = 0, 0
        self.screen1_out, self.screen2_out = 0, 0

        self.fetch_current_weather()
        self.update_weather_icon()
        self.update_weather_text()
        self.update_time()
        self.update_welcome_text()
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")




    def fetch_current_weather(self):
        # 检查今日日期与本地是都存在日期文件
        # 不存在则API拉取
        # 拉取后保存本地JSON，文件名为今日日期.json
        # 读取本地文件
        # 更新self.weather_icon self.weather_text
        # 发布消息

        self.weather_icon, self.weather_text = api_fetch_city_weather()
        print(self.weather_icon, self.weather_text)


    def update_time(self):
        time_now = datetime.datetime.now().strftime("%Y %m %d %H %M %S")
        time_format = [int(time) if len(time) == 2 else int(time[2:]) for time in time_now.split(" ")]
        mqtt_publish("screen/time_sync", str(time_format))

    def update_weather_icon(self):
        mqtt_publish("screen/weather", self.weather_icon)
        pass

    def update_weather_text(self):
        mqtt_publish("screen/weather_text", str_to_gb2312(self.weather_text))
        pass

    def update_welcome_text(self):
        text_hex = str_to_gb2312(self.welcome_text)
        mqtt_publish("screen/welcome_text", text_hex)

    def update_total_in_ground(self):
        all_in = self.screen1_in + self.screen2_in
        all_out = self.screen1_out + self.screen2_out
        mqtt_publish("screen/at_park", str_to_gb2312(f"在场车辆:{all_in - all_out}"))

    def update_entrance_out_number(self):
        with open("static_assets/parking_info.json", "r", encoding="UTF8") as f:
            records = json.load(f)
        today_records = records[self.current_date]
        for k, v in today_records.items():
            if v[1] == "screen1" and v[2] == "entrance":
                self.screen1_in += 1
            elif v[1] == "screen2" and v[2] == "entrance":
                self.screen2_in += 1
            elif v[1] == "screen1" and v[2] == "exit":
                self.screen1_out += 1
            elif v[1] == "screen2" and v[2] == "exit":
                self.screen2_out += 1


    def update_screen1_entrance(self):
        self.update_entrance_out_number()
        self.update_total_in_ground()
        mqtt_publish("screen1/entrance", str_to_gb2312(f"今日进场{self.screen1_in}/{self.screen1_in + self.screen2_in}"))


    def update_screen2_entrance(self):
        self.update_entrance_out_number()
        self.update_total_in_ground()
        mqtt_publish("screen2/entrance",
                     str_to_gb2312(f"今日进场{self.screen1_in}/{self.screen1_in + self.screen2_in}"))

    def update_screen1_exit(self, time_delta):
        self.update_entrance_out_number()
        self.update_total_in_ground()
        mqtt_publish("screen1/exit",
                     str_to_gb2312(f"今日出场{self.screen1_out}/{self.screen1_out + self.screen2_out}"))

    def update_screen2_exit(self, time_delta):
        self.update_entrance_out_number()
        self.update_total_in_ground()
        mqtt_publish("screen2/exit",
                     str_to_gb2312(f"今日出场{self.screen2_out}/{self.screen1_out + self.screen2_out}"))



    def update_screen1_plate(self, plate: str):
        mqtt_publish("screen1/car_plate", str_to_gb2312(f"{plate}"))

    def update_screen2_plate(self, plate: str):
        mqtt_publish("screen2/car_plate", str_to_gb2312(f"{plate}"))

    def update_screen1_car_inspect(self, direction):
        mqtt_publish("screen1/car_inspect", str_to_gb2312(f"车辆方向：{direction}"))

    def update_screen2_car_inspect(self, direction):
        mqtt_publish("screen2/car_inspect", str_to_gb2312(f"车辆方向：{direction}"))

    def update_screen1_parking_time(self, time_delta):
        if time_delta:
            mqtt_publish("screen1/stop_time", str_to_gb2312(time_delta))
        else:
            mqtt_publish("screen1/stop_time", str_to_gb2312("联系工作人员"))

    def update_screen2_parking_time(self, time_delta):
        if time_delta:
            mqtt_publish("screen2/stop_time", str_to_gb2312(time_delta))
        else:
            mqtt_publish("screen2/stop_time", str_to_gb2312("联系工作人员"))

    def control_screen1_gate(self, status: int):
        mqtt_publish("screen1/gate_status", str(status))

    def control_screen2_gate(self, status: int):
        mqtt_publish("screen2/gate_status", str(status))


class ParkingManagementSystem:
    def __init__(self):
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.current_records = self.get_current_parking_info()

    def get_current_parking_info(self):
        try:
            with open("static_assets/parking_info.json", "r", encoding="UTF8") as f:
                records = json.load(f)
        except:
            records = {}

        if self.current_date in records:
            return records[self.current_date]
        else:
            records[self.current_date] = {}
            with open("static_assets/parking_info.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(records, ensure_ascii=False, indent=4))
            return records[self.current_date]

    def update_json_records(self):
        with open("static_assets/parking_info.json", "r", encoding="UTF8") as f:
            records = json.load(f)
        records[self.current_date] = self.current_records
        with open("static_assets/parking_info.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(records, ensure_ascii=False, indent=4))

    def update_parking_records(self, plate, status, gate):
        record_count = 0 if len(self.current_records) == 0 else len(self.current_records)
        parking_record = [plate, gate, status, get_current_time()]
        self.current_records[record_count] = parking_record
        self.update_json_records()

    def on_screen1_entrance(self, plate: str):
        self.update_parking_records(plate, "entrance", "screen1")

    def on_screen2_entrance(self, plate: str):
        self.update_parking_records(plate, "entrance", "screen2")

    def on_screen1_exit(self, plate: str):
        '''
        1.识别车牌
        2.记录时间
        3.检查是否有入场纪录
        4.如果有，显示屏幕等自动开
        5.写入数据库
        6.如果没有，等待人工处理，播报声音
        7.不写入数据库
        :return:
        '''
        matched_k, match_count = -1, 0
        for k, v in self.current_records.items():
            if v[0] == plate and v[2] == "entrance":
                match_count += 1
                matched_k = k
        if matched_k == -1 or match_count %2 == 0:
            # 无入场纪录
            return
        entrance_record = self.current_records[matched_k]
        time_delta = compute_time_delta(entrance_record[3])
        # 分词播报更新屏幕开闸机
        self.update_parking_records(plate, "exit", "screen1")
        return time_delta


    def on_screen2_exit(self, plate: str):
        matched_k, match_count = -1, 0
        for k, v in self.current_records.items():
            if v[0] == plate and v[2] == "entrance":
                match_count += 1
                matched_k = k
        if matched_k == -1 or match_count % 2 == 0:
            # 无入场纪录
            return
        entrance_record = self.current_records[matched_k]
        time_delta = compute_time_delta(entrance_record[3])
        # 分词播报更新屏幕开闸机
        self.update_parking_records(plate, "exit", "screen2")
        return time_delta


class Controller:
    def __init__(self):
        self.parking_manage = ParkingManagementSystem()
        self.flush_screen = UpdateScreen()
        self.tokenizer = Tokenizer()
        with open("static_assets/building_boundary.json", "r", encoding="utf-8") as f:
            self.boundary = json.load(f)
        with open("static_assets/car_plate_mapping.json", "r", encoding="utf-8") as f:
            self.car_binding = json.load(f)
        self.mapping_dict = {
            "screen1/car_in": self.screen1_in,
            "screen2/car_in": self.screen2_in,
            "screen1/car_out": self.screen1_out,
            "screen2/car_out": self.screen2_out,
        }
        self.global_lock = False
        self.start_lock_time = time.time()
        self.release_time = 12
        self.car = Car()
        self.update_traffic_time = 40
        self.start_traffic_time = time.time()
        self.car_pos_copy = None

    def runnable(self):
        while True:
            for k, v in mqtt_subscribe_info.items():
                if k == "ai/car_pos":
                    continue
                if v[1] is True and self.global_lock is False:
                    # 从ai/car_pos遍历所有坐标
                    # 将xyxyxyxy坐标转center_xy
                    # 预先定义停车场入口坐标范围
                    # 检查center_xy 是否位于坐标范围内
                    # 若位于，结合进出调用不同的执行函数(即拿到是哪个门，哪个方向和那一辆车)
                    # 锁定15秒，防止误识别
                    self.car_pos_copy = mqtt_subscribe_info["ai/car_pos"].copy()
                    exec = self.mapping_dict[k]()
                    if exec is True:
                        self.global_lock = True
                        self.start_lock_time = time.time()
                        v[1] = False

            if self.global_lock and time.time() - self.start_lock_time >= self.release_time:
                self.resume_running()
            if time.time() - self.start_traffic_time >= self.update_traffic_time:
                self.traffic_boardcast(mqtt_subscribe_info["ai/car_pos"].copy())
                self.start_traffic_time = time.time()


    def fetch_plate(self, gate):
        boundary = self.boundary.get(gate)
        plate = -1
        for k, v in self.car_pos_copy.items():
            center_xy = convert_xyxyxyxy_to_center_xy(v)
            if check_point_in_polygon(center_xy, boundary):
                plate = k
        print(f"有效车牌{plate}")
        return plate

    def screen1_in(self):
        '''
        1.识别车牌
        2.记录时间
        3.控制屏幕数据更新
        4.开闸机
        5.写入数据库
        :return:
        '''
        plate = self.fetch_plate("广进门")
        if plate == -1:
            return False
        plate = str(plate)
        self.flush_screen.control_screen1_gate(1)
        self.play_voice("screen1", f"成都锦城学院进场车车牌号{plate}号车型{self.car_binding[str(plate)].get('type')}欢迎光临")
        self.parking_manage.on_screen1_entrance(plate)
        self.flush_screen.update_screen1_plate(f"车牌号:{plate}号车")
        self.flush_screen.update_screen1_car_inspect("进场")
        self.flush_screen.update_screen1_entrance()
        mqtt_publish("screen1/lock_released", "0")
        return True


    def screen2_in(self):
        plate = self.fetch_plate("严出门")
        if plate == -1:
            return False
        plate = str(plate)
        self.flush_screen.control_screen2_gate(1)
        self.play_voice("screen2",
                        f"成都锦城学院进场车车牌号{plate}号车型{self.car_binding[str(plate)].get('type')}欢迎光临")
        self.parking_manage.on_screen2_entrance(plate)
        self.flush_screen.update_screen2_plate(f"车牌号:{plate}号车")
        self.flush_screen.update_screen2_car_inspect("进场")
        self.flush_screen.update_screen2_entrance()
        mqtt_publish("screen2/lock_released", "0")
        return True

    def screen1_out(self):

        plate = self.fetch_plate("广进门")
        if plate == -1:
            return False
        plate = str(plate)
        time_delta = self.parking_manage.on_screen1_exit(plate)
        print(time_delta)
        if time_delta is None:
            self.play_voice("screen1",
                            f"成都锦城学院车牌号{plate}号车型{self.car_binding[str(plate)].get('type')}未检测到入场记录")
            self.flush_screen.update_screen1_parking_time(None)
        else:
            self.flush_screen.control_screen1_gate(1)
            self.play_voice("screen1",
                            f"成都锦城学院车牌号{plate}号停车总时长为{time_delta}一路顺风")
            self.flush_screen.update_screen1_parking_time(time_delta)
        self.flush_screen.update_screen1_plate(f"车牌号:{plate}号车")
        self.flush_screen.update_screen1_car_inspect("出场")
        self.flush_screen.update_screen1_exit(time_delta)
        mqtt_publish("screen1/lock_released", "1")
        return True

    def screen2_out(self):
        plate = self.fetch_plate("严出门")
        if plate == -1:
            return False
        plate = str(plate)
        print(plate)
        time_delta = self.parking_manage.on_screen2_exit(plate)
        print(time_delta)
        if time_delta is None:
            self.play_voice("screen2",
                            f"成都锦城学院车牌号{plate}号车型{self.car_binding[str(plate)].get('type')}未检测到入场记录")
            self.flush_screen.update_screen2_parking_time(None)
        else:
            self.flush_screen.control_screen2_gate(1)
            self.play_voice("screen2",
                            f"成都锦城学院车牌号{plate}号停车总时长为{time_delta}一路顺风")
            self.flush_screen.update_screen2_parking_time(time_delta)
        self.flush_screen.update_screen2_plate(f"车牌号:{plate}号车")
        self.flush_screen.update_screen2_car_inspect("出场")
        self.flush_screen.update_screen2_exit(time_delta)
        mqtt_publish("screen2/lock_released", "1")
        return True

    def resume_running(self):
        self.global_lock = False
        self.flush_screen.control_screen1_gate(0)
        self.flush_screen.update_screen1_plate(f"车牌号:无")
        self.flush_screen.control_screen2_gate(0)
        self.flush_screen.update_screen2_plate(f"车牌号：无")
        print("released")

    def play_voice(self, screen, text: str):
        tokenized = self.tokenizer.tokenize(text)
        print(tokenized)
        mqtt_publish(f"{screen}/voice_message", str(tokenized))

    def traffic_boardcast(self, plate_dict):
        self.car.traffic_notice_boardcast(plate_dict)



if __name__ == "__main__":
    controller = Controller()
    controller.runnable()



