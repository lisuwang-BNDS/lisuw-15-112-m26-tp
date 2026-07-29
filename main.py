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
import os
from PIL import Image
from cmu_graphics import *
import random
import eye_tracker
from vision_tracker import VisionTrackerThread, VisionData
from smart_map import TutorialLevel

Samplesize_need = 20



class RandomParallaxBackground:
    def __init__(self, layer1_path, layer2_pool, layer3_pool, layer4_pool, width, height):
        self.width = width
        self.height = height
        self.layer1_path = layer1_path
        self.speed1 = 0.15
        self.offset1 = 0.0
        self.layer2_pool = layer2_pool 
        self.speed2 = 0.45
        self.offset2 = 0.0
        self.layer2_curr = random.choice(self.layer2_pool)
        self.layer2_next = random.choice(self.layer2_pool)
        self.layer3_pool = layer3_pool  
        self.speed3 = 0.85
        self.offset3 = 0.0
        self.layer3_curr = random.choice(self.layer3_pool)
        self.layer3_next = random.choice(self.layer3_pool)
        self.layer4_pool = layer4_pool
        self.speed4 = 1.0
        self.offset4 =0.0
        self.layer4_curr = random.choice(self.layer4_pool)
        self.layer4_next = random.choice(self.layer4_pool)
        
# #this update function is partially written by gemini flash 

    def update(self):
        self.offset1 = (self.offset1 + 6 * self.speed1) % self.width

        self.offset2 += 6 * self.speed2
        if self.offset2 >= self.width:
            self.offset2 %= self.width  
            self.layer2_curr = self.layer2_next  
            self.layer2_next = random.choice(self.layer2_pool) 

        self.offset3 += 6 * self.speed3
        if self.offset3 >= self.width:
            self.offset3 %= self.width
            self.layer3_curr = self.layer3_next
            self.layer3_next = random.choice(self.layer3_pool)

        self.offset4 += 6 * self.speed4
        if self.offset4 >= self.width:
            self.offset4 %= self.width
            self.layer4_curr = self.layer4_next
            self.layer4_next = random.choice(self.layer4_pool)

    def draw(self, app):
    
        x1_l1 = (self.width / 2) - self.offset1
        x2_l1 = x1_l1 + self.width - 1  
        drawImage(self.layer1_path, x1_l1, self.height / 2, align='center', width=self.width, height=self.height)
        drawImage(self.layer1_path, x2_l1, self.height / 2, align='center', width=self.width, height=self.height)

        x1_l2 = (self.width / 2) - self.offset2
        x2_l2 = x1_l2 + self.width - 1
        drawImage(self.layer2_curr, x1_l2, self.height / 2, align='center', width=self.width, height=self.height)
        drawImage(self.layer2_next, x2_l2, self.height / 2, align='center', width=self.width, height=self.height)

        x1_l3 = (self.width / 2) - self.offset3
        x2_l3 = x1_l3 + self.width - 1
        drawImage(self.layer3_curr, x1_l3, self.height / 2, align='center', width=self.width, height=self.height)
        drawImage(self.layer3_next, x2_l3, self.height / 2, align='center', width=self.width, height=self.height)

        x1_l4 = (self.width / 2) - self.offset4
        x2_l4 = x1_l4 + self.width - 1
        drawImage(self.layer4_curr, x1_l4, self.height / 2, align='center', width=self.width, height=self.height)
        drawImage(self.layer4_next, x2_l4, self.height / 2, align='center', width=self.width, height=self.height)

#this class is bebugged and rewrite partially by gemini thinking model
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
            if hasattr(app, 'intro_sound'):
                app.intro_sound.pause()

    def jump(self, app, key):
        if key in ['space', 'enter']:
            app.state = 'menu'
            if hasattr(app, 'intro_sound'):
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
            color = 'cyan' if self.glitching and random.random() < 0.4 else 'white'
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


class Character: #this is the character for the starting page menu
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

