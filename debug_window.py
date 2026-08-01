import cv2
import time
import mediapipe as mp
import eye_tracker
from hand_tracker import HandGestureRecognizer

def main():
    print("=== Debug Window for Eye & Hand Tracking ===")
    print("This window displays camera input with tracking overlays")
    print("Press 'q' to quit")
    
    # Initialize trackers
    try:
        tracker = eye_tracker.MediaPipeEyeTracker()
        print("✓ Eye tracker loaded")
    except Exception as e:
        print(f"✗ Eye tracker failed: {e}")
        tracker = None

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )
    hand_recognizer = HandGestureRecognizer()
    print("✓ Hand tracker loaded")

    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("✗ Camera not available")
        return

    print("✓ Camera connected")
    print("Starting debug window...")

    # Warm up camera
    for _ in range(5):
        cap.read()
        time.sleep(0.05)

    mode = 0  # 0: EYE, 1: HAND
    
    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.02)
            continue

        frame = cv2.flip(frame, 1)
        
        # Display mode indicator
        mode_text = "EYE TRACKING" if mode == 0 else "HAND TRACKING"
        cv2.putText(frame, f'Mode: {mode_text} (Press SPACE to switch)', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, 'Press Q to quit', (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if mode == 0:
            # Eye tracking mode
            if tracker:
                vector, _ = tracker.detect_gaze_upgraded(frame)
                if vector is not None:
                    status = "Tracking" 
                    color = (0, 255, 0)
                else:
                    status = "Lost"
                    color = (0, 0, 255)
                cv2.putText(frame, f'Status: {status}', (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        else:
            # Hand tracking mode
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)
            
            if results.multi_hand_landmarks:
                hand_landmarks = results.multi_hand_landmarks[0]
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
                hx, hy, gesture = hand_recognizer.process_hand_gesture(
                    hand_landmarks.landmark, 640, 480
                )
                cv2.putText(frame, f'Gesture: {gesture}', (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                cv2.putText(frame, 'No hand detected', (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('Vision Debug Window', frame)
        
        # Handle keyboard input
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):
            mode = 1 - mode  # Toggle between 0 and 1

    cap.release()
    cv2.destroyAllWindows()
    hands.close()
    print("Debug window closed")

if __name__ == "__main__":
    main()
