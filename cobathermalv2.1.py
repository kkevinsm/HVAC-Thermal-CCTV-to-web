from flask import Flask, render_template, Response
import cv2
import numpy as np

app = Flask(__name__)

def get_temperature_value(color_name):
    temperature_values = {
        'Red': (35, 45),
        'Orange': (25, 34),
        'Yellow': (15, 24),
        'Green': (6, 14),
        'Blue': (0, 5)
    }
    return temperature_values.get(color_name, (0, 0))

def calculate_average_temperature(temperature_list):
    if not temperature_list:
        return 0
    total_sum = sum(temperature_list)
    return total_sum / len(temperature_list)

def detect_and_label_temperature(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    boundaries = [
        ([0, 50, 50], [10, 255, 255], 'Red'),
        ([11, 50, 50], [25, 255, 255], 'Orange'),
        ([26, 50, 50], [34, 255, 255], 'Yellow'),
        ([35, 50, 50], [85, 255, 255], 'Green'),
        ([86, 50, 50], [130, 255, 255], 'Blue')
    ]

    temperature_values = []

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
                temperature_range = get_temperature_value(color_name)
                average_temperature = sum(temperature_range) / 2
                temperature_values.append(average_temperature)
                temperature_label = f"{average_temperature:.1f} c"
                cv2.putText(frame, temperature_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36, 255, 12), 2)

    return frame, temperature_values

def generate_frames():
    cap = cv2.VideoCapture('C:\\xampp\htdocs\HVAC-Thermal-CCTV-to-web\src\ThermalExperiment.mp4')
    all_temperatures = []

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            labeled_frame, frame_temperatures = detect_and_label_temperature(frame)
            all_temperatures.extend(frame_temperatures)

            average_temperature = calculate_average_temperature(all_temperatures)
            cv2.putText(labeled_frame, f"Average Temp: {average_temperature:.1f} c", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            ret, buffer = cv2.imencode('.jpg', labeled_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('bukanindex.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True, port=5005)
