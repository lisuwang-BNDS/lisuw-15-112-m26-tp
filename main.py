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

#get a plot in the begining of the game


#---------------------------------
#tp2 and tonight

#adjustment on eye and hand 

#smartmap
#---
#finish smart map
#improving (tracler, gyuide, ui, sprites), UI UX
#OH 4:30 - 7 :00
#google slides _image or label, guides . one guide be slide
#


import io
import time
import os
import math
from PIL import Image
from cmu_graphics import *
import random
import eye_tracker
from vision_tracker import VisionTrackerThread, VisionData
from smart_map import TutorialLevel,RecursiveSmartMapGenerator, Bullet, Enemy, FlyingEnemy
from sprite_system import SpriteSheet, AnimatedSprite
from tutorial_story import TutorialStory
Samplesize_need = 20
class TutorialGuide:
    def __init__(self):
        self.current_step = 0
        self.completed = False
        self.show_highlights = True
        self.story_steps = self._create_story()
        
    def _create_story(self):
        #this tutorial text is written by ai and will be replaced later on
        return [
            {
                'id': 'intro',
                'title': 'WELCOME TO ENVISION',
                'text': 'Welcome, Envisioner. You must calibrate your ocular interface\nbefore entering the simulation. Go to the calibration house.',
                'color': 'cyan',
                'instruction': 'Navigate to the highlighted house'
            },
            {
                'id': 'calibration_complete',
                'title': 'CALIBRATION COMPLETE',
                'text': 'Ocular interface synchronized. Practice in the lab,\nthen return to town and enter the training facility.',
                'color': 'lime',
                'instruction': 'Press [B] to return to town when done practicing'
            },
            {
                'id': 'tutorial_complete',
                'title': 'TRAINING COMPLETE',
                'text': 'You have mastered the basics. Return to town\nand enter the main simulation when ready.',
                'color': 'gold',
                'instruction': 'Press [B] to return to town'
            },
            {
                'id': 'real_game',
                'title': 'MAIN SIMULATION',
                'text': 'The real challenge awaits. Enter the simulation\nto begin your journey.',
                'color': 'magenta',
                'instruction': 'Navigate to the highlighted entrance'
            }
        ]
    
    def get_current_step(self):
        if self.current_step < len(self.story_steps):
            return self.story_steps[self.current_step]
        return None
    
    def next_step(self):
        self.current_step += 1
        if self.current_step >= len(self.story_steps):
            self.completed = True
    
    def reset(self):
        self.current_step = 0
        self.completed = False
        self.show_highlights = True


def restart_game(app):
    app.player = Player(x=200, y=450, width=40, height=70)  # Start from high above
    app.bullets = []
    app.projectiles = []
    app.tutorial = TutorialLevel()
    app.smart_map = RecursiveSmartMapGenerator(app.player)
    app.distance = 0
    app.enemies_killed = 0
    app.game_start_time = time.time()
    app.survival_time = 0
    app.state = 'game'
    # Respawn player on the starting platform (drop from above)
    app.smart_map.respawnOnPlatform(app.player)

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
        if self.sprite:
            self.sprite.x = self.x