class Player:
    def __init__(self,x,y,width = 40, height = 80):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vy = 0.0
        self.g = 1.5 # gravitational a, since on graphics + means down
        self.jump_power = -22
        self.is_grounded = False
        self.ground_y = 900
        self.jumps_remaining = 2  
        self.max_jumps = 2
        self.dash_cooldown = 0
        self.dash_max_cooldown = 60  # 1.2 sec
        self.dash_speed = 25
        self.dash_duration = 15
        self.dash_timer = 0
        self.is_dashing = False
        self.dash_direction = 1  
        self.state = 'run' #for future animation and so ( run jump fall dash slide...)

    def get_rect(self):
            return (self.x, self.y, self.width, self.height)
        
    def jump(self):
        if self.jumps_remaining > 0:
            self.vy = self.jump_power
            self.jumps_remaining -= 1
            self.is_grounded = False
            self.state = 'jump'
    
    def dash(self, direction):
        print("enter dash function")
        print(self.dash_cooldown)
        if self.dash_cooldown == 0 and not self.is_dashing:
            print('actually fashing')
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_direction = direction
            self.dash_cooldown = self.dash_max_cooldown
            self.state = 'dash'


    def update(self, current_ground = 900):
        if self.is_dashing:
            self.x += self.dash_speed * self.dash_direction
            self.vy = 0
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
        print('update', self.dash_cooldown)
        if self.dash_cooldown > 0:
            print('hi')
            self.dash_cooldown -= 1
        
        self.ground_y = current_ground
        if not self.is_dashing:
            self.vy += self.g
            self.y += self.vy
        feet_y = self.y + self.height
        if feet_y >= self.ground_y:
            self.y = self.ground_y - self.height
            self.vy = 0
            self.is_grounded = True
            self.jumps_remaining = self.max_jumps  
            self.state = 'run'
        else:
            self.is_grounded = False
            if self.vy > 0:
                self.state = 'fall'

    def draw(self,app): #make it to sprites later on
        drawRect(self.x, self.y,self.width,self.height, fill='cyan')
        eye_y = self.y + 15
        drawCircle(self.x + self.width-10, eye_y, 4 , fill = 'red')
        if self.is_grounded:
            drawOval(self.x + self.width / 2, self.ground_y, self.width + 10, 8, fill='darkCyan', opacity=40)




class menu_triggerer:
    def __init__(self, x, y, w, h):
        self.left = x
        self.top = y
        self.w = w
        self.h = h

    def collide(self, other):
        if not isinstance(other, Character):
            return False
        return self.left <= other.x <= (self.left + self.w) and self.top <= other.y <= (self.top + self.h)

    def near(self, other, margin=30):
        if not isinstance(other, Character):
            return False
        return (self.left - margin <= other.x <= self.left + self.w + margin and
                self.top - margin <= other.y <= self.top + self.h + margin)

#This class is debugged with gemini thinking model 
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
                self.progress = 1.0 if is_pinching else min(0.8, self.progress + 0.05)

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
    else:
        app.camera_message = 'Look at next point and press space.'

#this function written by gemini thinking model
def get_image_files(folder_path):
    if not os.path.exists(folder_path):
        return []
    valid_exts = ('.png', '.jpg', '.jpeg')
    files = []
    for f in os.listdir(folder_path):
        if f.startswith('.'):
            continue
        if f.lower().endswith(valid_exts):
            files.append(os.path.join(folder_path, f))
    return sorted(files)

