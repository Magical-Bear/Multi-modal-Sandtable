"""
Author: Bill
Date Created: 2024-08-01
Description: Neural Language Understanding and Slot Filling convert to instructions
"""

import json
import time

from route_class import MQTTRouter
from coordinate_class import CoordinatePosition
from mqtt_class import MQTTClient
import ast


class NLPSlot():
    def __init__(self):
        self.actions_list = [['打开', '还有','开启', '阿开', "啊开", "达泰","达开","开",'大凯','大楷','大开','答开', "开启", "开起"], ['关闭', "管毕", "玩毕", "完毕"], ["启动","起动"], ["暂停","赞亭","暂廷","站"], ["哪里", "在哪", "位置", "是哪", "哪儿"]]
        self.object_list = [["路灯","路登", "的", "灯", "等", "路单", "路灯", "雾灯","录登", "录灯", "登","路丹","鲁丹","卢登", "路", "灯光"], ["车辆", "小车", "校车", "车", "跑车", "老婆"], ["温度"], ["湿度"], ["灯带", "等待", "登带", "带", "温带", "增大"], ["这个", "那个", "这是", "这里", "这", "这儿"]]
        self.num_list = [["全部", "所有", "所有路", "所有度"], [0, "零号", "0号", '林号路', "0", "零", "林号", "部单", "宁号","动林号", "令"], [1, "1号", "一号", '依号路', "1", "依号", "一号路", "伊号", "一号录"], [2, "二号", "二"], [3, "三号","三号路"], [4, "四号", "四"], [5, "五号","武号","无号", "五"], [6, "六号","留号","刘号", "六"], [7, "汽号","七号","气号","停七号","期号"],[8, "八号","巴号","停八号"],[9, "九号","酒","停酒号","停九号","停决号"]]

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
        car_pos = MQTTClient().mqtt_message_cache["plate_pos"]["ai/car_pos"]
        if car_pos:
            car_speech_results = f"图上共有{len(car_pos)}辆车。"
            for i, pos_list in car_pos.items():
                road = self.position.car_in_which_road(pos_list)
                building = self.position.car_close_to_which_building(pos_list)
                if road and building:
                    car_speech_results += f"{i}号小车位于{road}临近{building}。"
                else:
                    lack_info = f"小车位于{road}" if road else f"小车临近{building}"
                    car_speech_results += f"{i}号{lack_info}"
            return car_speech_results
        return f"定位失败了，重新放个位置试试呢"



    def strip_recognition(self, action, num):
        if action == "打开":
            return self.router.rgb_line_open()

        else:
            return self.router.rgb_line_close()


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
                        if area in self.position.strip_to_area_mapping_dict:
                            for item in self.position.strip_to_area_mapping_dict[area]:
                                self.router.rgb_line_control(item, [112, 274, 180])
                    else:
                        result = self.router.each_light_control(area, 0)
                        if area in self.position.strip_to_area_mapping_dict:
                            for item in self.position.strip_to_area_mapping_dict[area]:
                                self.router.rgb_line_control(item, [0, 0, 0])
                    return result
            elif action in self.actions_list[-1]:
                if building:
                    return building
            return f"请您移动手指到物体中心点"

        return f"没找到您的手指"

    def asr_controller(self, message, tts):
        action, obj, num = None, None, None
        result = None

        if isinstance(message, str):
            print(message)
            if message == "现在天色渐渐暗了":
                for i in range(7):
                    self.light_recognition("打开", i)
                    time.sleep(0.2)
                tts.text_to_speech(f"0-6号路灯已开")
                text = self.strip_recognition("打开", 0)
                tts.text_to_speech(text)
                time.sleep(0.5)
                tts.text_to_speech("暮色如墨晕染天际，一键点亮满园灯火。")
            elif message == "现在天色渐渐亮了":
                text = self.strip_recognition("关闭", 0)
                tts.text_to_speech(text)
                time.sleep(0.5)
                for i in range(7):
                    text = self.light_recognition("关闭", i)
                    time.sleep(0.2)
                tts.text_to_speech(f"0-6号路灯已关")
                # tts.text_to_speech(
                #     "晨曦穿透薄雾，智能关闭满城灯火。车流量监测系统显示，超跑轰鸣、公交缓行，不同车型数据在智慧交通平台交织，绘就早高峰流动图景。")
            return None






        for k in range(len(message)-1, -1, -1):
            item = message[k]
            if action is None:
                for group in self.actions_list:
                    if item in group:
                        action = group[0]
                        break

            if obj is None:
                for i in range(len(self.object_list) - 1, -1, -1):
                    if item in self.object_list[i]:
                        obj = self.object_list[i][0]
                        break
                # for group in self.object_list:
                #     if item in group:
                #         obj = group[0]

            if num is None:
                for group in self.num_list:
                    if item in group:
                        num = group[0]
                        break

        print(action, obj, num)
        if action and obj and (num is not None):
            if obj == "路灯":
                result = self.light_recognition(action, num)
            elif obj == "车辆":
                result = self.car_recognition()

        if action and obj:
            if obj == "灯带":
                result = self.strip_recognition(action, num)
            # if obj == "路灯":
            #     result = self.light_recognition(action, "全部")

        if obj == "车辆":
            result = self.car_recognition()
        elif obj == "温度":
            result = self.temp_recognition()
        elif obj == "湿度":
            result = self.humi_recognition()
        elif obj in self.object_list[-1] and action is not None:
            result = self.multimodal_recognition(action)

        return result

















