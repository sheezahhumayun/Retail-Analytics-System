import cv2

cap = cv2.VideoCapture("sample-data/entrance.mp4")

print("Opened:", cap.isOpened())
print("FPS:", cap.get(cv2.CAP_PROP_FPS))

ret, frame = cap.read()

if ret:
    print("Frame shape:", frame.shape)

cap.release()