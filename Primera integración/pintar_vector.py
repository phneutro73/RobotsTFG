import numpy as np
import cv2 as cv
import math
import json

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

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        corners, ids, rejected = cv.aruco.detectMarkers(gray_frame, dictionary, parameters=arucoParams)

        if ids is not None and len(ids) > 0:
            cv.aruco.drawDetectedMarkers(frame, corners, ids)
            for i, corner in enumerate(corners):
                # Calcular centro del marcador
                center = tuple(np.mean(corner[0], axis=0).astype(int))
                # Esquinas del marcador
                top_left = corner[0][0]
                top_right = corner[0][1]
                bottom_right = corner[0][2]
                bottom_left = corner[0][3]

                # Determinar la orientación más cercana al eje horizontal o vertical
                # Ejemplo: Usando el lado superior
                vector_horizontal = top_right - top_left
                if np.abs(vector_horizontal[0]) > np.abs(vector_horizontal[1]):
                    # Lado superior es más horizontal
                    direction = (int(vector_horizontal[0]), 0)
                else:
                    # Lado lateral es más vertical
                    direction = (0, int(vector_horizontal[1]))

                # Punto de fin basado en el vector
                end_point = (center[0] + direction[0], center[1] + direction[1])

                # Dibujar la línea de dirección
                cv.arrowedLine(frame, center, end_point, (0, 0, 255), 2, tipLength=0.2)

        cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()

