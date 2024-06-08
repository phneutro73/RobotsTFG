import cv2 as cv

camera_width = 1280
camera_height = 720
camera_frame_rate = 30

cap = cv.VideoCapture(1)
cap.set(3, camera_width)
cap.set(4, camera_height)
cap.set(5, camera_frame_rate)

num = 0

while cap.isOpened():
    ret, frame = cap.read()
    if ret:
        cv.imshow('frame', cv.flip(frame,1))
        if cv.waitKey(1) & 0xFF == ord('s'):
            cv.imwrite('image{}.jpg'.format(num), frame)
            print("image saved!")
            num += 1
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

cap.release()
cv.destroyAllWindows()