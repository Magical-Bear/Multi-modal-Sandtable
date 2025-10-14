import pyaudio
import wave
import threading
import time
import numpy as np
import audioop



class AudioRecorder:
    def __init__(self, output_filename="output.wav", threshold_db=68, max_record_time=20, sliding_window_size=5, end_time=1):
        self.output_filename = output_filename
        self.threshold_db = threshold_db
        self.stop_db = self.threshold_db - 10
        self.max_record_time = max_record_time
        self.sliding_window_size = sliding_window_size
        self.frames = []
        self.is_recording = False
        self.p = pyaudio.PyAudio()
        self.last_db_check_time = 0
        self.end_time = end_time

    def calculate_decibel(self, data):
        """计算分贝值"""
        try:
            rms = audioop.rms(data, 2)
            decibel = 20 * np.log10(rms)
            if decibel == -np.inf or decibel == 0:
                decibel = 40
        except:
            decibel = 40
        return decibel

    def start_recording(self):
        self.frames.clear()
        stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        print("监听中，等待声音...")

        while not self.is_recording:
            data = stream.read(1024)
            db = self.calculate_decibel(data)
            # print(f"当前分贝: {db:.2f} dB", end='\r')
            # print(db)
            #
            # record_start = input("dd")
            # if record_start == "d":
            #     self.is_recording = True
            #     start_time = time.time()
            #     self.frames.append(data)  # 录制第一块数据
            #     break


            # # 检查是否达到阈值开始录制
            if db >= self.threshold_db:
                print("\n开始录制...")
                self.is_recording = True
                start_time = time.time()
                self.frames.append(data)  # 录制第一块数据
                break

        # 开始录制
        while self.is_recording:
            data = stream.read(1024)
            self.frames.append(data)

            db = self.calculate_decibel(data)

            # 检查录制时间和分贝
            if db < self.stop_db:
                if time.time() - self.last_db_check_time > self.end_time:
                    print("\n录制停止：分贝低于阈值500毫秒。")
                    break
            else:
                self.last_db_check_time = time.time()

            if (time.time() - start_time) > self.max_record_time:
                print("\n录制停止：超过最大录制时间。")
                break

        self.is_recording = False
        stream.stop_stream()
        stream.close()

    def save_recording(self):
        with wave.open(self.output_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.frames))

    def record(self, endtime=1):
        while True:
            self.end_time = endtime
            if len(self.frames) >= 24:
                self.save_recording()
                self.frames.clear()
                break
            else:
                recording_thread = threading.Thread(target=self.start_recording)
                recording_thread.start()
                recording_thread.join()

    def terminate(self):
        self.p.terminate()

# 使用示例
if __name__ == "__main__":
    recorder = AudioRecorder()
    recorder.record()
    recorder.terminate()