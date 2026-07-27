import math

class Platform:
    def __init__(self,x,y,width,height = 30):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = 'NORMAL'
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
        self.type = 'MOVING'
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
        self.type = 'CRUMBLING'
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

