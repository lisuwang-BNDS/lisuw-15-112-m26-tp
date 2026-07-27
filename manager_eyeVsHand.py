import cv2
import time
import queue
import mediapipe as mp

import eye_tracker
from hand_tracker import HandGestureRecognizer

def run_unified_camera_process(queue_out, mode_value, stop_event, screen_width, screen_height):
    try:
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        mp_hands = mp.solutions.hands
        mp_drawing = mp.solutions.drawing_utils
        hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        hand_recognizer = HandGestureRecognizer()

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            try: queue_out.put_nowait(('error', 'Cannot open camera'))
            except: pass
            return

    
        for _ in range(5):
            cap.read()
            time.sleep(0.05)

        print("[VisionManager] ")

        frame_counter = 0

        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            current_mode = mode_value.value  

            
            if current_mode == 0:
                vector, _ = eye_tracker.detect_gaze_upgraded(frame, eye_cascade)
                if vector is None:
                    try: queue_out.put_nowait(('eye', None, None))
                    except: pass
                    cv2.putText(frame, "EYE: LOST", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    vx, vy = vector
                    try: queue_out.put_nowait(('eye', vx, vy))
                    except: pass
                    cv2.putText(frame, f"EYE: ({vx:.2f}, {vy:.2f})", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            
            elif current_mode == 1:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    hand_landmarks = results.multi_hand_landmarks[0]
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    hx, hy, gesture = hand_recognizer.process_hand_gesture(hand_landmarks.landmark, screen_width, screen_height)
                    try: queue_out.put_nowait(('hand', hx, hy, gesture))
                    except: pass
                    cv2.putText(frame, f"HAND: {gesture}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                else:
                    try: queue_out.put_nowait(('hand', None, None, 'NONE'))
                    except: pass
                    cv2.putText(frame, "HAND: SEARCHING", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            
            # frame_counter += 1
            # if frame_counter % 2 == 0:
            #     small_frame = cv2.resize(frame, (160, 120))
            #     ret, jpg_buf = cv2.imencode('.jpg', small_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            #     if ret:
            #         try: queue_out.put_nowait(('frame', jpg_buf.tobytes()))
            #         except: pass

            time.sleep(0.01)

        hands.close()
        cap.release()
    except Exception as e:
        print(f"[error]: {e}")