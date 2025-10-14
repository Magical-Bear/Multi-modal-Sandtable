"""
Author: Bill
Date Created: 2024-08-01
Description: Get Car and Finger Position then semantic to text
"""
from shapely.geometry import Point, Polygon


def is_point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def closest_polygon(point, polygons):
    point = Point(point)
    min_distance = float('inf')
    closest_poly = None

    for name, vertices in polygons.items():
        polygon = Polygon(vertices)
        distance = point.distance(polygon)
        if distance < min_distance:
            min_distance = distance
            closest_poly = name

    return closest_poly, min_distance


class CoordinatePosition():
    def __init__(self):
        self.street_lamp_dict = {6: [[350, 100], [800, 50], [340, 550]],
                            5: [[350, 730], [520, 550], [700, 750], [500, 780]],
                            4: [[600, 480], [920, 150], [970, 400], [800, 650]],
                            3: [[350, 830], [620, 900], [820, 850], [1000, 1000], [1200, 1000], [1200, 1060],
                                [380, 1030]],
                            2: [[950, 750], [1070, 450], [1040, 120], [1220, 140], [1240, 900], [1000, 900]],
                            1: [[1340, 120], [1430, 120], [1470, 700], [1570, 750], [1570, 850], [1360, 900]]}

        self.road_dict = {"广严大道": [[800, 50], [920, 150], [400, 730], [340, 550]],
                     "至善北路": [[830, 650], [950, 400], [930, 200], [1060, 180], [1070, 450], [950, 750]],
                     "仁爱路": [[1000, 900], [1240, 900], [1200, 1000], [1000, 1000], [820, 850], [700, 750],
                                [570, 600],
                                [650, 530], [770, 650]],
                     "创业路": [[400, 730], [500, 780], [700, 750], [720, 880], [520, 900], [350, 830]],
                     "西源大道": [[1240, 1070], [1230, 0], [1330, 0], [1360, 1070]],
                     "劳动路": [[750, 0], [750, 30], [360, 100], [320, 570], [270, 570], [320, 50]],
                     "实践东路": [[350, 950], [1230, 1060], [1230, 1120], [350, 1000]]
                     }

        self.buildings_dict = {"c教": [[650, 330], [720, 230], [1000, 450], [950, 600]],
                          "b教": [[630, 340], [900, 600], [820, 750], [530, 450]],
                          "a教": [[500, 500], [780, 760], [610, 850], [400, 630]],
                          "图书馆": [[450, 20], [620, 5], [620, 275],[450,270]],
                          "和平大楼": [[1000, 100], [1300, 100], [1300, 550], [1000, 550]],
                          "操场": [[700, 890], [800, 800], [960, 940], [830, 1080]],
                          "至善大楼": [[920, 560], [1300, 560], [1300, 920], [920, 950]]
                               }

        self.buildings_description = {"c教": "这是信义大楼C教，物联网与通信工程省级实验示范中心，也是我们沙盘的所在地哦。",
                                      "b教": "这是仁爱大楼B教，名字取自孙中山先生三民主义仁爱二字。",
                                      "a教": "这是忠孝大楼A教。名字取自孙中山先生，三民主义中忠孝二字。忠孝大楼有着欧式建筑特有的圆形穹顶，圆形连廊将东西两个部分有机链接起来，成为整个楼的核心交通体系。",
                                      "图书馆": "这是图书馆，作为校园的地标性建筑之一，更是被称为锦城白宫。",
                                      "和平大楼": "这是和平大楼，是锦城学院的行政大楼，电子信息学院和物联网工程系的老师们就位于和平楼西楼。",
                                      "至善大楼": "这是至善大楼，来源于校训-止于至善。止于至善理解为不断追求卓越和完善的过程。",
                                      "操场": "这是东区操场，可以满足同学们跑步锻炼的需求。",
                                      "四维大楼": "这是四维大楼，取名来自礼、义、廉、耻国之四维。四维大楼还可以满足同学们各个维度的需求",
                                      }

        self.strip_to_area_mapping_dict = {
            6: [0, 1],
            3: [2, 4],
            2: [3, 5]
        }

    def point_in_surface(self, point: list, surface: dict):
        for name, vertices in surface.items():
           if is_point_in_polygon(point, vertices):
               return name
        return None


    def point_close_surface(self, point: list, surface: dict, threshold=1000):
        closest_poly, distance = closest_polygon(point, surface)
        print(closest_poly, distance)
        if distance < threshold:
            return closest_poly
        return None

    def convert_xyxyxyxy_to_center_xy(self, obb: list):
        left_top = obb[0]
        right_button = obb[2]
        center_x = (left_top[0] + right_button[0]) // 2
        center_y = (left_top[1] + right_button[1]) // 2
        return [center_x, center_y]

    def finger_in_which_area(self, finger_pos: list):
        # xy_pos = self.convert_xyxyxyxy_to_center_xy(finger_pos)
        # return self.point_in_surface(xy_pos, self.street_lamp_dict)
        xy_pos = self.convert_xyxyxyxy_to_center_xy(finger_pos)
        distance = self.point_close_surface(xy_pos, self.street_lamp_dict, 100)
        return distance

    def finger_in_which_car(self, finger_pos: list, car_pos: dict):
        # TODO padding car pos
        xy_pos = self.convert_xyxyxyxy_to_center_xy(finger_pos)
        return self.point_in_surface(xy_pos, car_pos)

    def finger_in_which_building(self, finger_pos: list):
        # xy_pos = self.convert_xyxyxyxy_to_center_xy(finger_pos)
        # building = self.point_in_surface(xy_pos, self.buildings_dict)
        # if building:
        #     return self.buildings_description[building]
        xy_pos = self.convert_xyxyxyxy_to_center_xy(finger_pos)
        building = self.point_close_surface(xy_pos, self.buildings_dict, 350)
        if building:
            return self.buildings_description[building]
        return None

    def car_in_which_road(self, car_pos:list):
        xy_pos = self.convert_xyxyxyxy_to_center_xy(car_pos)
        return self.point_in_surface(xy_pos, self.road_dict)

    def car_close_to_which_building(self, car_pos:list):
        xy_pos = self.convert_xyxyxyxy_to_center_xy(car_pos)
        return self.point_close_surface(xy_pos, self.buildings_dict)