def onAppStart(app):
    app.width = 1500
    app.height = 1000
    app.stepsPerSecond = 50
    app.is_running = True
    app.fenced = False
    app.msg_need_ca = None
    app.player = Player(x=200, y=730, width=40, height=70)

    app.vision = VisionData()
    app.camera_mode = 0  # 0: Eye, 1: Hand

    app.gaze_x, app.gaze_y = None, None

    app.mouse_x, app.mouse_y = app.width // 2, app.height // 2
    app.mouse_pressed = False

    app.state = 'intro'
    try:
        url_intro = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/Future Noir.mp3'
        app.intro_sound = Sound(url_intro)
        app.intro_sound.play(loop=True)
    except Exception:
        pass

    app.intro = IntroLogo()

    try:
        url_menu_walking = '/Users/lisuwang/untitled folder/112Projec/assets/sounds/walking_menu.ogg'
        app.menu_walking_sound = Sound(url_menu_walking)
    except Exception:
        pass

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

    
    app.demo_targets = [
        DemoTarget(350, 300, 50, "15"),
        DemoTarget(1150, 300, 50, "112"),
        DemoTarget(450, 700, 50, "ENVISION"),
        DemoTarget(1050, 700, 50, "15"),
        DemoTarget(750, 500, 60, "112")
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

  
    base_bg_dir = '/Users/lisuwang/untitled folder/112Projec/assets/images/self_categoried_background/'

    
    layer1_files = get_image_files(os.path.join(base_bg_dir, 'layer1_far'))
    layer2_files = get_image_files(os.path.join(base_bg_dir, 'layer2_mid'))
    layer3_files = get_image_files(os.path.join(base_bg_dir, 'layer3_near'))
    layer4_files = get_image_files(os.path.join(base_bg_dir, 'layer4_nearest'))

    l1_path = layer1_files[0] 
    l2_pool = layer2_files 
    l3_pool = layer3_files 
    l4_pool = layer4_files

    app.bg = RandomParallaxBackground(l1_path, l2_pool, l3_pool,l4_pool, app.width, app.height)
    app.game_speed = 5

    app.tutorial = TutorialLevel()
    app.insideGame = 'tutorial' # future add different difficulty and non tutorial 

    app.vision_thread = VisionTrackerThread(app)
    app.vision_thread.start()


def onStep(app):
    if app.state == 'intro':
        app.intro.change(app)

    elif app.state == 'calibration':
        if app.recording_data and app.vision.raw_vx is not None and app.vision.raw_vy is not None:
            app.stable_samples.append((app.vision.raw_vx, app.vision.raw_vy))
            if len(app.stable_samples) >= Samplesize_need:
                _finish_current_point_capture(app)

    elif app.state in ('demo', 'game') : 
        if app.state == 'game':
            app.bg.update()
            app.player.update()
            if app.insideGame == 'tutorial':
                app.tutorial.update(app.game_speed,app)
            
                app.tutorial.check_collisions(app.player, app)
            else:
                pass #normal game
            if app.camera_mode == 1 and app.vision.hand_gesture == 'PINCH':
                app.player.jump()

        
        if app.camera_mode == 0:
            if app.vision.raw_vx is not None and app.vision.raw_vy is not None:
                cx, cy = get_gazerecorder_style_pointer(app, app.vision.raw_vx, app.vision.raw_vy)
                if app.gaze_x is None:
                    app.gaze_x, app.gaze_y = cx, cy
                else:
                    app.gaze_x = int(app.gaze_x + 0.25 * (cx - app.gaze_x))
                    app.gaze_y = int(app.gaze_y + 0.25 * (cy - app.gaze_y))
            else:
                app.gaze_x, app.gaze_y = app.mouse_x, app.mouse_y

            #cursor_x, cursor_y = app.gaze_x, app.gaze_y
            #is_pinching = app.mouse_pressed

        
        # else:
        #     if app.vision.hand_x is not None and app.vision.hand_y is not None:
        #         #cursor_x, cursor_y = app.vision.hand_x, app.vision.hand_y
        #         #is_pinching = (app.vision.hand_gesture == 'PINCH')
        #     else:
        #         cursor_x, cursor_y = app.mouse_x, app.mouse_y
        #         is_pinching = app.mouse_pressed

        for target in app.demo_targets:
            if target.flash_timer > 0:
                target.flash_timer -= 1
            

def onMouseMove(app, mouseX, mouseY):
    app.mouse_x, app.mouse_y = mouseX, mouseY


def onMousePress(app, mouseX, mouseY):
    app.mouse_pressed = True


def onMouseRelease(app, mouseX, mouseY):
    app.mouse_pressed = False


def onKeyPress(app, key):
    if app.state == 'intro':
        app.intro.jump(app, key)

    elif app.state == 'menu':
        if key == 'space' and app.rightest_bottom_building.near(app.character):
            app.camera_mode = 1 - app.camera_mode

    elif app.state == 'calibration':
        if key in ['space', 'enter']:
            if not app.recording_data:
                app.stable_samples = []
                app.recording_data = True

    elif app.state in ('demo', 'game'):
        if key in ['b', 'escape']:
            app.state = 'menu'
        elif key == 'space':
            
            if app.state == 'game':
                app.player.jump()
        elif key == 's': ############
            app.camera_mode = 1 - app.camera_mode
        elif key == 'd' and app.state == 'game':
            app.player.dash(1)
        elif key == 'a' and app.state == 'game':
            app.player.dash(-1)
        


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
                        app.fenced = True
                        if app.camera_mode == 0 and app.vision.camera_available:
                            app.state = 'calibration'
                            app.calib_index = 0
                            app.stable_samples = []
                            app.calib_raw_results = {}
                        else:
                            app.state = 'demo'
                    if v == app.middle_upper_building:
                        if not app.fenced:
                            app.msg_need_ca = 'please go to the fence to finish the lab'
                        else:
                            app.state = 'game'


                    else:

                        app.character.x, app.character.y = x, y


def redrawAll(app):
    if app.state == 'intro':
        app.intro.draw(app)

    elif app.state == 'menu':
        imageWidth, imageHeight = getImageSize(app.url)
        drawImage(app.url, app.width/2, app.height/2, align='center', width=imageWidth, height=imageHeight)
        drawCircle(app.character.x, app.character.y, 10, fill='red')
        if app.msg_need_ca != None:
            drawLabel(app.msg_need_ca, app.width//2, 30, fill= 'yellow', bold = True)
        
        #this branch written with gemini flash
        if app.rightest_bottom_building.near(app.character):
            curr_mode = "EYE" if app.camera_mode == 0 else "HAND"
            next_mode = "HAND" if app.camera_mode == 0 else "EYE"
            drawRect(app.width // 2 - 220, 30, 440, 40, fill='black', opacity=80, align='center')
            drawLabel(f"Mode: {curr_mode} | Press [ SPACE ] to switch to {next_mode}", app.width // 2, 30, fill='yellow', size=15, bold=True)
    #this elif branch is debugged and rewritten with gemini flash
    elif app.state == 'calibration':
        drawRect(0, 0, app.width, app.height, fill='aliceBlue')
        
        if app.calib_index < len(app.calib_order):
            current_target_id = app.calib_order[app.calib_index]
            tx, ty = app.calib_targets[current_target_id]

            drawCircle(tx, ty, 25, fill='crimson')
            drawCircle(tx, ty, 8, fill='white')

            progress = min(len(app.stable_samples), Samplesize_need) / Samplesize_need
            drawRect(app.width // 2 - 120, app.height - 90, 240, 14, fill=None, border='gray')

            progress_w = 240 * progress
            if progress_w > 1:
                bar_color = 'limeGreen' if app.recording_data else 'lightGray'
                drawRect(app.width // 2 - 120, app.height - 90, progress_w, 14, fill=bar_color)

            if not app.recording_data:
                msg = f"Look at Point {app.calib_index + 1} and Press [ SPACE ]"
            else:
                msg = f"Recording Point {app.calib_index + 1}... Hold Gaze!"

            drawLabel(msg, app.width // 2, app.height - 50, size=18, bold=True, align='center')

    elif app.state == 'demo':
        drawRect(0, 0, app.width, app.height, fill='black')

        for gx in range(0, app.width, 100):
            drawLine(gx, 0, gx, app.height, fill='darkSlateGray', opacity=30)
        for gy in range(0, app.height, 100):
            drawLine(0, gy, app.width, gy, fill='darkSlateGray', opacity=30)

        drawRect(0, 0, app.width, 70, fill='black', opacity=80)
        drawLine(0, 70, app.width, 70, fill='cyan')

        mode_title = "EYE-TRACKING LAB" if app.camera_mode == 0 else "HAND-GESTURE LAB"
        drawLabel(f"DEMO // {mode_title}", 40, 25, fill='cyan', size=20, bold=True, align='left')

        hint_str = "Look at targets (or Mouse) to charge" if app.camera_mode == 0 else "Move hand (or Mouse) & Pinch/Click to trigger"
        drawLabel(f"Objective: {hint_str} | Press [ SPACE ] Switch Mode | Press [ B ] Back to Menu", 40, 50, fill='gray', size=13, align='left')

    
        

        if app.camera_mode == 0:
            if app.gaze_x is not None and app.gaze_y is not None:
                drawLine(app.gaze_x - 20, app.gaze_y, app.gaze_x + 20, app.gaze_y, fill='cyan')
                drawLine(app.gaze_x, app.gaze_y - 20, app.gaze_x, app.gaze_y + 20, fill='cyan')
                drawCircle(app.gaze_x, app.gaze_y, 8, fill=None, border='cyan')
                drawLabel(f"Gaze/Cursor ({app.gaze_x}, {app.gaze_y})", app.gaze_x, app.gaze_y + 28, fill='cyan', size=11)
        else:
            for target in app.demo_targets:
                        base_color = 'cyan' if app.camera_mode == 0 else 'magenta'
                        if target.flash_timer > 0:
                            drawCircle(target.x, target.y, target.radius + 15, fill='white', opacity=80)
            
                        drawCircle(target.x, target.y, target.radius, fill=None, border=base_color, opacity=50)
            
                        inner_r = target.radius * target.progress
                        if inner_r > 1:
                            drawCircle(target.x, target.y, inner_r, fill=base_color, opacity=60)
            
                        drawLabel(target.label, target.x, target.y, fill='white', size=12, bold=True)
            hx = app.vision.hand_x if app.vision.hand_x is not None else app.mouse_x
            hy = app.vision.hand_y if app.vision.hand_y is not None else app.mouse_y
            cursor_color = 'lime' if (app.vision.hand_gesture == 'PINCH' or app.mouse_pressed) else 'magenta'
            drawCircle(hx, hy, 16, fill=cursor_color, opacity=70)
            drawCircle(hx, hy, 24, fill=None, border=cursor_color)
            drawLabel(f"Gesture: {app.vision.hand_gesture}", hx, hy + 35, fill=cursor_color, size=13, bold=True)
    elif app.state == 'game':
        app.bg.draw(app)
        drawLine(0, 800, app.width, 800, fill='cyan', lineWidth=3)

        app.player.draw(app)

        if app.insideGame == 'tutorial': ##remember if not
            app.tutorial.draw(app)
        



def onAppStop(app):
    app.is_running = False
    if hasattr(app, 'vision_thread'):
        app.vision_thread.stop()


if __name__ == '__main__':
    runApp(width=1500, height=1000)