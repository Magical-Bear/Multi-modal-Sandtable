"""
Author: Bill
Date Created: 2024-08-01
Description: Main function for inference
"""
from coordinate_class import CoordinatePosition
from mqtt_class import MQTTClient
from route_class import MQTTRouter
from slot_class import NLPSlot
from sound_class import TextToSound
from recoder import AudioRecorder
from asr import AudioSpeechReco
import jieba

mqtt_client = MQTTClient()
coordinate = CoordinatePosition()
router = MQTTRouter()
slot = NLPSlot()
tts = TextToSound()
recorder = AudioRecorder()
asr = AudioSpeechReco()


def one_loop():
    # recorder.record(endtime=0.7)
    # if asr.is_waked() :wqis False:
    #     return
    #::peech("我在")
    recorder.record()
    new_arrival = asr.tokenizer()
    asr_result = slot.asr_controller(new_arrival, tts)

    if asr_result:
        tts.text_to_speech(asr_result)




#star_time = time.time()


while True:
    one_loop()