class Player:
    def __init__(self,x,y,width = 40, height = 80):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vy = 0.0
        self.g = 1.5 # gravitational a, since on graphics + means down
        self.jump_power = -22
        
        self.animation_state = 'run'  # , run, jump, death, aim, dash
        self.sprite_sheet = None
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5
        self.facing_direction = 1  # 1 = right, -1 = left
        
        self.jump_sprite = SpriteSheet("/Users/lisuwang/untitled folder/112Projec/assets/images/wake.png",5,1 )
        self.death_sprite = SpriteSheet ("/Users/lisuwang/untitled folder/112Projec/assets/images/death.png", 6, 1)
        self.aim_sprite = SpriteSheet("/Users/lisuwang/untitled folder/112Projec/assets/images/charge.png", 4,1)
        self.dash_sprite = SpriteSheet("/Users/lisuwang/untitled folder/112Projec/assets/images/GAS dash with FX.png",7,1)
        
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
        
        
        self.weapon_level = 1
        self.max_weapon_level = 3
        self.projectile_speed = 15
        self.projectile_size = 5
        self.fire_rate = 0

        
        self.hp = 10
        self.max_hp = 10
    
    def set_animation_state(self, state):
        self.animation_state = state
        self.current_frame = 0
        self.animation_timer = 0
    
    
    def update_animation(self):
            
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            current_sprite = self.get_current_sprite()
            if current_sprite:
                self.current_frame = (self.current_frame + 1) % current_sprite.cols
    
    def get_current_sprite(self):
        
        if self.animation_state == 'run':
            return self.run_sprite
        elif self.animation_state == 'jump':
            return self.jump_sprite
        elif self.animation_state == 'death':
            return self.death_sprite
        elif self.animation_state == 'aim':
            return self.aim_sprite
        elif self.animation_state == 'dash':
            return self.dash_sprite
        return None
    
    def draw_sprite(self, app):
        
        current_sprite = self.get_current_sprite()
        if current_sprite:
            frame = current_sprite.getFrame(0, self.current_frame)
            drawImage(frame, self.x + self.width/2, self.y + self.height/2, align='center', width=self.width, height=self.height)
    
    def trigger_death(self):
        """Trigger death animation"""
        self.set_animation_state('death')
    
   

    def get_rect(self):
            return (self.x, self.y, self.width, self.height)
        
    def jump(self):
        if self.jumps_remaining > 0:
            self.vy = self.jump_power
            self.jumps_remaining -= 1
            self.is_grounded = False
            self.state = 'jump'
    
    def dash(self, direction, screen_width = 1500):
        print("enter dash function")
        print(self.dash_cooldown)
        if self.dash_cooldown == 0 and not self.is_dashing:
            dash_distance = self.dash_speed * self.dash_duration
            if direction == 1 and self.x + dash_distance > screen_width - self.width:
                
                return
            if direction == -1 and self.x - dash_distance < 0:
                return
            
            print('actually fashing')
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            self.dash_direction = direction
            self.dash_cooldown = self.dash_max_cooldown
            self.state = 'dash'

   


    def update(self, current_ground = 900, screen_width = 1500, screen_height = 1000):
        if self.is_dashing:
            self.set_animation_state('dash')
        elif not self.is_grounded:
            if self.vy <= 0:
                self.set_animation_state('jump')
        else:
            
            self.set_animation_state('run')
            
        if self.is_dashing:
            self.x += self.dash_speed * self.dash_direction
            self.vy = 0
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.set_animation_state('run')
            else:
                self.set_animation_state('dash')
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
            self.set_animation_state('run')
        else:
            self.is_grounded = False
            if self.vy > 0:
                self.state = 'fall'
                self.set_animation_state('jump')
            else:
                self.set_animation_state('jump')
        
        if self.x < 0:
            self.x = 0
            self.is_dashing = False  
        
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
            self.is_dashing = False 
        
        if self.y < 0:
            self.y = 0
            self.vy = 0
        
        if self.y + self.height > screen_height:
            self.y = screen_height - self.height
            self.vy = 0

    def draw(self,app): 
        # Draw sprite if available
        current_sprite = self.get_current_sprite()
        if current_sprite:
            frame = current_sprite.getFrame(self.current_frame, 0)
            # Use original frame dimensions with scale factor
            orig_width, orig_height = current_sprite.getOriginalFrameSize()
            scale_factor = 2.5  # Scale up sprite for better visibility
            drawImage(frame, self.x + self.width/2, self.y + self.height/2, align='center',
                     width=orig_width * scale_factor, height=orig_height * scale_factor)
        else:
            # Fallback to cyan rect
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
        app.tutorial_guide.next_step()
        app.fenced = True
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
    app.distance = 0
    app.enemies_killed = 0
    app.game_start_time = time.time()
    app.survival_time = 0
    app.bullets = []
    app.width = 1500
    app.height = 1000
    app.stepsPerSecond = 50
    app.is_running = True
    app.fenced = False
    app.msg_need_ca = None
    app.player = Player(x=200, y=450, width=40, height=70)  # Start from high above

    app.vision = VisionData()
    app.camera_mode = 0  # 0: Eye, 1: Hand, 2: Keyboard

    app.gaze_x, app.gaze_y = None, None

    app.mouse_x, app.mouse_y = app.width // 2, app.height // 2
    app.mouse_pressed = False

    app.state = 'intro'
    app.tutorial_guide = TutorialGuide()
    app.tutorial_completed = False
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
    
    try:
        sprite_sheet_path = '/Users/lisuwang/untitled folder/112Projec/assets/images/cat-sprite-32x32.png'
        app.character_sprite_sheet = SpriteSheet(sprite_sheet_path, rows=1, cols=4)
        app.character.sprite = AnimatedSprite(app.character_sprite_sheet, app.character.x, app.character.y, 70, 70)
    except Exception as e:
        print(f"Failed to load sprite sheet: {e}")

    
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
    app.game_speed = 10

    app.tutorial = TutorialLevel()
    app.insideGame = 'smart' # future add different difficulty and non tutorial
    app.smart_map = RecursiveSmartMapGenerator(app.player)
    app.modeSwitch = (app.width - 220, 200, 200, 50)
    app.Switchcooldown = 0
    app.MaxCoolSwitch= 30  
    app.projectiles = [] 
    
    
    app.jump_zone = (100, app.height - 150, 120, 100)  
    app.eye_jump_progress = 0.0
    app.eye_dash_progress = 0.0
    app.hand_jump_cooldown = 0
    app.hand_dash_cooldown = 0
    
    app.eye_history = []  
    app.eye_history_max = 30  
    app.special_skill_ready = False
    app.eye_skill_cooldown = 0
    
    app.aim_trajectory = None

    app.vision_thread = VisionTrackerThread(app)
    app.vision_thread.start()


