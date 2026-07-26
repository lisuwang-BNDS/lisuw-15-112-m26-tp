#other complexity in the leve itself (feature, plaftform / physics)
#backgtound
#handtracking mediapipe()

import multiprocessing as mp
import queue
import threading
from cmu_graphics import *
import eye_tracker

Samplesize_need = 20
import random


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
        if self.opacity < 100: #TypeError: Label.opacity should be number-in-range-0-100 (but 100.80000000000015 is of type float)
            self.opacity = min(100,(self.opacity + 0.7))
        if self.opacity > 60 and self.opacity_for_text < 100:
            self.opacity_for_text = min(100,(self.opacity_for_text + 1.3))
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
            drawLine(cx - w/2, cy + 55, cx + w/2, cy + 55, fill='cyan', opacity=self.opacity_for_text)
            drawLabel("ASSISTIVE EYE-TRACKING ADVENTURE FOR 112 PROJECT", cx, cy + 85, fill='magenta', size=13, bold=True, font='monospace', opacity=self.opacity_for_text)

        if self.time > 40:
       
            pulse_opacity = 30 + int(40 * ((self.time % 30) / 30.0))
            drawLabel("[ PRESS SPACE TO START ]", cx, app.height - 70, fill='gray', size=12, font='monospace', opacity=pulse_opacity)


    
class Character:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def move(self,dx,dy):
        self.x += dx
        self.y += dy

    

class menu_triggerer:
    def __init__(self,x,y,w,h):
        self.left = x
        self.top = y
        self.w = w
        self.h = h

    def collide(self,other):
        if not isinstance(other,Character):
            return False
        if self.left <= other.x <= (self.left + self.w) and self.top <= other.y <= (self.top + self.h):
            return True
        return False
    







def get_gazerecorder_style_pointer(app, current_vx, current_vy):
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

    if GrandWeight == 0: return app.width // 2, app.height // 2

    return int(screenX / GrandWeight), int(screenY / GrandWeight)


def _finish_current_point_capture(app):
    if len(app.stable_samples) < Samplesize_need:
        return

    avg_vx = sum(p[0] for p in app.stable_samples) / len(app.stable_samples)
    avg_vy = sum(p[1] for p in app.stable_samples) / len(app.stable_samples)
    print(avg_vx, avg_vy)

    current_target_id = app.calib_order[app.calib_index]
    app.calib_raw_results[current_target_id] = (avg_vx, avg_vy)

    app.stable_samples = []
    app.recording_data = False
    app.calib_index += 1

    if app.calib_index >= len(app.calib_order):
        app.state = 'game'
        app.camera_message = 'Complete!'
    else:
        app.camera_message = 'Look at next point and press space.'


def _camera_queue_listener(app):
    while not getattr(app, 'stop_event', None).is_set():
        try:
            payload = app.camera_queue.get(timeout=0.1)
        except queue.Empty:
            continue

        with app.lock:
            if not payload:
                continue

            kind = payload[0]
            if kind == 'point':
                _, vx, vy = payload
                if vx is None or vy is None:
                    app.raw_vx = None
                    app.raw_vy = None
                    app.camera_status = 'lost'
                else:
                    app.raw_vx = vx
                    app.raw_vy = vy
                    app.camera_status = 'tracking'
            elif kind == 'error':
                _, message = payload
                app.raw_vx = None
                app.raw_vy = None
                app.camera_status = 'error'


def onAppStart(app):
    app.width = 1500
    app.height = 1000
    app.stepsPerSecond = 50
    app.stop_event = threading.Event()
    app.lock = threading.Lock()
    app.raw_vx = None
    app.raw_vy = None
    app.gaze_x = None
    app.gaze_y = None

    # app.testWalls_forMenu = []
    # app.waitForCheck = 0
    # app.startcheckx = 0
    # app.startchecky = 0


    app.camera_status = 'starting'
    app.camera_message = 'camera'

    app.state = 'calibration' #calibration,menu
    url_intro = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/Future Noir.mp3'
    app.intro_sound = Sound(url_intro)
    print(app.intro_sound)
    app.intro_sound.play(loop = True)
    app.intro = IntroLogo()


    url_menu_walking = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/walking_menu.ogg'
    app.menu_walking_sound = Sound(url_menu_walking)

