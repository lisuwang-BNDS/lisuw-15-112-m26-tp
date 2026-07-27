import cv2
import mediapipe as mp

class MediaPipeEyeTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.RIGHT_IRIS = 473
        self.RIGHT_L = 362
        self.RIGHT_R = 263
        self.RIGHT_TOP = 386
        self.RIGHT_BOTTOM = 374

    def detect_gaze_upgraded(self, frame, eye_cascade=None):

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None, frame

        landmarks = results.multi_face_landmarks[0].landmark

        iris = landmarks[self.RIGHT_IRIS]
        eye_left = landmarks[self.RIGHT_L]
        eye_right = landmarks[self.RIGHT_R]
        eye_top = landmarks[self.RIGHT_TOP]
        eye_bottom = landmarks[self.RIGHT_BOTTOM]

        eye_width = eye_right.x - eye_left.x
        if eye_width <= 0:
            return None, frame
        vector_x = (iris.x - eye_left.x) / eye_width

        eye_height = eye_bottom.y - eye_top.y
        if eye_height <= 0:
            return None, frame
        vector_y = (iris.y - eye_top.y) / eye_height

        vector_x = max(0.0, min(1.0, vector_x))
        vector_y = max(0.0, min(1.0, vector_y))

        abs_iris_x = int(iris.x * w)
        abs_iris_y = int(iris.y * h)
        cv2.circle(frame, (abs_iris_x, abs_iris_y), 3, (0, 0, 255), -1)

        return (vector_x, vector_y), frame