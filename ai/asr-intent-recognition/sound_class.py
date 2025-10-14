"""
Author: Bill
Date Created: 2024-08-01
Description: Wake word detection and text to sound
"""
import sounddevice as sd
from scipy.io.wavfile import write
import pyttsx3
import numpy as np
from route_class import MQTTRouter


class WWD():
    def __init__(self):
        self.duration = 2
        self.samplerate = 44100
        self.router = MQTTRouter()

    def action_voice_recording(self):
        voice_name = "action.wav"
        myrecording = sd.rec(int(self.duration * self.samplerate), samplerate=self.samplerate, channels=2)
        sd.wait()
        write(f"../uploads/{voice_name}", self.samplerate, myrecording)
        self.router.send_recording_message()
        # MQTTClient().publish("ai/local/recording", voice_name)
        return voice_name

class TextToSound():
    def __init__(self):
        self.engine = pyttsx3.init()
        # 设置语速
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate - 50)
        # 设置音量
        volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', volume + 0.25)
        # 设置语音
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'zh' in voice.id:
                self.engine.setProperty('voice', voice.id)
                break

    def text_to_speech(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
