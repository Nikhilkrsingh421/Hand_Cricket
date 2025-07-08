import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("कैमरा नहीं खुल रहा है!")
else:
    print("कैमरा सफलतापूर्वक खुल गया है!")

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('Test Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        print("फ्रेम नहीं मिल रहा!")
        break

cap.release()
cv2.destroyAllWindows() 