def onStep(app):
    if app.state == 'intro':
        app.intro.change(app)
    
    elif app.state == 'menu':
        if app.character.sprite:
            app.character.sprite.updateAnimation()

    elif app.state == 'calibration':
        if app.recording_data and app.vision.raw_vx is not None and app.vision.raw_vy is not None:
            app.stable_samples.append((app.vision.raw_vx, app.vision.raw_vy))
            if len(app.stable_samples) >= Samplesize_need:
                _finish_current_point_capture(app)

    elif app.state in ('demo', 'game') : 
        
        if app.state == 'game':
            app.distance += app.game_speed * 0.1
            app.survival_time = time.time() - app.game_start_time
            app.bg.update()
            app.player.update()
            app.player.update_animation()
            if app.insideGame == 'tutorial':
                app.tutorial.update(app.game_speed,app)
            
                app.tutorial.check_collisions(app.player, app)
                if app.insideGame == 'tutorial' and app.tutorial.current >= len(app.tutorial.sections):
                    app.tutorial_completed = True
                    app.tutorial_guide.next_step()
                    app.state = 'menu'
                    app.character.x, app.character.y = 830, 600
                    app.player.hp = app.player.max_hp
            elif app.insideGame == 'smart':
                app.smart_map.update(app.game_speed, app)
                app.smart_map.checkCollision(app.player, app)
            if app.player.hp <= 0 and app.state == 'game':
                app.player.trigger_death()
                app.state = 'gameover'
                return
            if app.Switchcooldown == 0:
                x, y, w, h = app.modeSwitch
                if app.camera_mode == 0:
                    if app.gaze_x != None and app.gaze_y != None:
                        if x <= app.gaze_x <= x + w and y <= app.gaze_y <= y + h:
                            app.camera_mode = 1 
                            app.Switchcooldown = app.MaxCoolSwitch
                elif app.camera_mode == 1:
                    if app.vision.hand_gesture == 'PINCH' and app.vision.hand_x != None:
                        if x <= app.vision.hand_x <= x + w and y <= app.vision.hand_y <= y + h:
                            app.camera_mode = 2  
                            app.Switchcooldown = app.MaxCoolSwitch
                else:  
                    pass  # Keyboard mode 
            else:
                app.Switchcooldown -= 1
            
            if app.camera_mode == 0:
                if app.gaze_x != None and app.gaze_y != None:
                   #this relative position algorithm is inspired and designed by gemini flash
                    app.eye_history.append((app.gaze_x, app.gaze_y))
                    if len(app.eye_history) > app.eye_history_max:
                        app.eye_history.pop(0)
                    if len(app.eye_history) >= 10 and app.eye_skill_cooldown == 0:
                        recent_x = [p[0] for p in app.eye_history[-10:]]
                        x_range = max(recent_x) - min(recent_x)
                        if x_range > 125:
                            app.special_skill_ready = True
                            app.eye_skill_cooldown = 60 
                    
                    if app.special_skill_ready and app.eye_skill_cooldown == 0:
                        Screenx = app.width / 2
                        Screeny = app.height / 2
                        if abs(app.gaze_x - Screenx) < 150 and abs(app.gaze_y - Screeny) < 150:
                            if app.insideGame == 'smart':
                                if hasattr(app, 'smart_map'):
                                    app.smart_map.respawnOnPlatform(app.player)
                                app.special_skill_ready = False
                                app.eye_skill_cooldown = 120
                            
                    
                    if app.eye_skill_cooldown > 0:
                        app.eye_skill_cooldown -= 1
            elif app.camera_mode == 1:
                if app.hand_jump_cooldown > 0:
                    app.hand_jump_cooldown -= 1
                if app.hand_dash_cooldown > 0:
                    app.hand_dash_cooldown -= 1
                if app.vision.hand_gesture == 'PINCH' and app.hand_jump_cooldown == 0:
                    if app.player.jumps_remaining > 0:
                        app.player.jump()
                        app.hand_jump_cooldown = 20  
                if app.vision.hand_gesture == 'FIST' and app.hand_dash_cooldown == 0:
                    if app.player.dash_cooldown == 0:
                        direction = 1 if app.vision.hand_x > app.width / 2 else -1
                        app.player.dash(direction)
                        app.hand_dash_cooldown = 25
                if app.vision.hand_gesture == 'PISTOL_AIM' and app.vision.hand_x != None and app.vision.hand_y != None:
                    app.player.set_animation_state('aim')
                    start_x = app.player.x + app.player.width / 2
                    start_y = app.player.y + app.player.height / 2
                    vx = (app.vision.hand_x - app.player.x) / 20
                    vy = (app.vision.hand_y - app.player.y) / 20
                    dist = (vx**2 + vy**2) ** 0.5
                    if dist > 0:
                        vx = (vx / dist) * app.player.projectile_speed
                        vy = (vy / dist) * app.player.projectile_speed
                    app.aim_trajectory = {'start': (start_x, start_y), 'velocity': (vx, vy)}
                else:
                    app.aim_trajectory = None
                
                if app.vision.hand_gesture == 'PISTOL_FIRE':
                    if app.vision.hand_x != None and app.vision.hand_y != None:
                        projectile = {'x': app.player.x + app.player.width / 2, 'y': app.player.y + app.player.height / 2, 'vx': (app.vision.hand_x - app.player.x) / 20, 
                            'vy': (app.vision.hand_y - app.player.y) / 20,
                            'speed': app.player.projectile_speed,
                            'radius': app.player.projectile_size
                        }
                        dist = (projectile['vx']**2 + projectile['vy']**2) ** 0.5
                        if dist > 0:
                            projectile['vx'] = (projectile['vx'] / dist) * projectile['speed']
                            projectile['vy'] = (projectile['vy'] / dist) * projectile['speed']
                        app.projectiles.append(projectile)
            elif app.camera_mode == 2:
                if app.player.fire_rate > 0:
                    app.player.fire_rate -= 1
            
            for b in app.bullets[:]:
                b.update(app.game_speed, app)
                if not b.is_active:
                    app.bullets.remove(b)
                
            
            for v in app.projectiles[:]:
                v['x'] += v['vx']
                v['y'] += v['vy']
                if v['x'] < 0 or v['x'] > app.width or v['y'] < 0 or v['y'] > app.height:
                    app.projectiles.remove(v)
                    continue
                
                active_map = app.tutorial if app.insideGame == 'tutorial' else app.smart_map
                for obj in active_map.spawned:
                    if isinstance(obj, (Enemy, FlyingEnemy)) and getattr(obj, 'is_active', True):
                        proj_center_x = v['x']
                        proj_center_y = v['y']
                        proj_radius = v['radius']
                        
                        if (proj_center_x + proj_radius > obj.x and 
                            proj_center_x - proj_radius < obj.x + obj.width and
                            proj_center_y + proj_radius > obj.y and 
                            proj_center_y - proj_radius < obj.y + obj.height):
                            obj.is_active = False
                            app.enemies_killed += 1  
                            if v in app.projectiles:
                                app.projectiles.remove(v)
                            break

        
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

        for target in app.demo_targets:
            if target.flash_timer > 0:
                target.flash_timer -= 1
        
            