#since each objects may have its own function, if use inheritance will be 15 classes, or use one parent class?
    app.leftest_top_building = menu_triggerer(8,8,236,418)
    app.hangin_neonlight = menu_triggerer(254,50,42,185)
    app.groundwater = menu_triggerer(50,503,60,36)
    app.leftest_bottom_building = menu_triggerer(14,624,475,319)
    app.fence = menu_triggerer(505,752,369,182)
    app.rightest_bottom_building= menu_triggerer(882,683,436,281)
    app.middle_upper_building= menu_triggerer(565,6,250,419)
    app.rightest_upper_building= menu_triggerer(882,4,314,424)
    app.corridor_between_upper= menu_triggerer(825,21,49,349)
    app.right_light= menu_triggerer(1216,238,62,178)
    app.left_light= menu_triggerer(495,6,54,160)
    app.trash_can = menu_triggerer(523,308,37,52)
    app.road = menu_triggerer(814,507,69,160)
    app.alarm_sign = menu_triggerer(1328,174,157,128)
    app.monitor_camera = menu_triggerer(1330,688,38,56)
    app.triggers_menu = [app.leftest_top_building,app.hangin_neonlight,app.groundwater,app.leftest_bottom_building,app.fence,app.rightest_bottom_building,
                         app.middle_upper_building,app.rightest_upper_building,app.corridor_between_upper,app.right_light,app.left_light,
                         app.trash_can,app.alarm_sign,app.monitor_camera] #NO ROAD HERE< <<<<<<< !


    app.character = Character(830,600)



    app.url = '/Users/lisuwang/untitled folder/112Projec/assets/images/Menu page/Menu page 1.png'
    app.recording_data = False

    app.calib_targets = {
        '1': (100, 100), '2': (app.width/2, 100), '3': (app.width - 100, 100),
        '4': (100, app.height/2), '5': (app.width/2, app.height/2), '6': (app.width - 100, app.height/2),
        '7': (100, app.height - 100), '8': (app.width/2, app.height - 100), '9': (app.width - 100, app.height - 100),
    }
    app.calib_order = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    app.calib_index = 0
    app.stable_samples = []
    app.calib_raw_results = {}
    #mp
    app.camera_queue = mp.Queue(maxsize=20)
    app.camera_stop_event = mp.Event()
    app.camera_process = mp.Process(
        target=eye_tracker.run_camera_process,
        args=(app.camera_queue, app.camera_stop_event, app.width, app.height),
        daemon=True,
    )
    app.camera_process.start()

    app.queue_thread = threading.Thread(target=_camera_queue_listener, args=(app,), daemon=True)
    app.queue_thread.start()


def onStep(app):
    with app.lock:
        current_vx = app.raw_vx
        current_vy = app.raw_vy

    if app.state == 'intro':
        app.intro.change(app)

    elif app.state == 'calibration':
        if app.recording_data and current_vx is not None and current_vy is not None:
            app.stable_samples.append((current_vx, current_vy))

            if len(app.stable_samples) >= Samplesize_need:
                _finish_current_point_capture(app)

    elif app.state == 'game':
        if current_vx is not None and current_vy is not None:
            cx, cy = get_gazerecorder_style_pointer(app, current_vx, current_vy)
            if app.gaze_x is None:
                app.gaze_x, app.gaze_y = cx, cy
            else:
                ALPHA = 0.20
                app.gaze_x = int(app.gaze_x + ALPHA * (cx - app.gaze_x))
                app.gaze_y = int(app.gaze_y + ALPHA * (cy - app.gaze_y))
        else:
            app.gaze_x, app.gaze_y = None, None


def onKeyPress(app, key):
    if app.state == 'intro':
        app.intro.jump(app, key)


    if app.state != 'calibration':
        return

    if key in ['space', 'enter']:
        if not app.recording_data:
            app.stable_samples = []
            app.recording_data = True
            print("Recording")

