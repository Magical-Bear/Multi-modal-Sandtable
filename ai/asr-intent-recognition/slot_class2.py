"""
Author: Bill
Date Created: 2024-08-01
Description: Neural Language Understanding and Slot Filling convert to instructions,by asr
"""

import json
from route_class import MQTTRouter
from coordinate_class import CoordinatePosition
from mqtt_class import MQTTClient
import ast


class NLPSlot():
    def __init__(self):
        self.actions_list = [['打开', '开启', '阿开', "啊开", "达泰","达开",'开','凯','楷','恺'], ['关闭', "管毕", "玩毕", "完毕",'必','关','管'], ["启动","起动"], ["暂停","赞亭","暂廷","站"], ["哪里", "在哪", "位置"]]
        self.object_list = [["路灯","路登", "的", "灯", "等", "路单", "路灯", "录登", "录灯", "登","路丹","鲁丹","卢登"], ["车辆", "小车", "校车"], ["温度"], ["湿度"], ["灯带", "等待", "登带", "带"], ["这个", "那个", "这是", "这里", "是"]]
        self.num_list = [["全部", "所有", "所有路", "所有度"], [0, "零号", "0号", '林号路', "0", "零", "林号", "部单", "宁号","动林号"], [1, "1号", "一号", '依号路', "1", "依号", "一号路", "伊号", "一号录"], [2, "二号"],[3, "三号","三号路"],[4, "四号"],[5, "五号","武号","无号"],[6, "六号","留号","刘号"],[7, "汽号","七号","气号","停七号","期号"],[8, "八号","巴号","停八号"],[9, "九号","酒","停酒号","停九号","停决号"], ["白色"], ["绿色"], ["红色"], ["蓝色"]]

        self.action = None
        self.obj_type = None
        self.obj_num = None
        self.asr_cache = None
        self.router = MQTTRouter()
        self.position = CoordinatePosition()

    def light_recognition(self, action, num):
        if num == "全部":
            if action == "打开":
                return self.router.all_light_control(1)
            else:
                return self.router.all_light_control(0)
        else:
            if action == "打开":
                return self.router.each_light_control(num, 1)
            else:
                return self.router.each_light_control(num, 0)


    def car_recognition(self):
        car_pos = MQTTClient().mqtt_message_cache["car_pos"]["ai/server/yolo/car"]
        if car_pos:
            car_pos = ast.literal_eval(car_pos)
            road = self.position.car_in_which_road(car_pos)
            building = self.position.car_close_to_which_building(car_pos)
            if road and building:
                return f"小车位于{road}临近{building}"
            return f"小车位于{road}" if road else f"小车临近{building}"
        return f"定位失败了，重新放个位置试试呢"

    def strip_recognition(self):
        pass

    def temp_recognition(self):
        temp = MQTTClient().mqtt_message_cache["temperature"]["network/temp_info"]
        if temp:
            temp = temp.split("_")[1]
            return f"当前温度是{temp}摄氏度"
        return f"等待温度传感器上报数据"


    def humi_recognition(self):
        humi = MQTTClient().mqtt_message_cache["humidity"]["network/humi_info"]
        if humi:
            humi = humi.split("_")[1]
            return f"当前湿度是百分之{humi}"
        return f"等待温度传感器上报数据"

    def multimodal_recognition(self, action):
        finger = MQTTClient().mqtt_message_cache["finger_pos"]["ai/server/yolo/finger"]
        if finger:
            finger = ast.literal_eval(finger)
            area = self.position.finger_in_which_area(finger)
            building = self.position.finger_in_which_building(finger)
            if action in ["打开", "关闭"]:
                if area:
                    if action == "打开":
                        result = self.router.each_light_control(area, 1)
                        self.router.rgb_light_control()
                    else:
                        result = self.router.each_light_control(area, 0)
                    return result
            elif action in self.actions_list[-1]:
                if building:
                    return self.position.finger_in_which_building(building)

        return f"没找到您的手指"

    def asr_controller(self, message):
        action, obj, num = None, None, None
        result = None
        print(message)
        try:
            message_dict = dict(eval(message))
        except:

            print("json error")
            print(message)
            return None


        for k, v in message_dict.items():
            if k == "action" and action is None:
                for group in self.actions_list:
                    if v in group:
                        action = group[0]


            if k == "object" and obj is None:
                for group in self.object_list:
                    if v in group:
                        obj = group[0]


            if k == "number" and num is None:
                for group in self.num_list:
                    if v in group:
                        num = group[0]


        print(obj, num, action, "dsjakhsadh")
        if action and obj and num:
            if obj == "路灯":
                result = self.light_recognition(action, num)
            elif obj == "车辆":
                result = self.car_recognition()

        if obj == "车辆":
            result = self.car_recognition()
        elif obj == "温度":
            result = self.temp_recognition()
        elif obj == "湿度":
            result = self.humi_recognition()
        elif obj in self.object_list[-1]:
            result = self.multimodal_recognition(action)

        return result

















