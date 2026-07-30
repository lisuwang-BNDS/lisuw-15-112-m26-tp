import cv2
import time
import threading
import traceback
import mediapipe as mp
import eye_tracker
from hand_tracker import HandGestureRecognizer
#decerase confidence level
#keyboarda
class VisionData:
    def __init__(self):
        self.raw_vx = None
        self.raw_vy = None
        self.hand_x = None
        self.hand_y = None
        self.hand_gesture = 'NONE'
        self.camera_status = 'searching'
        self.camera_available = False


class VisionTrackerThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        
        self.daemon = True
        self.running = True

    def run(self):
        try:
            try:
                tracker = eye_tracker.MediaPipeEyeTracker()
                print("MediaPipe loaded")
            except Exception as e:
                print(f"FAILED")
                tracker = None

            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            hand_recognizer = HandGestureRecognizer()

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("[VisionTracker] use keyboard or moouse")
                self.app.vision.camera_available = False
                return

            self.app.vision.camera_available = True
            print("[VisionTracker] sucess")

            for _ in range(5):
                cap.read()
                time.sleep(0.05)

            while self.running and getattr(self.app, 'is_running', True):
                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.02)
                    continue

                frame = cv2.flip(frame, 1)
                current_mode = getattr(self.app, 'camera_mode', 0)  # 0: EYE, 1: HAND

                if current_mode == 0:
                    if tracker:
                        vector, _ = tracker.detect_gaze_upgraded(frame)
                    else:
                        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                        vector, _ = eye_tracker.detect_gaze_upgraded(frame, eye_cascade)

                    if vector is not None:
                        self.app.vision.raw_vx, self.app.vision.raw_vy = vector
                        self.app.vision.camera_status = 'tracking'
                    else:
                        self.app.vision.raw_vx, self.app.vision.raw_vy = None, None
                        self.app.vision.camera_status = 'lost'

                elif current_mode == 1:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(rgb_frame)

                    if results.multi_hand_landmarks:
                        hand_landmarks = results.multi_hand_landmarks[0]
                        hx, hy, gesture = hand_recognizer.process_hand_gesture(
                            hand_landmarks.landmark, self.app.width, self.app.height
                        )
                        self.app.vision.hand_x, self.app.vision.hand_y = hx, hy
                        self.app.vision.hand_gesture = gesture
                    else:
                        self.app.vision.hand_x, self.app.vision.hand_y = None, None
                        self.app.vision.hand_gesture = 'NONE'

                time.sleep(0.02)  

            hands.close()
            cap.release()

        except Exception as e:
            print("wrong")
            traceback.print_exc()

    def stop(self):
        self.running = False