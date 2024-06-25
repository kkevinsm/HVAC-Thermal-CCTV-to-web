from flask import Flask, render_template, Response, jsonify, request
import cv2
import numpy as np
import threading
import time

app = Flask(__name__)

average_temperature = 0
lock = threading.Lock()

def get_temperature_value(color_name):
    temperature_values = {
        'Red': (36, 45),
        'Orange': (26, 35),
        'Yellow': (16, 25),
        'Green': (6, 15),
        'Blue': (0, 5)
    }
    return temperature_values.get(color_name, (0, 0))

def detect_and_label_temperature(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    boundaries = [
        ([0, 50, 50], [10, 255, 255], 'Red'),
        ([11, 50, 50], [25, 255, 255], 'Orange'),
        ([26, 50, 50], [34, 255, 255], 'Yellow'),
        ([35, 50, 50], [85, 255, 255], 'Green'),
        ([86, 50, 50], [130, 255, 255], 'Blue')
    ]

    total_area = 0
    weighted_temp_sum = 0
    detected_rects = 0

    for (lower, upper, color_name) in boundaries:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(hsv, lower, upper)

        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                temperature_range = get_temperature_value(color_name)
                avg_temp = np.mean(temperature_range)
                weighted_temp_sum += avg_temp * area
                total_area += area
                detected_rects += 1
                temperature_label = f"{avg_temp:.1f} C"
                cv2.putText(frame, temperature_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (36, 255, 12), 2)

    if total_area > 0:
        weighted_average_temp = weighted_temp_sum / total_area
    else:
        weighted_average_temp = 0

    return frame, weighted_average_temp, detected_rects

def generate_frames():
    global average_temperature
    cap = cv2.VideoCapture('D:\\Code\\HVAC-Thermal-CCTV-to-web\\src\\ThermalExperiment.mp4')
    all_temperatures = []

    fps = 0.0

    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            break
        else:
            labeled_frame, frame_average_temp, rect_count = detect_and_label_temperature(frame)
            all_temperatures.append(frame_average_temp)

            with lock:
                average_temperature = np.mean(all_temperatures[-100:])

            text = f"Average Temp: {average_temperature:.1f} C"
            rects_text = f"Rectangles: {rect_count}"
            fps_text = f"FPS: {fps:.2f}"

            cv2.putText(labeled_frame, fps_text, (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 255), 2)
            cv2.putText(labeled_frame, rects_text, (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 255, 255), 2)
            cv2.putText(labeled_frame, text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            end_time = time.time()
            processing_time = end_time - start_time
            fps = 1 / processing_time

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


@app.route('/average_temperature')
def get_average_temperature():
    global average_temperature
    with lock:
        return jsonify({'average_temperature': average_temperature})
    
@app.route('/send_temperature', methods=['GET'])
def send_temperature():
    global average_temperature
    with lock:
        temp = average_temperature
    return jsonify({'temperature': temp})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