def onMouseMove(app, mouseX, mouseY):
    app.mouse_x, app.mouse_y = mouseX, mouseY


def onMousePress(app, mouseX, mouseY):
    app.mouse_pressed = True
    if app.state == 'gameover':
        cx = app.width / 2
        if cx - 180 <= mouseX <= cx + 180 and 610 <= mouseY <= 660:
            restart_game(app)
        elif cx - 180 <= mouseX <= cx + 180 and 680 <= mouseY <= 730:
            app.state = 'menu'


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
            app.character.x, app.character.y = 830, 600
            app.player.hp = app.player.max_hp
        elif key == 'space' and app.state == 'demo':
            app.camera_mode = 1 if app.camera_mode == 0 else 0
        elif key == 'enter' and app.state == 'demo':
            app.insideGame = 'tutorial'
            app.state = 'game'
            app.camera_mode = 1  # Default to hand mode
            app.tutorial = TutorialLevel()
            app.smart_map = RecursiveSmartMapGenerator(app.player)
            app.smart_map.respawnOnPlatform(app.player)
        elif key == 'space':
            if app.state == 'game':
                app.player.jump()
        elif key == 's':
            app.camera_mode = (app.camera_mode + 1) % 3  
        elif key == 'd' and app.state == 'game':
            app.player.dash(1)
        elif key == 'a' and app.state == 'game':
            app.player.dash(-1)
        elif key == 'f' and app.state == 'game' and app.camera_mode == 2:
            #
            if app.player.fire_rate == 0:
                projectile = {'x': app.player.x + app.player.width / 2, 'y': app.player.y + app.player.height / 2, 
                    'vx': app.player.projectile_speed, 'vy': 0,
                    'speed': app.player.projectile_speed,
                    'radius': app.player.projectile_size
                }
                app.projectiles.append(projectile)
                app.player.fire_rate = 10
                
                bullet_x = app.player.x + app.player.width
                bullet_y = app.player.y + app.player.height / 2 - 3
                app.bullets.append(Bullet(bullet_x, bullet_y))

    elif app.state == 'gameover':
        if key == 'r':
            restart_game(app)
        elif key == 'm':
            app.state = 'menu'
            app.player.hp = app.player.max_hp  
            app.character.x, app.character.y = 830, 600  
            app.player.hp = app.player.max_hp  # Reset HP when going to menu
            app.character.x, app.character.y = 830, 600  # Reset character position to avoid triggering game start

