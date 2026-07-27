#other complexity in the leve itself (feature, plaftform / physics)
#backgtound
#handtracking mediapipe()

#diamond square

# other complexity in the leve itself (feature, plaftform / physics)
# background
# handtracking mediapipe()
# diamond square
# other complexity in the leve itself (feature, plaftform / physics)
# background
# handtracking mediapipe()
# diamond square
import io
import time
import queue

import threading
import multiprocessing as mp
from PIL import Image
from cmu_graphics import *
import random
import eye_tracker
import manager_eyeVsHand   

Samplesize_need = 20


class IntroLogo:
    def __init__(self):
        self.time = 0              
        self.opacity = 0            
        self.opacity_for_text = 0   
        self.glitching = False
        self.glitch_time = 0
        self.flashingx = 0
        self.flashingy = 0
        self.glitch_slices = []     

    def change(self, app):
        self.time += 1
        if self.opacity < 100:
            self.opacity = min(100, (self.opacity + 0.7))
        if self.opacity > 60 and self.opacity_for_text < 100:
            self.opacity_for_text = min(100, (self.opacity_for_text + 1.3))
        if not self.glitching and random.random() < 0.07 or self.time < 30:
            self.glitching = True
            self.glitch_time = random.randint(2, 5)  

        if self.glitching:
            self.glitch_time -= 1
            self.flashingx = random.randint(-8, 8)
            self.flashingy = random.randint(-3, 3)
            self.glitch_slices = []
            for i in range(random.randint(1, 4)):
                y = random.randint(app.height // 2 - 80, app.height // 2 + 80)
                h = random.randint(3, 18)
                dx = random.randint(-30, 30)
                self.glitch_slices.append((y, h, dx))
            if self.glitch_time <= 0:
                self.glitching = False
                self.flashingx = 0
                self.flashingy = 0
                self.glitch_slices = []
        if self.time > 420:
            app.state = 'menu'
            app.intro_sound.pause()

    def jump(self, app, key):
        if key in ['space', 'enter']:
            app.state = 'menu'
            app.intro_sound.pause()

    def draw(self, app):
        drawRect(0, 0, app.width, app.height, fill='black')
        cx = app.width / 2
        cy = app.height / 2 - 30
        if self.opacity > 0:
            text = "E N V I S I O N"
            if self.glitching:
                drawLabel(text, cx + self.flashingx - 6, cy + self.flashingy - 2, fill='magenta', size=64, bold=True, font='monospace', opacity=self.opacity * 0.75)
                drawLabel(text, cx + self.flashingx + 6, cy + self.flashingy + 2, fill='cyan', size=64, bold=True, font='monospace', opacity=self.opacity * 0.75)
            if self.glitching and random.random() < 0.4:
                color = 'cyan' 
            else:
                color = 'white'
            drawLabel(text, cx + self.flashingx, cy + self.flashingy, fill=color, size=64, bold=True, font='monospace', opacity=self.opacity)
            if self.glitching:
                for y, h, dx in self.glitch_slices:
                    slice_color = random.choice(['cyan', 'magenta', 'black', 'white'])
                    drawRect(cx - 350 + dx, y, 700, h, fill=slice_color, opacity=80)

        if self.opacity_for_text > 0:
            w = 360 * (self.opacity_for_text / 100)
            if w > 1:
                drawLine(cx - w/2, cy + 55, cx + w/2, cy + 55, fill='cyan', opacity=self.opacity_for_text)
            drawLabel("ASSISTIVE EYE-TRACKING ADVENTURE FOR 112 PROJECT", cx, cy + 85, fill='magenta', size=13, bold=True, font='monospace', opacity=self.opacity_for_text)

        if self.time > 40:
            pulse_opacity = 30 + int(40 * ((self.time % 30) / 30.0))
            drawLabel("[ PRESS SPACE TO START ]", cx, app.height - 70, fill='gray', size=12, font='monospace', opacity=pulse_opacity)


class Character:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy


class menu_triggerer:
    def __init__(self, x, y, w, h):
        self.left = x
        self.top = y
        self.w = w
        self.h = h

    def collide(self, other):
        if not isinstance(other, Character):
            return False
        if self.left <= other.x <= (self.left + self.w) and self.top <= other.y <= (self.top + self.h):
            return True
        return False

    def near(self, other, margin=30):
        if not isinstance(other, Character):
            return False
        return (self.left - margin <= other.x <= self.left + self.w + margin and
                self.top - margin <= other.y <= self.top + self.h + margin)


class DemoTarget:
    def __init__(self, x, y, radius=45, label="TARGET"):
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.progress = 0.0
        self.activated = False
        self.flash_timer = 0

    def check_hover(self, cx, cy, is_pinching=False, mode=0):
        if cx is None or cy is None:
            self.progress = max(0.0, self.progress - 0.05)
            return False

        dist = ((cx - self.x) ** 2 + (cy - self.y) ** 2) ** 0.5
        if dist <= self.radius:
            if mode == 0:
                self.progress = min(1.0, self.progress + 0.04)
            else:
                if is_pinching:
                    self.progress = 1.0
                else:
                    self.progress = min(0.8, self.progress + 0.05)

            if self.progress >= 1.0 and not self.activated:
                self.activated = True
                self.flash_timer = 15
                return True
        else:
            self.progress = max(0.0, self.progress - 0.04)
            if self.progress <= 0.01:
                self.progress = 0.0
                self.activated = False

        return False


def get_gazerecorder_style_pointer(app, current_vx, current_vy):
    if not app.calib_raw_results:
        return app.width // 2, app.height // 2

    GrandWeight = 0.0
    screenX = 0.0
    screenY = 0.0
    for target_id, calib_vector in app.calib_raw_results.items():
        calib_vx, calib_vy = calib_vector
        screen_pos = app.calib_targets[target_id]

        dist = ((current_vx - calib_vx) ** 2 + (current_vy - calib_vy) ** 2) ** 0.5

        if dist < 0.03:
            return screen_pos[0], screen_pos[1]

        weight = 1.0 / (dist ** 2)
        GrandWeight += weight
        screenX += screen_pos[0] * weight
        screenY += screen_pos[1] * weight

    if GrandWeight == 0: 
        return app.width // 2, app.height // 2

    return int(screenX / GrandWeight), int(screenY / GrandWeight)


def _finish_current_point_capture(app):
    if len(app.stable_samples) < Samplesize_need:
        return

    avg_vx = sum(p[0] for p in app.stable_samples) / len(app.stable_samples)
    avg_vy = sum(p[1] for p in app.stable_samples) / len(app.stable_samples)

    current_target_id = app.calib_order[app.calib_index]
    app.calib_raw_results[current_target_id] = (avg_vx, avg_vy)

    app.stable_samples = []
    app.recording_data = False
    app.calib_index += 1

    if app.calib_index >= len(app.calib_order):
        app.state = 'demo'
        app.camera_message = 'Complete!'
    else:
        app.camera_message = 'Look at next point and press space.'


def _camera_queue_listener(app):
    while not getattr(app, 'stop_event', None).is_set():
        try:
            while not app.camera_queue.empty():
                payload = app.camera_queue.get_nowait()
                if not payload: 
                    continue

                kind = payload[0]
                with app.lock:
                    if kind in ('eye', 'point'):
                        _, vx, vy = payload
                        app.raw_vx, app.raw_vy = vx, vy
                        app.camera_status = 'tracking' if vx is not None else 'lost'
                    elif kind == 'hand':
                        _, hx, hy, gesture = payload
                        app.hand_x, app.hand_y, app.hand_gesture = hx, hy, gesture
                    elif kind == 'frame':
                        _, frame_bytes = payload
                        app.latest_frame_bytes = frame_bytes
                    elif kind == 'error':
                        app.raw_vx, app.raw_vy = None, None
                        app.camera_status = 'error'
            time.sleep(0.01)
        except Exception:
            time.sleep(0.01)


def onAppStart(app):
    app.width = 1500
    app.height = 1000
    app.stepsPerSecond = 50
    app.stop_event = mp.Event()
    app.lock = threading.Lock()

    app.raw_vx, app.raw_vy = None, None
    app.gaze_x, app.gaze_y = None, None

    app.hand_x, app.hand_y = None, None
    app.hand_gesture = 'NONE'

    app.latest_frame_bytes = None
    app.camera_cmu_image = None
    app.step_counter = 0

    app.state = 'intro'
    url_intro = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/Future Noir.mp3'
    app.intro_sound = Sound(url_intro)
    app.intro_sound.play(loop=True)
    app.intro = IntroLogo()

    url_menu_walking = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/walking_menu.ogg'
    app.menu_walking_sound = Sound(url_menu_walking)

    app.leftest_top_building = menu_triggerer(8, 8, 236, 418)
    app.hangin_neonlight = menu_triggerer(254, 50, 42, 185)
    app.groundwater = menu_triggerer(50, 503, 60, 36)
    app.leftest_bottom_building = menu_triggerer(14, 624, 475, 319)
    app.fence = menu_triggerer(505, 752, 369, 182)
    app.rightest_bottom_building = menu_triggerer(882, 683, 436, 281)
    app.middle_upper_building = menu_triggerer(565, 6, 250, 419)
    app.rightest_upper_building = menu_triggerer(882, 4, 314, 424)
    app.corridor_between_upper = menu_triggerer(825, 21, 49, 349)
    app.right_light = menu_triggerer(1216, 238, 62, 178)
    app.left_light = menu_triggerer(495, 6, 54, 160)
    app.trash_can = menu_triggerer(523, 308, 37, 52)
    app.road = menu_triggerer(814, 507, 69, 160)
    app.alarm_sign = menu_triggerer(1328, 174, 157, 128)
    app.monitor_camera = menu_triggerer(1330, 688, 38, 56)
    app.triggers_menu = [
        app.leftest_top_building, app.hangin_neonlight, app.groundwater,
        app.leftest_bottom_building, app.fence, app.rightest_bottom_building,
        app.middle_upper_building, app.rightest_upper_building, app.corridor_between_upper,
        app.right_light, app.left_light, app.trash_can, app.alarm_sign, app.monitor_camera
    ]

    app.character = Character(830, 600)
    app.url = '/Users/lisuwang/untitled folder/112Projec/assets/images/Menu page/Menu page 1.png'

    app.demo_score = 0
    app.demo_targets = [
        DemoTarget(350, 300, 50, "ALPHA"),
        DemoTarget(1150, 300, 50, "BETA"),
        DemoTarget(450, 700, 50, "GAMMA"),
        DemoTarget(1050, 700, 50, "DELTA"),
        DemoTarget(750, 500, 60, "CORE")
    ]

    app.calib_targets = {
        '1': (100, 100), '2': (app.width/2, 100), '3': (app.width - 100, 100),
        '4': (100, app.height/2), '5': (app.width/2, app.height/2), '6': (app.width - 100, app.height/2),
        '7': (100, app.height - 100), '8': (app.width/2, app.height - 100), '9': (app.width - 100, app.height - 100),
    }
    app.calib_order = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    app.calib_index = 0
    app.recording_data = False
    app.stable_samples = []
    app.calib_raw_results = {}

    app.camera_queue = mp.Queue(maxsize=10)
    app.camera_mode = mp.Value('i', 0)

    app.vision_process = mp.Process(
        target=manager_eyeVsHand.run_unified_camera_process,
        args=(app.camera_queue, app.camera_mode, app.stop_event, app.width, app.height),
        daemon=True
    )
    app.vision_process.start()

    app.queue_thread = threading.Thread(target=_camera_queue_listener, args=(app,), daemon=True)
    app.queue_thread.start()


def onStep(app):
    # app.step_counter += 1
    # if app.step_counter % 3 == 0:
    #     with app.lock:
    #         if app.latest_frame_bytes is not None:
    #             try:
    #                 pil_img = Image.open(io.BytesIO(app.latest_frame_bytes))
    #                 app.camera_cmu_image = CMUImage(pil_img)
    #                 app.latest_frame_bytes = None
    #             except Exception:
    #                 pass

    if app.state == 'intro':
        app.intro.change(app)

    elif app.state == 'calibration':
        with app.lock:
            current_vx = app.raw_vx
            current_vy = app.raw_vy

        if app.recording_data and current_vx is not None and current_vy is not None:
            app.stable_samples.append((current_vx, current_vy))
            if len(app.stable_samples) >= Samplesize_need:
                _finish_current_point_capture(app)

    elif app.state in ('demo', 'game'):
        if app.camera_mode.value == 0:
            with app.lock:
                current_vx = app.raw_vx
                current_vy = app.raw_vy
            if current_vx is not None and current_vy is not None:
                cx, cy = get_gazerecorder_style_pointer(app, current_vx, current_vy)
                if app.gaze_x is None:
                    app.gaze_x, app.gaze_y = cx, cy
                else:
                    app.gaze_x = int(app.gaze_x + 0.25 * (cx - app.gaze_x))
                    app.gaze_y = int(app.gaze_y + 0.25 * (cy - app.gaze_y))
            else:
                app.gaze_x, app.gaze_y = None, None
            
            cursor_x, cursor_y = app.gaze_x, app.gaze_y
            is_pinching = False
        else:
            cursor_x, cursor_y = app.hand_x, app.hand_y
            is_pinching = (app.hand_gesture == 'PINCH')

        for target in app.demo_targets:
            if target.flash_timer > 0:
                target.flash_timer -= 1
            triggered = target.check_hover(cursor_x, cursor_y, is_pinching, app.camera_mode.value)
            if triggered:
                app.demo_score += 100


def onKeyPress(app, key):
    if app.state == 'intro':
        app.intro.jump(app, key)

    elif app.state == 'menu':
        if key == 'space' and app.rightest_bottom_building.near(app.character):
            if app.camera_mode.value == 0:
                app.camera_mode.value = 1  
            else:
                app.camera_mode.value = 0  

    elif app.state == 'calibration':
        if key in ['space', 'enter']:
            if not app.recording_data:
                app.stable_samples = []
                app.recording_data = True

    elif app.state in ('demo', 'game'):
        if key in ['b', 'escape']:
            app.state = 'menu'
        elif key == 'space':
            app.camera_mode.value = 1 - app.camera_mode.value


def onKeyHold(app, keys):
    if app.state == 'menu':
        app.menu_walking_sound.play()
        x, y = app.character.x, app.character.y
        if 'left' in keys: app.character.move(-5, 0)
        if 'right' in keys: app.character.move(5, 0)
        if 'up' in keys: app.character.move(0, -5)
        if 'down' in keys: app.character.move(0, 5)

        if not 0 <= app.character.x <= app.width or not 0 <= app.character.y <= app.height:
            app.character.x, app.character.y = x, y
        else:
            for v in app.triggers_menu:
                if v.collide(app.character):
                    if v == app.fence:
                        if app.camera_mode.value == 0:
                            app.state = 'calibration'
                            app.calib_index = 0
                            app.stable_samples = []
                            app.calib_raw_results = {}
                        else:
                            app.state = 'demo'
                    else: 
                        app.character.x, app.character.y = x, y


def redrawAll(app):
    if app.state == 'intro':
        app.intro.draw(app)

    elif app.state == 'menu':
        imageWidth, imageHeight = getImageSize(app.url)
        drawImage(app.url, app.width/2, app.height/2, align='center', width=imageWidth, height=imageHeight)
        drawCircle(app.character.x, app.character.y, 10, fill='red')

        if app.rightest_bottom_building.near(app.character):
            curr_mode = "EYE" if app.camera_mode.value == 0 else "HAND"
            next_mode = "HAND" if app.camera_mode.value == 0 else "EYE"
            drawRect(app.width // 2 - 220, 30, 440, 40, fill='black', opacity=80, align='center')
            drawLabel(f"Mode: {curr_mode} | Press [ SPACE ] to switch to {next_mode}", app.width // 2, 30, fill='yellow', size=15, bold=True)

    elif app.state == 'calibration':
        drawRect(0, 0, app.width, app.height, fill='aliceBlue')

        if app.calib_index < len(app.calib_order):
            current_target_id = app.calib_order[app.calib_index]
            tx, ty = app.calib_targets[current_target_id]

            drawCircle(tx, ty, 25, fill='crimson')
            drawCircle(tx, ty, 8, fill='white')

            progress = min(len(app.stable_samples), Samplesize_need) / Samplesize_need
            drawRect(app.width // 2 - 120, app.height - 90, 240, 14, fill=None, border='gray')
            
            # 👈 修复点：加入 progress_w > 1 尺寸保护，防止宽度为 0 报错
            progress_w = 240 * progress
            if progress_w > 1:
                bar_color = 'limeGreen' if app.recording_data else 'lightGray'
                drawRect(app.width // 2 - 120, app.height - 90, progress_w, 14, fill=bar_color)

            if not app.recording_data:
                msg = f"Look at Point {app.calib_index + 1} and Press [ SPACE ]"
            else:
                msg = f"Recording Point {app.calib_index + 1}... Hold Gaze!"

            drawLabel(msg, app.width // 2, app.height - 50, size=18, bold=True, align='center')

    elif app.state in ('demo', 'game'):
        drawRect(0, 0, app.width, app.height, fill='black')
        
        for gx in range(0, app.width, 100):
            drawLine(gx, 0, gx, app.height, fill='darkSlateGray', opacity=30)
        for gy in range(0, app.height, 100):
            drawLine(0, gy, app.width, gy, fill='darkSlateGray', opacity=30)

        drawRect(0, 0, app.width, 70, fill='black', opacity=80)
        drawLine(0, 70, app.width, 70, fill='cyan')

        mode_title = "EYE-TRACKING LAB (CALIBRATED)" if app.camera_mode.value == 0 else "HAND-GESTURE LAB"
        drawLabel(f"SYSTEM DEMO // {mode_title}", 40, 25, fill='cyan', size=20, bold=True, align='left')
        
        hint_str = "Look at targets to charge" if app.camera_mode.value == 0 else "Move hand & Pinch to trigger"
        drawLabel(f"Objective: {hint_str} | Press [ SPACE ] Switch Mode | Press [ B ] Back to Menu", 40, 50, fill='gray', size=13, align='left')

        drawLabel(f"SCORE: {app.demo_score}", app.width - 260, 35, fill='yellow', size=24, bold=True, align='left')

        for target in app.demo_targets:
            base_color = 'cyan' if app.camera_mode.value == 0 else 'magenta'
            if target.flash_timer > 0:
                drawCircle(target.x, target.y, target.radius + 15, fill='white', opacity=80)
            
            drawCircle(target.x, target.y, target.radius, fill=None, border=base_color, opacity=50)
            
            # 👈 核心修复点：计算蓄力圆环半径，严格要求 r > 1 才绘制，防止 0.0 半径导致崩溃！
            inner_r = target.radius * target.progress
            if inner_r > 1:
                drawCircle(target.x, target.y, inner_r, fill=base_color, opacity=60)

            drawLabel(target.label, target.x, target.y, fill='white', size=12, bold=True)

        if app.camera_mode.value == 0:
            if app.gaze_x is not None and app.gaze_y is not None:
                drawLine(app.gaze_x - 20, app.gaze_y, app.gaze_x + 20, app.gaze_y, fill='cyan')
                drawLine(app.gaze_x, app.gaze_y - 20, app.gaze_x, app.gaze_y + 20, fill='cyan')
                drawCircle(app.gaze_x, app.gaze_y, 8, fill=None, border='cyan')
                drawLabel(f"Gaze ({app.gaze_x}, {app.gaze_y})", app.gaze_x, app.gaze_y + 28, fill='cyan', size=11)
            else:
                drawLabel("Gaze Signal Lost...", app.width // 2, app.height // 2, fill='red', size=20)

        else:
            if app.hand_x is not None and app.hand_y is not None:
                cursor_color = 'lime' if app.hand_gesture == 'PINCH' else 'magenta'
                drawCircle(app.hand_x, app.hand_y, 16, fill=cursor_color, opacity=70)
                drawCircle(app.hand_x, app.hand_y, 24, fill=None, border=cursor_color)
                drawLabel(f"Gesture: {app.hand_gesture}", app.hand_x, app.hand_y + 35, fill=cursor_color, size=13, bold=True)
            else:
                drawLabel("Hand Tracking Searching...", app.width // 2, app.height // 2, fill='red', size=20)

    if app.camera_cmu_image is not None and app.state != 'intro':
        cam_w, cam_h = 200, 150
        cam_x, cam_y = app.width - cam_w - 20, app.height - cam_h - 20
        drawRect(cam_x - 4, cam_y - 4, cam_w + 8, cam_h + 8, fill='black', opacity=80)
        drawImage(app.camera_cmu_image, cam_x, cam_y, width=cam_w, height=cam_h)
        
        mode_text = "EYE" if app.camera_mode.value == 0 else "HAND"
        drawLabel(f"CAM FEED [{mode_text}]", cam_x + 10, cam_y + 15, fill='lime', size=11, bold=True, align='left')


def onAppStop(app):
    if getattr(app, 'stop_event', None) is not None:
        app.stop_event.set()

    if getattr(app, 'queue_thread', None) is not None:
        app.queue_thread.join(timeout=1)

    if getattr(app, 'vision_process', None) is not None:
        try:
            if app.vision_process.is_alive():
                app.vision_process.terminate()
                app.vision_process.join(timeout=1)
        except Exception:
            pass


if __name__ == '__main__':
    runApp(width=1500, height=1000)