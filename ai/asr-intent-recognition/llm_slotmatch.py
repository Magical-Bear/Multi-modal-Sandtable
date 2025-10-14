import requests


class ChatLLMs:
    def __init__(self, llm_name: str="deepseek-ai/DeepSeek-V3"):
        self.llm_name = llm_name
        self.headers = {
            "Authorization": "Bearer sk-hopohzwnqqljfijpmsqfnhyaykvlbvlihvgqrskavvqzifra",
            "Content-Type": "application/json"
        }

        self.url = "https://api.siliconflow.cn/v1/chat/completions"

    def chat_llm(self, system_prompt: str, user_prompt: str):
        try:
            payload = {
                "model": self.llm_name,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
                "stream": False,
                "max_tokens": 512,
                "stop": ["null"],
                "temperature": 0.7,
                "top_p": 0.7,
                "top_k": 50,
                "frequency_penalty": 0.5,
                "n": 1,
                "response_format": {"type": "text"},
                "tools": [
                    {
                        "type": "function",
                        "function": {
                            "description": "<string>",
                            "name": "<string>",
                            "parameters": {},
                            "strict": False
                        }
                    }
                ]
            }
            response = requests.request("POST", self.url, json=payload, headers=self.headers).json()
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            return None

llm = ChatLLMs("deepseek-ai/DeepSeek-V3")
system_prompt = f"""
你是语音识别错误修复和槽填充专家，请按照要求修复语音识别错误
你会被提供语音识别后的短句,你的任务是在不引起更多错误的前提下纠正有把握纠正的同音或者读音相近的错别字，你必须给出推理的过程。

你应该按照下面的流程一步步的进行判断:(1)梳理句子的结构并且断句(2)判断句子是否有同音错别字(3)如果有错别字则将转化为有声调的汉语拼音(4)根据汉语拼音和上下文推断出候选的答案(5)选择上下文合理的答案,如果改变词的读音差别过大或者对答案没把握可以保持原句不变直接输出，答案用[]包裹,并且前面用<改>,<原>来表示是否修改

输入:达开一号路灯
断句：达开 一号 路灯 推理:(1) "达开" 有问题（(2)"达开"的拼音是"da3 kai1"(3)"da3 kai1"的候选词有"打开"、"大开","答开"(4)最合适的选项为"打开",打开最合适，进行改写
结果:{{"repaired": {{"打开 一号 路灯"}}}}

输入:小车在哪儿
断句:小车 在 哪儿 推理:(1)句子没有语病，因此分词输出
结果：{{"src": {{"打开 一号 路灯"}}}}


"""
response = llm.chat_llm("你很全能", "告诉我法国首都")
