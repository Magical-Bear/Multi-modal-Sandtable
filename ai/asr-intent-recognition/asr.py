import base64
import os.path
import urllib
import requests
import json
import jieba
from fuzzy_search import fuzzy_search
from mqtt_class import MQTTClient

mqtt_client = MQTTClient()

class AudioSpeechReco():
    def __init__(self):
        self.API_KEY = "TXmPPmNtVm09EOXMbLablRpN"
        self.SECRET_KEY = "nMMIAFOt6AjGNmhDKFJgE7pIztaD4ggD"
        self.url = "https://vop.baidu.com/server_api"

    def get_file_content_as_base64(self, path, urlencoded=False):
        """
        获取文件base64编码
        :param path: 文件路径
        :param urlencoded: 是否对结果进行urlencoded
        :return: base64编码信息
        """
        with open(path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf8")
            if urlencoded:
                content = urllib.parse.quote_plus(content)
        return content

    def get_access_token(self):
        """
        使用 AK，SK 生成鉴权签名（Access Token）
        :return: access_token，或是None(如果错误)
        """
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.API_KEY, "client_secret": self.SECRET_KEY}
        return str(requests.post(url, params=params).json().get("access_token"))

    def infer(self, path="output.wav"):
        if os.path.exists(path):
            base64_str = self.get_file_content_as_base64(path)
            src_len = os.path.getsize(path)

            payload = json.dumps({
                "format": "wav",
                "rate": 16000,
                "channel": 1,
                "cuid": "yHfzfy7cGkBnzAQFatlnLqCVkJPM9bMv",
                "speech": base64_str,
                "len": src_len,
                "token": self.get_access_token()
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = requests.request("POST", self.url, headers=headers, data=payload)

            response = json.loads(response.text)

            if response["err_msg"] == "success.":

                return response["result"][0]
            else:
                return -1
        return -2

    def is_waked(self):
        result = self.infer()[:-1][:4]
        if isinstance(result, str):
            result = result[:-1][:4]
            similarity = fuzzy_search(result)
            triggled = True if similarity >= 0.5 else False
            return triggled
        return False

    def tokenizer(self):
        try:
            result = self.infer()[:-1]
            if isinstance(result, str):
                if "现在天色渐渐暗了" in result:
                    return "现在天色渐渐暗了"
                elif "现在天色渐渐亮了" in result:
                    return "现在天色渐渐亮了"
                else:
                    seg_list = [token for token in jieba.cut(result, cut_all=True)]
                    print(seg_list)
                    return seg_list
            return []
        except Exception:
            return []




# asr = AudioSpeechReco()
# result = asr.infer()
# print(result)