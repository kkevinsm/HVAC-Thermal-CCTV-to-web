import cv2
import numpy as np

def get_temperature_label(color_name):
    temperature_labels = {
        'Red': '80-100 c',
        'Orange': '60-79 c',
        'Yellow': '40-59 c',
        'Green': '20-39 c',
        'Blue': '0-19 c'
    }
    return temperature_labels.get(color_name, 'warna')

def detect_and_label_temperature(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    boundaries = [
        ([0, 50, 50], [10, 255, 255], 'Red'),
        ([11, 50, 50], [25, 255, 255], 'Orange'),
        ([26, 50, 50], [34, 255, 255], 'Yellow'),
        ([35, 50, 50], [85, 255, 255], 'Green'),
        ([86, 50, 50], [130, 255, 255], 'Blue')
    ]

    for (lower, upper, color_name) in boundaries:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(hsv, lower, upper)

        output = cv2.bitwise_and(frame, frame, mask=mask)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                temperature_label = get_temperature_label(color_name)
                cv2.putText(frame, temperature_label, (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    return frame

cap = cv2.VideoCapture('/Users/devaraya/Documents/thermalvideocctv/src/ThermalExperiment2.mp4')

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fps = int(cap.get(cv2.CAP_PROP_FPS))

out = cv2.VideoWriter('output_video.avi', cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        labeled_frame = detect_and_label_temperature(frame)
        out.write(labeled_frame)

        cv2.imshow('THERMAL CCTV', labeled_frame)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
