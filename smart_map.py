import math
#different pools
#hardcoded level
#some code for map gen
class Platform:
    def __init__(self,x,y,width,height = 30):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    def update(self,game_speed,app):
        self.x -= game_speed

    def draw(self,app):
        pass
        #image
    
    def on_player_stepped(self,player):
        #effect of player stepping on
        pass

class MovingPlatform(Platform):
    def __init__(self,x,y,width,move_range = 100, move_speed = 0.05, vertical = True):
        super().__init__(x,y,width)
       
        self.base_y = y
        self.base_x = x
        self.move_range = move_range
        self.move_speed = move_speed
        self.vertical = vertical
        self.time_step = 0
    def update(self,game_speed,app):
        super().update(game_speed)
        self.base_x -= game_speed
        self.time_step += self.move_speed
        deviates = math.sin(self.time_step) * self.move_range
        if self.vertical:
            self.y = self.base_y + deviates
        else:
            self.x = self.base_x + deviates

class CrumblingPlatform(Platform):
    def __init__(self,x,y,width):
        super().__init__(x,y,width)
    
        self.stepped = False
        self.timer = 30
        self.is_broken = False

    def on_player_stepped(self,player):
        self.stepped = True

    def update(self,game_speed, app =None):
        super().update(game_speed)
        if self.stepped and not self.is_broken:
            self.timer -= 1
            if self.timer <= 0:
                self.is_broken = True

    def draw(self, app):
        if self.is_broken: 
            return
        #draw



#gemini flash helped with debug
class GazeDoor(Platform):
    def __init__(self, x, y, width, height):
        super().__init__(x,y,width,height)
        self.progress = 0.0 
        self.is_unlocked = False

    def check_interaction(self,x, y, is_pinching=False, mode=0):
        if self.is_unlocked or x is None or y is None:
            return
        
        cx, cy = self.x + self.w / 2, self.y + self.h / 2
        dist = ((x - cx)**2 + ( y - cy)**2)**0.5
        
        if dist < max(self.width, self.height): 
            if mode == 0:  
                self.progress = min(1.0, self.progress + 0.08)
            else:       
                if is_pinching:
                    self.progress = min(1.0, self.progress + 0.08)
        else:
            self.progress = max(0.0, self.progress - 0.02)

        if self.progress >= 1.0:
            self.is_unlocked = True
            self.is_active = False  

    def draw(self, app):
        if self.is_unlocked: return
        drawRect(self.x, self.y, self.w, self.h, fill='magenta', border='cyan', borderWidth=3, opacity=80)
        if self.progress > 0:
            dw = self.w * self.progress
            drawRect(self.x, self.y - 15, dw, 8, fill='lime')
        drawLabel("LOOK / PINCH TO UNLOCK", self.x + self.w/2, self.y + self.h/2, fill='white', size=11, bold=True)
