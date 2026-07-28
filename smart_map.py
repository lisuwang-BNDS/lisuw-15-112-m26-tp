import math
from cmu_graphics import *
import random
#different pools
#hardcoded level
#some code for map gen
class GameObject():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.right = self.x + self.width
        self.height = height
        self.bottom = self.y +self.height
        self.is_active = True
  
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def collides_with(self, other):
        ox,oy,ow,oh = other.get_rect()
        oright = ox + ow
        odown = oy + oh
        LeftOver = self.x < oright
        RightOver = self.right > ox
        HoriOver = LeftOver and RightOver
        TopOver = self.y < odown
        BotoOver = self.bottom > oy
        VerOver = TopOver and BotoOver

        if HoriOver and VerOver:
            return True
        return False

    
class Platform(GameObject):
    def __init__(self,x,y,width,height = 30):
        super().__init__(x,y,width,height)

    def update(self,game_speed,app):
        self.x -= game_speed

    def draw(self,app):
        drawRect(self.x, self.y, self.width, self.height, fill='gray')
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
    def draw(self, app):
        color = 'orange' if self.vertical else 'yellow'
        drawRect(self.x, self.y, self.width, self.height, fill=color)


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
        shake = 0
        if self.stepped and self.timer > 0:
            shake = random.randint(-2, 2)
        drawRect(self.x + shake, self.y, self.width, self.height, fill='brown')
        if self.stepped and self.timer > 0:
            drawLabel(f"{self.timer}", self.x + self.width/2, self.y - 10, fill='red', size=16)




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

class Obstacle(GameObject):

    def __init__(self, x, y, width, height, damage=1):
        super().__init__(x, y, width, height)
        self.damage = damage

class Spike(Obstacle):
    def __init__(self, x, y, width=30, height=30):
        super().__init__(x, y, width, height)
    
    def update(self, game_speed, app):
        self.x -= game_speed
    
    def draw(self, app):
        drawPolygon(self.x,self.y, self.width, 3, fill='red')
    
class Enemy(Obstacle):
    def __init__(self, x, y, width=40, height=60, patrol_range=100):
        super().__init__(x, y, width, height)
        self.base_x = x #enemy sefl
        self.patrol_range = patrol_range
        self.direction = 1
        self.speed = 2
    
    def update(self, game_speed, app):
        self.base_x -= game_speed
        #for pistol
        self.x = self.base_x + math.sin(app.stepsPerSecond * 0.05) * self.patrol_range
    
    def draw(self, app):
        drawRect(self.x, self.y, self.width, self.height, fill='purple')


class FlyingEnemy(Obstacle):
    def __init__(self, x, y, width=40, height=40):
        super().__init__(x, y, width, height)
        self.base_y = y
        self.base_x = x
        self.wing_angle = 0
    
    def update(self, game_speed, app):
        self.base_x -= game_speed
        self.x = self.base_x
        self.y = self.base_y + math.sin(app.stepsPerSecond * 0.1) * 30
        self.wing_angle += 0.3
    
    def draw(self, app):
        drawCircle(self.x + self.width/2, self.y + self.height/2, 15, fill='darkGreen')
        wing = math.sin(self.wing_angle) * 10
        drawOval(self.x - 10, self.y + wing, 20, 10, fill='lime')
        drawOval(self.x + self.width - 10, self.y + wing, 20, 10, fill='lime')

        

#this class of collectible (especially the animation of angle) desgiend by gemini flash
class Collectible(GameObject):
    def __init__(self, x, y, width=30, height=30, value=10):
        super().__init__(x, y, width, height)
        self.value = value
        self.collected = False
        self.angle = random.random() * math.pi * 2
    
    def update(self, game_speed, app):
        self.x -= game_speed
        self.angle += 0.1
        self.y += math.sin(self.angle) * 0.5
    
    def on_collect(self, player):
        self.collected = True
        self.is_active = False
        return self.value
    