def drawGameOver(app):
    drawRect(0, 0, app.width, app.height, fill='black', opacity=85)
    
    cx = app.width / 2
    

    box_w, box_h = 460, 230
    box_x, box_y = cx - box_w / 2, 300
    
    drawLabel("STATS", cx, box_y + 35, fill='cyan', size=22, bold=True, font='monospace')
    
    drawLabel(f"Distance Reached : {int(app.distance)} m", cx, box_y + 85, fill='white', size=18, font='monospace')
    drawLabel(f"Enemies Defeated : {app.enemies_killed}", cx, box_y + 125, fill='white', size=18, font='monospace')
    drawLabel(f"Survival Time    : {int(app.survival_time)} s", cx, box_y + 165, fill='white', size=18, font='monospace')
    
    drawLabel("[ R ] RESTART MISSION", cx, 635, fill='white', size=18, bold=True, font='monospace')
    
    drawLabel("[ M ] RETURN TO MAIN MENU", cx, 705, fill='white', size=18, bold=True, font='monospace')

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
                            if app.tutorial_completed:
                                app.insideGame = 'smart'
                                app.state = 'game'
                                app.tutorial_guide.next_step()
                                app.tutorial_guide.show_highlights = False
                                app.smart_map = RecursiveSmartMapGenerator(app.player)
                                app.smart_map.respawnOnPlatform(app.player)
                            else:
                                app.state = 'game'
                            app.state = 'game'
                    if v == app.rightest_upper_building:
                        if not app.fenced:
                            app.msg_need_ca = 'please go to the fence to finish the lab'
                        else:
                            app.insideGame = 'tutorial'
                            app.state = 'game'
                            app.camera_mode = 1  
                            app.tutorial = TutorialLevel()
                            app.smart_map = RecursiveSmartMapGenerator(app.player)
                            app.smart_map.respawnOnPlatform(app.player)


                    else:

                        app.character.x, app.character.y = x, y


