import multiprocessing as mp
import cv2
import os
import time


def restrain(value, lo, hi):
    return max(lo, min(hi, value))




def scale_vector_to_screen(x, y, screen_width, screen_height):
    if x is None or y is None:
        return None, None
    scaledX = int(x * screen_width)
    scaledY = int(y * screen_height)
    scaledX = restrain(scaledX, 20, max(20, screen_width - 20))
    scaledY = restrain(scaledY, 20, max(20, screen_height - 20))
    return scaledX, scaledY

#some knowledge obtained from gemini flash and https://www.analyticsvidhya.com/blog/2022/10/face-detection-using-haar-cascade-using-python/
def detect_gaze_upgraded(frame, eye_cascade):
    frame = cv2.flip(frame, 1) 
    monitor = frame.copy()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=5) #with gemini flash
    if len(eyes) == 0:
        cv2.putText(
            monitor,
            'no eye here',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )
        return None, monitor
    ex, ey, ew, eh = max(eyes, key=lambda b: b[2] * b[3]) #eye with largests area
    cv2.rectangle(monitor, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    eye_roi = frame[ey:ey + eh, ex:ex + ew]#row - y, col - x
    eye_blur = cv2.GaussianBlur(eye_roi, (7, 7), 0)

    _, threshold = cv2.threshold(eye_blur, 70, 255, cv2.THRESH_BINARY_INV)
    cv2.imshow('Eye', threshold)
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None, monitor

    largest = max(contours, key=cv2.contourArea)
    moments = cv2.moments(largest)

    if moments['m00'] != 0:
        pupil_in_eye_x = moments['m10'] / moments['m00']
        pupil_in_eye_y = moments['m01'] / moments['m00']
    else:
        pupil_in_eye_x = ew / 2.0
        pupil_in_eye_y = eh / 2.0

    vector_x = restrain(pupil_in_eye_x / float(ew), 0.0,1.0)
    vector_y = restrain(pupil_in_eye_y / float(eh),0.0,1.0)

    abs_pupil_x = int(ex + pupil_in_eye_x)
    abs_pupil_y = int(ey + pupil_in_eye_y)
    cv2.circle(monitor, (abs_pupil_x, abs_pupil_y), 4, (0, 0, 255), -1)

    cv2.putText(
        monitor,
        f' ({vector_x:.3f}, {vector_y:.3f})',
        (ex, max(20, ey - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 255, 0),
        1,
    )

    return (vector_x, vector_y), monitor


#reference from https://opencv-opencv.mintlify.app/modules/videoio. some code here are done with copoilot，https://docs.python.org/3/library/queue.html
def run_camera_process(queue, stop_event, screen_width, screen_height):

    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        queue.put(('error', 'Unable to open the webcam.'))
        return

    for _ in range(5):
        cap.read()
        time.sleep(0.05)

    cv2.namedWindow("Eye Tracker Monitor", cv2.WINDOW_AUTOSIZE)

    while not stop_event.is_set():
        ok, frame = cap.read()
        if not ok:
            queue.put(('error', 'Camera frame read failed.'))
            break

        vector, monitor_frame = detect_gaze_upgraded(frame, eye_cascade)
        cv2.imshow("Eye Tracker Monitor", monitor_frame)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        if vector is None:
            queue.put(('point', None, None))
        else:
            vx, vy = vector
            sx, sy = scale_vector_to_screen(vx, vy, screen_width, screen_height)
            queue.put(('point', sx, sy))

        time.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()