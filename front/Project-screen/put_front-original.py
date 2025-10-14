from flask import Flask, Response
import cv2

# 创建 Flask 应用
app = Flask(__name__)


# 视频帧生成器
def generate_frames():
    # 替换为你的 RTSP 地址
    cap = cv2.VideoCapture("rtsp://admin:iot_c108c108@192.168.124.5:554/stream1")

    if not cap.isOpened():
        print("Error: Cannot access the video stream.")
        return

    while True:
        success, frame = cap.read()
        if not success:
            print("Error: Failed to read frame.")
            break
        else:
            # 将帧编码为 JPEG 格式
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # 生成符合 MJPEG 流格式的帧数据
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


# 根路由，直接返回视频流
@app.route('/')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 主函数
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5200)
