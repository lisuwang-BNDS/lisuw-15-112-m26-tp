
import cv2
import math
import time
from collections import deque
import mediapipe as mp


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class HandGestureRecognizer:
    def __init__(self):
        self.history_points = deque(maxlen=8)
        self.last_swipe_time = 0

    @staticmethod
    def calculate_vector_angle_3d(p1, p2, p3):
        
        u = (p2.x - p1.x, p2.y - p1.y, p2.z - p1.z)
        v = (p3.x - p2.x, p3.y - p2.y, p3.z - p2.z)

        dot_product = u[0]*v[0] + u[1]*v[1] + u[2]*v[2]
        norm_u = math.sqrt(u[0]**2 + u[1]**2 + u[2]**2)
        norm_v = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)

        if norm_u * norm_v == 0:
            return 0.0

        cos_theta = max(-1.0, min(1.0, dot_product / (norm_u * norm_v)))
        return math.degrees(math.acos(cos_theta))

    def detect_finger_states(self, landmarks):
        
        angles = [
            self.calculate_vector_angle_3d(landmarks[2], landmarks[3], landmarks[4]),  
            self.calculate_vector_angle_3d(landmarks[5], landmarks[6], landmarks[8]),   
            self.calculate_vector_angle_3d(landmarks[9], landmarks[10], landmarks[12]), 
            self.calculate_vector_angle_3d(landmarks[13], landmarks[14], landmarks[16]),
            self.calculate_vector_angle_3d(landmarks[17], landmarks[18], landmarks[20]) 
        ]
        return [angle < 30.0 for angle in angles]

    # def detect_dynamic_swipe(self, current_x, current_y):
        
    #     now = time.time()
    #     self.history_points.append((current_x, current_y, now))

    #     if now - self.last_swipe_time < 0.4 or len(self.history_points) < 6:
    #         return None

    #     first_x, first_y, first_t = self.history_points[0]
    #     dx = current_x - first_x
    #     dy = current_y - first_y
    #     dt = now - first_t

    #     if dt <= 0:
    #         return None

    #     velocity = math.sqrt(dx**2 + dy**2) / dt

    #     if velocity > 500 and math.sqrt(dx**2 + dy**2) > 120:
    #         if abs(dx) > abs(dy) * 1.25:
    #             self.last_swipe_time = now
    #             self.history_points.clear()
    #             return 'SWIPE_RIGHT' if dx > 0 else 'SWIPE_LEFT'
    #         elif abs(dy) > abs(dx) * 1.25:
    #             self.last_swipe_time = now
    #             self.history_points.clear()
    #             return 'SWIPE_DOWN' if dy > 0 else 'SWIPE_UP'

    #     return None

    def process_hand_gesture(self, landmarks, width, height):
        
        states = self.detect_finger_states(landmarks)
        index_tip = landmarks[8]
        screen_x = int(index_tip.x * width)
        screen_y = int(index_tip.y * height)

        # swipe = self.detect_dynamic_swipe(screen_x, screen_y)
        # if swipe:
        #     return screen_x, screen_y, swipe

        if states[1] and not states[2] and not states[3] and not states[4]:
            thumb_tip = landmarks[4]
            index_mcp = landmarks[5]
            dist = math.sqrt((thumb_tip.x - index_mcp.x)**2 + (thumb_tip.y - index_mcp.y)**2)
            
            if dist < 0.08:  
                return screen_x, screen_y, 'PISTOL_FIRE'
            return screen_x, screen_y, 'PISTOL_AIM'

        thumb_tip = landmarks[4]
        pinch_dist = math.sqrt((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)
        if pinch_dist < 0.05:
            return screen_x, screen_y, 'PINCH'

        if states[1]:
            return screen_x, screen_y, 'POINT'
        
        if not any(states):
            return screen_x, screen_y, 'FIST'

        return screen_x, screen_y, 'NONE'