def redrawAll(app):
    if app.state == 'intro':
        app.intro.draw(app)

    elif app.state == 'menu':
        imageWidth, imageHeight = getImageSize(app.url)
        drawImage(app.url, app.width/2, app.height/2, align='center', width=imageWidth, height=imageHeight)
        
        if app.character.sprite:
            app.character.sprite.draw(app)
        else:
            drawCircle(app.character.x, app.character.y, 10, fill='red')
        
        if app.msg_need_ca != None:
            drawLabel(app.msg_need_ca, app.width//2, 30, fill= 'yellow', bold = True)
        
        if app.tutorial_guide.show_highlights and not app.tutorial_guide.completed:
            current_step = app.tutorial_guide.get_current_step()
            if current_step:
                # Draw story text overlay
                drawRect(app.width//2 - 300, 100, 600, 150, fill='black', opacity=85, border=current_step['color'], borderWidth=2)
                drawLabel(current_step['title'], app.width//2, 130, fill=current_step['color'], size=20, bold=True)
                drawLabel(current_step['text'], app.width//2, 180, fill='white', size=14)
                drawLabel(current_step['instruction'], app.width//2, 230, fill='gray', size=12, italic=True)
                
                if current_step['id'] == 'intro':
                    drawRect(app.fence.left, app.fence.top, app.fence.w, app.fence.h, fill='red', opacity=40, border='red', borderWidth=3)
                
                elif current_step['id'] == 'calibration_complete':
                    drawRect(app.rightest_upper_building.left, app.rightest_upper_building.top, app.rightest_upper_building.w, app.rightest_upper_building.h, fill='red', opacity=40, border='red', borderWidth=3)
                
                elif current_step['id'] == 'real_game' and app.tutorial_completed:
                    drawRect(app.middle_upper_building.left, app.middle_upper_building.top, app.middle_upper_building.w, app.middle_upper_building.h, fill='red', opacity=40, border='red', borderWidth=3)
        
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
        drawLabel(f"Objective: {hint_str} | Press [ SPACE ] Switch Mode | Press [ B ] Back to Town", 40, 50, fill='gray', size=13, align='left')
        
        drawRect(app.width//2 - 250, app.height - 100, 500, 50, fill='lime', opacity=30, border='lime', borderWidth=2)
        drawLabel("Press [ ENTER ] to proceed to Tutorial | Press [ B ] to return to Town", app.width//2, app.height - 75, fill='lime', size=14, bold=True)
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
    elif app.state in ('game', 'gameover'):
        app.bg.draw(app)
        drawLabel(f"HP: {app.player.hp}/{app.player.max_hp}", 80, 40, fill='red', size=24, bold=True, font='monospace')
        drawLabel(f"Distance: {int(app.distance)}m", 240, 40, fill='cyan', size=24, bold=True, font='monospace')
        

        app.player.draw(app)
        
        if app.camera_mode == 2:
            for b in app.bullets:
                b.draw(app)
        
        if app.camera_mode == 1:
            for proj in app.projectiles:
                drawCircle(proj['x'], proj['y'], proj['radius'], fill='yellow')

        if app.insideGame == 'tutorial': ##remember if not
            app.tutorial.draw(app)
            # Add B to return to town prompt
            drawRect(app.width//2 - 150, app.height - 60, 300, 40, fill='gold', opacity=30, border='gold', borderWidth=2)
            drawLabel("Press [ B ] to return to Town", app.width//2, app.height - 40, fill='gold', size=14, bold=True)
        elif app.insideGame == 'smart':
            app.smart_map.draw(app)
        
        #this button animation written by ai
        mode_btn_x, mode_btn_y = app.width - 220, 200
        mode_btn_w, mode_btn_h = 200, 50
        mode_color = 'cyan' if app.camera_mode == 0 else 'magenta' if app.camera_mode == 1 else 'lime'
        drawRect(mode_btn_x, mode_btn_y, mode_btn_w, mode_btn_h, fill=mode_color, opacity=80, border='white')
        mode_text = "EYE MODE" if app.camera_mode == 0 else "HAND MODE" if app.camera_mode == 1 else "KEYBOARD"
        drawLabel(mode_text, mode_btn_x + mode_btn_w//2, mode_btn_y + mode_btn_h//2, fill='white', size=14, bold=True)
        drawLabel("Look/Pinch/'S' to switch", mode_btn_x + mode_btn_w//2, mode_btn_y + mode_btn_h + 15, fill='gray', size=10)
        
        if app.camera_mode == 0:
            skill_color = 'gold' if app.special_skill_ready else 'gray'
            skill_text = "SKILL READY!" if app.special_skill_ready else "SKILL CHARGING..."
            
            drawRect(app.width/2 - 100, app.height - 80, 200, 40, fill=skill_color, opacity=30, border=skill_color, borderWidth=2)
            drawLabel(skill_text, app.width/2, app.height - 60, fill=skill_color, size=14, bold=True)
            
            if app.eye_skill_cooldown > 0:
                cooldown_pct = app.eye_skill_cooldown / 120
                drawRect(app.width/2 - 100, app.height - 80, 200 * cooldown_pct, 40, fill='red', opacity=50)
            
            if len(app.eye_history) >= 2:
                for i in range(len(app.eye_history) - 1):
                    x1, y1 = app.eye_history[i]
                    x2, y2 = app.eye_history[i + 1]
                    alpha = int(100 * (i / len(app.eye_history)))
                    alpha = min(100,alpha)
                    drawLine(x1, y1, x2, y2, fill='cyan', opacity=alpha)
            
            if app.gaze_x is not None and app.gaze_y is not None:
                cursor_color = 'gold' if app.special_skill_ready else 'cyan'
                drawCircle(app.gaze_x, app.gaze_y, 20, fill=cursor_color, opacity=50)  
                drawCircle(app.gaze_x, app.gaze_y, 8, fill='white')
            
            drawLabel("Move eyes LEFT-RIGHT rapidly to charge, look CENTER to upgrade WEAPON", app.width/2, app.height - 30, fill='gray', size=11)
        elif app.camera_mode == 1:
        #     hint_y = app.height - 120
        #     drawLabel("PINCH = JUMP", 100, hint_y, fill='lime', size=12, bold=True)
        #     drawLabel("FIST = DASH", 100, hint_y + 25, fill='orange', size=12, bold=True)
        #     drawLabel("PISTOL AIM = TRAJECTORY", 100, hint_y + 50, fill='cyan', size=12, bold=True)
        #     drawLabel("PISTOL FIRE = SHOOT", 100, hint_y + 75, fill='red', size=12, bold=True)
            
             
            if app.aim_trajectory:
                start_x, start_y = app.aim_trajectory['start']
                vx, vy = app.aim_trajectory['velocity']
                print('drawtra')
                drawLine(start_x,start_y,start_x + vx*60, start_y + vy*60, dashes = True)
                
            
            if app.vision.hand_x is not None and app.vision.hand_y is not None:
                print('vvvvvv')
                cursor_color = 'lime' if app.vision.hand_gesture == 'PINCH' else 'orange' if app.vision.hand_gesture == 'FIST' else 'cyan' if app.vision.hand_gesture == 'PISTOL_AIM' else 'red' if app.vision.hand_gesture == 'PISTOL_FIRE' else 'magenta'
                drawCircle(app.vision.hand_x, app.vision.hand_y, 20, fill=cursor_color, opacity=50)
                drawCircle(app.vision.hand_x, app.vision.hand_y, 8, fill='white')
                drawLabel(f"Gesture: {app.vision.hand_gesture}", app.vision.hand_x, app.vision.hand_y + 35, fill=cursor_color, size=11, bold=True)
        else:  
            hint_y = app.height - 120
            drawLabel("SPACE = JUMP", 100, hint_y, fill='lime', size=12, bold=True)
            drawLabel("A/D = DASH LEFT/RIGHT", 100, hint_y + 25, fill='orange', size=12, bold=True)
            drawLabel("F = SHOOT", 100, hint_y + 50, fill='red', size=12, bold=True)
            drawLabel(f"Weapon Level: {app.player.weapon_level}/{app.player.max_weapon_level}", 100, hint_y + 75, fill='gold', size=12, bold=True)
        if app.state == 'gameover':
                drawGameOver(app)


def onAppStop(app):
    app.is_running = False
    if hasattr(app, 'vision_thread'):
        app.vision_thread.stop()


if __name__ == '__main__':
    runApp(width=1500, height=1000)