def onKeyHold(app,keys):
    print(app.state)
    if app.state == 'menu':
        app.menu_walking_sound.play()
        x = app.character.x 
        y = app.character.y
        if 'left' in keys: 
            app.character.move(-5,0)
        if 'right' in keys: 
            app.character.move(5,0)
        if 'up' in keys: 
            app.character.move(0,-5)
        if 'down' in keys: 
            app.character.move(0,5)
    if not 0 <= app.character.x <= app.width or not 0 <= app.character.y <= app.height:
        app.character.x, app.character.y = x,y
    else:
        for v in app.triggers_menu:
            if v.collide(app.character):
                if v == app.fence:
                    app.state = 'start'

                else: 
                    app.character.x, app.character.y = x,y
        

        

    

def onMousePress(app, mouseX, mouseY):
    pass
    # if app.waitForCheck == 0:

    #     app.startcheckx = mouseX
    #     app.startchecky = mouseY
    #     app.waitForCheck = 1
    #     print(f"marking, left top: ({mouseX}, {mouseY})")
    # elif app.waitForCheck == 1:
    #     w = mouseX - app.startcheckx
    #     h = mouseY - app.startchecky
        
    #     wall = (app.startcheckx, app.startchecky, w, h)
    #     app.testWalls_forMenu.append(wall)
    #     print(f"This wall is tested!!!!    :    {wall}")

    #     app.waitForCheck = 0


def redrawAll(app):
    if app.state == 'intro':
        app.intro.draw(app)

    elif app.state == 'menu':
        imageWidth, imageHeight = getImageSize(app.url)
        imageWidth, imageHeight = getImageSize(app.url)
        drawImage(app.url, app.width/2, app.height/2, align='center',width=imageWidth,height=imageHeight)

        # for x, y, w, h in app.testWalls_forMenu:
        #     drawRect(x, y, w, h, fill='red', opacity=50, border='white')

        #drawImage(app.url, 325, 200, align='center',width=imageWidth//2, height=imageHeight//2)
        drawCircle(app.character.x, app.character.y, 10, fill = 'red')


    elif app.state == 'calibration':
        drawRect(0, 0, app.width, app.height, fill='aliceBlue')

        if app.calib_index < len(app.calib_order):
            current_target_id = app.calib_order[app.calib_index]
            tx, ty = app.calib_targets[current_target_id]

            drawCircle(tx, ty, 20, fill='crimson')
            drawCircle(tx, ty, 6, fill='white')

            progress = min(len(app.stable_samples), Samplesize_need) / Samplesize_need
            drawRect(app.width // 2 - 100, app.height - 80, 200, 12, fill=None, border='gray')
            if progress > 0:
                bar_color = 'limeGreen' if app.recording_data else 'lightGray'
                drawRect(app.width // 2 - 100, app.height - 80, 200 * progress, 12, fill=bar_color)

            if not app.recording_data:
                msg = "press space to record"
            else:
                msg = f"recodin Point {app.calib_index + 1}"

            drawLabel(msg, app.width // 2, app.height - 50, size=16, align='center')

    elif app.state == 'game':
        drawRect(0, 0, app.width, app.height, fill='ghostWhite')

        if app.gaze_x is not None and app.gaze_y is not None:
            drawCircle(app.gaze_x, app.gaze_y, 14, fill=None, border='cyan', borderWidth=3)
            drawCircle(app.gaze_x, app.gaze_y, 4, fill='cyan')


def onAppStop(app):
    if getattr(app, 'stop_event', None) is not None:
        app.stop_event.set()
    if getattr(app, 'camera_stop_event', None) is not None:
        app.camera_stop_event.set()

    if getattr(app, 'queue_thread', None) is not None:
        app.queue_thread.join(timeout=1)

    if getattr(app, 'camera_process', None) is not None:
        try:
            if app.camera_process.is_alive():
                app.camera_process.terminate()
                app.camera_process.join(timeout=1)
        except Exception:
            pass


if __name__ == '__main__':
    runApp(width=1500, height=1000)