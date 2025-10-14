import cv2


rtsp_url = 'rtsp://admin:iot_c108c108@192.168.124.5:554/stream1'

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("无法打开RTSP流")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("无法读取帧")
        break

    cv2.imshow('RTSP Stream', frame)


    if cv2.waitKey(1) & 0xFF == ord('q'):

        break


cap.release()
cv2.destroyAllWindows()