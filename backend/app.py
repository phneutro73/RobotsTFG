from flask import Flask, Response, request, jsonify
import cv2 as cv
import numpy as np
import json
import time
import threading
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load camera calibration data
with open('camera_calib.json') as file:
    data = json.load(file)
camera_matrix = np.array(data['camera_matrix'])
dist_coeffs = np.array(data['distortion_coefficients'])

dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
arucoParams = cv.aruco.DetectorParameters()
cap = cv.VideoCapture(1)

camera_width = 1920
camera_height = 1080
camera_frame_rate = 60

cap.set(3, camera_width)
cap.set(4, camera_height)
cap.set(5, camera_frame_rate)

current_target_index = 0  # Comienza con el primer marcador en la ruta
route = []

def send_command_to_robot(id, command):
    url = "http://192.168.1.42/command?cmd="
    
    if command == 'move_forward':
        requests.get(url + 'S')
        print("forward")
    
    elif command == 'move_backward':
        requests.get(url + 'Z')
        print("backward")

    elif command == 'move_left':
        requests.get(url + 'A')
        print("left")

    elif command == 'move_right':
        requests.get(url + 'D')
        print("right")

def calculate_angle(vector1, vector2):
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector1, unit_vector2)
    dot_product = np.clip(dot_product, -1.0, 1.0)
    angle_rad = np.arccos(dot_product)
    cross_product = np.cross(unit_vector1, unit_vector2)
    
    if cross_product < 0:
        angle_deg = 360 - np.degrees(angle_rad)
    else:
        angle_deg = np.degrees(angle_rad)

    return angle_deg

def navigate_to_marker(robot_id, target_marker_id, centers, ids, direction_vector, distance_meters):
    index_robot = np.where(ids == robot_id)[0]
    index_marker = np.where(ids == target_marker_id)[0]

    if index_robot.size > 0 and index_marker.size > 0:
        center_robot = centers[index_robot[0]]
        center_marker = centers[index_marker[0]]
        center_vector = center_marker - center_robot
        angle = calculate_angle(direction_vector, center_vector)
        
        if abs(angle) > 4:
            if angle <= 180:
                send_command_to_robot(robot_id, 'move_right')
                print('angle')
            else:
                send_command_to_robot(robot_id, 'move_left')
        elif distance_meters >= 0.3:
            send_command_to_robot(robot_id, 'move_forward')
        else:
            print("Reached target")
            return True  # Indica que ha llegado al marcador
        print(distance_meters, robot_id, target_marker_id, angle)
        
    return False  # Indica que aún no ha llegado al marcador

@app.route('/start_navigation', methods=['POST'])
def start_navigation():
    global current_target_index, route
    data = request.json
    robot_id = data['robot_id']
    target_marker_id = data['target_marker_id']
    route = [target_marker_id]  # Solo un destino para esta implementación
    current_target_index = 0  # Reset route index

    def generate_frames():
        global current_target_index

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)
            
            if ids is not None:
                ids = ids.flatten()
                
            if ids is not None and len(ids) > 0:
                centers = [np.mean(corner[0], axis=0).astype(int) for corner in corners]
                rvecs, tvecs, _ = cv.aruco.estimatePoseSingleMarkers(corners, 0.05, camera_matrix, dist_coeffs)
                cv.aruco.drawDetectedMarkers(frame, corners, ids)
                
                if current_target_index < len(route):
                    target_marker_id = route[current_target_index]
                    index_robot = np.where(ids == robot_id)[0]
                    index_marker = np.where(ids == target_marker_id)[0]
                    
                    if index_robot.size > 0 and index_marker.size > 0:
                        center_robot = centers[index_robot[0]]
                        center_marker = centers[index_marker[0]]
                        cv.line(frame, tuple(center_robot), tuple(center_marker), (255, 0, 0), 2)
                        distance_meters = np.linalg.norm(tvecs[index_robot][0] - tvecs[index_marker][0])
                        mid_point = (center_robot + center_marker) // 2
                        cv.putText(frame, f"{distance_meters:.2f}m", tuple(mid_point), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        robot_corners = corners[index_robot[0]][0]
                        top_right = robot_corners[1]
                        top_left = robot_corners[0]
                        direction_vector = top_right - top_left
                        end_point = center_robot + direction_vector
                        end_point = tuple(end_point.astype(int))
                        cv.arrowedLine(frame, tuple(center_robot), end_point, (0, 0, 255), 2, tipLength=0.2)
                        if navigate_to_marker(robot_id, target_marker_id, centers, ids, direction_vector, distance_meters):
                            current_target_index += 1  # Pasa al siguiente marcador en la ruta
                            return jsonify({'status': 'completed'})  # Return status completed
                        time.sleep(0.5)
                    
            _, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
