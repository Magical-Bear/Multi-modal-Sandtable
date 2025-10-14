import cv2

img = cv2.imread("../2.jpg")
print(img.shape)

boundary_dict = {  "广进门": [ [1300, 668], [1650, 668], [1650, 1000], [1300, 1000] ],
  "严出门": [[1310, 0], [1507, 0], [1507, 315], [1310, 315] ]}

for k, v in boundary_dict.items():
    for points in v:
        cv2.circle(img, points, 15, (255, 0, 255), -1)

cv2.imshow("demo", img)
cv2.imwrite("demo.png", img)
cv2.waitKey(0)
cv2.destroyAllwindows()
