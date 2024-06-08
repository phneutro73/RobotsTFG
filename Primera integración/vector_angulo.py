import json
import numpy as np
import cv2 as cv
import math

def calculate_angle(vector1, vector2):
    # Normaliza los vectores y calcula el ángulo usando el producto punto
    unit_vector1 = vector1 / np.linalg.norm(vector1)
    unit_vector2 = vector2 / np.linalg.norm(vector2)
    dot_product = np.dot(unit_vector1, unit_vector2)
    dot_product = np.clip(dot_product, -1.0, 1.0)
    angle_rad = math.acos(dot_product)
    return math.degrees(angle_rad)

def main():
    try:
        with open('../camera_calib.json') as file:
            data = json.load(file)
        camera_matrix = np.array(data['camera_matrix'])
        dist_coeffs = np.array(data['distortion_coefficients'])
    except:
        print("File not valid")

    dictionary = cv.aruco.getPredefinedDictionary(cv.aruco.DICT_ARUCO_MIP_36h12)
    arucoParams = cv.aruco.DetectorParameters()
    cap = cv.VideoCapture(1)

    robot_id = 72
    marker_id = 73

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)
        if ids is not None:
            ids = ids.flatten()

        if ids is not None and len(ids) > 0:
            cv.aruco.drawDetectedMarkers(frame, corners, ids)
            centers = [np.mean(corner[0], axis=0).astype(int) for corner in corners]

            index_robot = np.where(ids == robot_id)[0]
            index_marker = np.where(ids == marker_id)[0]

            if index_robot.size > 0 and index_marker.size > 0:
                center_robot = centers[index_robot[0]]
                center_marker = centers[index_marker[0]]
                
                # Dibujar la línea entre los centros y calcular la distancia
                cv.line(frame, tuple(center_robot), tuple(center_marker), (255, 0, 0), 2)
                distance = np.linalg.norm(center_robot - center_marker)
                mid_point = (center_robot + center_marker) // 2
                cv.putText(frame, f"{distance:.2f}px", tuple(mid_point), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Dibujar la línea de dirección del robot
                robot_corners = corners[index_robot[0]][0]
                top_right = robot_corners[1]
                top_left = robot_corners[0]
                direction_vector = top_right - top_left  # Asumimos que el vector es horizontal
                end_point = center_robot + direction_vector
                end_point = tuple(end_point.astype(int))  # Asegúrate de que end_point es un entero
                cv.arrowedLine(frame, tuple(center_robot), end_point, (0, 0, 255), 2, tipLength=0.2)

                # Calcular y mostrar el ángulo entre la dirección del robot y la línea entre centros
                center_vector = center_marker - center_robot
                angle = calculate_angle(direction_vector, center_vector)
                cv.putText(frame, f"Angle: {angle:.2f} deg", (50, 80), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
