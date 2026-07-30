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
    
        self.height = height
       
        self.is_active = True
  
    
    def get_rect(self):
        return (self.x, self.y, self.width, self.height)
    
    def collides_with(self, other):
        ox, oy, ow, oh = other.get_rect()
        oright = ox + ow
        odown = oy + oh
        
        current_right = self.x + self.width
        current_bottom = self.y + self.height
        
        LeftOver = self.x < oright
        RightOver = current_right > ox     
        HoriOver = LeftOver and RightOver
        
        TopOver = self.y < odown
        BotoOver = current_bottom > oy    
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
        super().update(game_speed,app)
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
        super().update(game_speed,app)
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
        
        cx, cy = self.x + self.width / 2, self.y + self.height / 2
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
        drawRect(self.x, self.y, self.width, self.height, fill='magenta', border='cyan', borderWidth=3, opacity=80)
        if self.progress > 0:
            dw = self.width * self.progress
            drawRect(self.x, self.y - 15, dw, 8, fill='lime')
        drawLabel("LOOK / PINCH TO UNLOCK", self.x + self.width/2, self.y + self.height/2, fill='white', size=11, bold=True)

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


class Coin(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, 25, 25)
    
    def draw(self, app):
        if self.collected:
            return
        drawCircle(self.x, self.y , 12, fill='gold')
        drawLabel("$", self.x , self.y , fill='orange')

class Gem(Collectible):
    def __init__(self, x, y, color='cyan'):
        super().__init__(x, y, 20, 30, value=25)
        self.color = color
    
    def draw(self, app):
        if self.collected:
            return
        
        drawPolygon(self.x,self.y,12, 4, fill=self.color)


class HealthPack(Collectible):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, value=1)
    
    def draw(self, app):
        if self.collected:
            return
        drawRect(self.x , self.y, 20, 30, fill='red')


#the following two platform's function and features designed by gemini flash 
class Spring(Platform):
    def __init__(self, x, y, width=40, height=20, boost_power=-20):
        super().__init__(x, y, width, height)
        self.boost_power = boost_power
        self.compressed = False
        self.compress_timer = 0
    
    def on_player_stepped(self, player):
        if not self.compressed:
            self.compressed = True
            self.compress_timer = 5
            player.vy = self.boost_power
            player.is_grounded = False
    
    def update(self, game_speed, app):
        super().update(game_speed, app)
        if self.compressed:
            self.compress_timer -= 1
            if self.compress_timer <= 0:
                self.compressed = False
    
    def draw(self, app):
        if self.compressed:
            drawRect(self.x, self.y + 10, self.width, self.height - 10, fill='lime')
        else:
           drawRect(self.x, self.y + self.height - 5, self.width, 5, fill='green')


class BouncyPlatform(Platform):
    def __init__(self, x, y, width, bounciness=1.5):
        super().__init__(x, y, width)
        self.bounciness = bounciness
    
    def on_player_stepped(self, player):
        player.vy = -abs(player.vy) * self.bounciness
        if abs(player.vy) < 8:
            player.vy = -12
    
    def draw(self, app):
        drawRect(self.x, self.y, self.width, self.height, fill='pink')
        drawLabel("BOUNCE", self.x, self.y , fill='white')

######HARD COOOODEED TUTORIAL LEVEL.  TAT
class TutorialLevel:
    def __init__(self):
        self.gameobjects = []
        self.current = 0
        self.sections = self._create()
        self.spawned = []
        self.section_start_x = 0
        self.text = ""
        self.timer = 0
        self.totdis = 0  #
    #some part of the tedious parameter is handled by gemini thinking model
    def _create(self):
        return [
                    {
                        'name': 'Basic Platforms',
                        'text': 'This is what every envisioner must goes through <_<, jump on these to see what you can do! ',
                        'objects': [
                            Platform(400, 750, 200),
                            Platform(950, 700, 200),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Moving Platforms',
                        'text': 'Great moves, now time your jumps !',
                        'objects': [
                            MovingPlatform(400, 750, 150, move_range=80, vertical=True),
                            MovingPlatform(950, 700, 150, move_range=60, vertical=True),
                            MovingPlatform(1500, 650, 150, move_range=100, vertical=True),
                        ]
                    },
                    {
                        'name': 'Crumbling Platforms',
                        'text': '',
                        'objects': [
                            CrumblingPlatform(400, 750, 150),
                            Platform(900, 700, 100),
                            CrumblingPlatform(1300, 650, 150),
                            Platform(1700, 600, 200),
                        ]
                    },
                    {
                        'name': 'Bouncy Platforms',
                        'text': '',
                        'objects': [
                            BouncyPlatform(400, 750, 150, bounciness=1.8),
                            Platform(950, 650, 150),
                            BouncyPlatform(1400, 550, 150, bounciness=2.0),
                            Platform(1850, 450, 200),
                        ]
                    },
                    {
                        'name': 'Springs',
                        'text': '',
                        'objects': [
                            Spring(450, 780, boost_power=-18),
                            Platform(900, 650, 200),
                            Spring(1350, 630, boost_power=-22),
                            Platform(1800, 500, 200),
                        ]
                    },
                    
                    {
                        'name': 'Collectibles - Coins',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            Coin(450, 700),
                            Coin(500, 700),
                            Platform(950, 700, 200),
                            Coin(1000, 650),
                            Coin(1050, 650),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Collectibles - Gems',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            Gem(450, 700),
                            Platform(950, 650, 200),
                            Gem(1000, 600),
                            Gem(1050, 600),
                            Platform(1500, 550, 200),
                        ]
                    },
                    {
                        'name': 'Health Packs',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            HealthPack(500, 700),
                            Platform(950, 700, 200),
                            HealthPack(1050, 650),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Spikes',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            Spike(500, 770),
                            Platform(950, 700, 200),
                            Spike(1050, 720),
                            Spike(1100, 720),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Ground Enemies',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 300),
                            Enemy(500, 690, patrol_range=80),
                            Platform(950, 700, 300),
                            Enemy(1050, 640, patrol_range=100),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Flying Enemies',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            FlyingEnemy(500, 600),
                            Platform(950, 700, 200),
                            FlyingEnemy(1050, 550),
                            Platform(1500, 650, 200),
                        ]
                    },
                    {
                        'name': 'Gaze Doors',
                        'text': '',
                        'objects': [
                            Platform(400, 750, 200),
                            GazeDoor(950, 650, 80, 100),
                            Platform(1150, 650, 200),
                        ]
                    },
        
                ]


    def update(self,gamespeed, app):
        self.totdis += gamespeed
        if self.current < len(self.sections):
            section = self.sections[self.current]
            secStar = self.current * 1400 #each sec 1400 px (increased for wider platform spacing)
            secEnd = secStar + 1400
            if self.totdis >= secStar and not any(v for v in self.spawned if hasattr(v, 'hadsec' ) and v.hadsec == self.current):
                for v in section['objects']:
                    newX = app.width + 200 + v.x*0.5
                    new = self.getanother(v, newX)
                    new.hadsec = self.current
                    self.spawned.append(new)
                self.text = section['text']
                self.timer = 180
            if self.totdis >= secEnd:
                self.current += 1
            if self.timer > 0:
                self.timer -= 1
            else:
                self.text = '' #######
            for v in self.spawned[:]:
                v.update(gamespeed,app)
                if v.x < -200:
                    self.spawned.remove(v)
    def getanother(self,v,newX):
        classOfclone = v.__class__
        if classOfclone == Platform:
            return classOfclone(newX, v.y, v.width, v.height)
        elif classOfclone == MovingPlatform:
            return classOfclone(newX, v.y, v.width, v.move_range, v.move_speed, v.vertical)
        elif classOfclone == CrumblingPlatform:
            return classOfclone(newX, v.y, v.width)
        elif classOfclone == BouncyPlatform:
            return classOfclone(newX, v.y, v.width, v.bounciness)
        elif classOfclone == Spring:
            return classOfclone(newX, v.y, v.width, v.height, v.boost_power)
        
        elif classOfclone == Spike:
            return classOfclone(newX, v.y, v.width, v.height)
        elif classOfclone == Enemy:
            return classOfclone(newX, v.y, v.width, v.height, v.patrol_range)
        elif classOfclone == FlyingEnemy:
            return classOfclone(newX, v.y, v.width, v.height)
        elif classOfclone == Coin:
            return classOfclone(newX, v.y)
        elif classOfclone == Gem:
            return classOfclone(newX, v.y, v.color)
        elif classOfclone == HealthPack:
            return classOfclone(newX, v.y)
        elif classOfclone == GazeDoor:
            return classOfclone(newX, v.y, v.width, v.height)
        else:
            return classOfclone

    def draw(self,app):
        for v in self.spawned:
            if v.is_active:
                v.draw(app)
        if self.text:
            drawLabel(self.text,app.width//2, 75, fill ='white')


    def check_collisions(self,player,app):
        playerinfo = player.get_rect()
        playeIsOnPlat = False
        highestPl = 900
        landedPl = None
        
        for v in self.spawned:
            if v.is_active == False:
                continue
            if isinstance(v, GazeDoor):
                if v.collides_with(player):
                    if hasattr(app, 'gaze_x') and hasattr(app, 'gaze_y'):
                       v.check_interaction(app.gaze_x, app.gaze_y, is_pinching=(app.vision.hand_gesture == 'PINCH' if hasattr(app, 'vision') else False), mode=app.camera_mode if hasattr(app, 'camera_mode') else 0)
            
            if isinstance(v, Platform):
                if v.collides_with(player):
                    playerBot = player.y + player.height
                    playerTop = player.y
                    playerLeft = player.x
                    playerRight = player.x + player.width
                    playerLastBot = playerBot - player.vy
                    playerLastTop = playerTop - player.vy
                    
                    if playerLastBot <= v.y + 5 and player.vy >= 0 and playerBot >= v.y:
                        if v.y < highestPl:
                            highestPl = v.y
                            playeIsOnPlat = True
                            landedPl = v
                    
                    elif playerLastTop >= v.y + v.height - 5 and player.vy < 0 and playerTop <= v.y + v.height:
        
                        player.y = v.y + v.height
                        player.vy = 0
                    
                    elif playerRight >= v.x and playerLeft < v.x:
                        player.x = v.x - player.width
                    
                    elif playerLeft <= v.x + v.width and playerRight > v.x + v.width:
                        player.x = v.x + v.width
            
            elif isinstance(v, Collectible):
                if v.collides_with(player):
                    if not v.collected:
                        v.on_collect(player)

            elif isinstance(v, Obstacle):
                if v.collides_with(player):
                    #  damage 
                    player.x = 200
                    player.y = 730
                    player.vy = 0
                    player.jumps_remaining = player.max_jumps  
            
        if playeIsOnPlat and landedPl:
            player.y = highestPl - player.height
            player.vy = 0
            player.is_grounded = True
            player.ground_y = highestPl
            player.jumps_remaining = player.max_jumps 
            landedPl.on_player_stepped(player)
        else:
            if player.y + player.height >= 900:
                player.y = 900 - player.height
                player.vy = 0
                player.is_grounded = True
                player.ground_y = 900
                player.jumps_remaining = player.max_jumps  
            else:
                player.is_grounded = False
                player.ground_y = 900

#integtate. camera 

#simple harded only one jump eye and hand , double jumop and dash 

#rand0om just do regular 


#UI... UX

#same with jumpping and dash, max length, double jump max h, dash max x, _____range depends on difficulty. On of diffcult move per move
#acheive. poools diff combination . key 
#new-complexity, backtracking?

class RecursiveSmartMapGenerator:
    def __init__(self,player,depthPertime = 4):
        self.player = player
        self.spawned = []
        self.sumDist = 0
        self.depthPertime = depthPertime
        self.last_y = 750
        self.last_width = 400
        start = Platform(0,750,400)
        self.spawned.append(start)
        self.last_x = 400
    def getDifficulty(self):
        return min(1.0, self.sumDist / 15000.0)
    def update(self,speed,app):
        self.sumDist += speed
        for v in self.spawned[:]:
            v.update(speed, app)
            if getattr(v,'x',0) + getattr(v,'width', 50) < -300:
                self.spawned.remove(v)
        self.last_x -= speed
        if self.last_x < app.width + 800:
            self.genChunkRec(app)
    def genChunkRec(self,app):
        diff = self.getDifficulty()
        path = self._BackTrac(self.last_x,self.last_y, self.last_width, 0, self.depthPertime, diff)
        if path:
            for plat, things in path:
                self.spawned.append(plat)
                for v in things:
                    self.spawned.append(things)
                self.last_x = plat.x  + plat.width
                self.last_y = plat.y
                self.last_width = plat.width
        else:
            failed = Platform(self.last_x + 150, 750, 300)
            self.spawned.append(failed)
            self.last_x = failed.x + failed.width
            self.last_y = failed.y 
            self.last_width = failed.width

    def _BackTrac(self, curX, curY, curW, depth, MaxDepth, diff):
        if depth >= MaxDepth:
            return [] #base case, find the road
        else:
            potential = self._GetJumpPoten(diff)
            random.shuffle(potential)
            for dx,dy, width, Plats in potential:
                nextX = curX + dx
                nextY = curY + dy
                if self._isLegal(nextY, Plats, diff):
                    plat = self._makePlat(Plats, nextX, nextY, width, diff)
                    things = self._makeThing(plat, diff)
                    possibleSol = self._BackTrac(nextX + width, nextY, width, depth + 1,MaxDepth, diff)
                    if possibleSol != None:
                        return [(plat, things)] + possibleSol
            return None
    def _GetJumpPoten(self,diff):
        potential = [(random.randint(120, 200), random.randint(-60, 60), random.randint(160, 260), Platform),
            (random.randint(160, 240), random.randint(-100, 40), random.randint(140, 220), Platform)]
        if diff  > 0.3:
            potential.append((random.randint(180, 280), random.randint(-80, 80), random.randint(120, 180), MovingPlatform))
            potential.append((random.randint(150, 220), random.randint(-40, 40), random.randint(120, 180), CrumblingPlatform))
        if diff > 0.5:
            potential.append((random.randint(220, 320), random.randint(-160, -60), random.randint(100, 160), Spring))
            potential.append((random.randint(200, 300), random.randint(-80, 80), random.randint(100, 160), BouncyPlatform))
        return potential

    def _isLegal(self, y, Plats, diff):
        if y < 300 or y > 900:
            return False
        return True
    def _makePlat(self,Plats, nextX,nextY,width,diff):
        if Plats == MovingPlatform:
            return MovingPlatform(nextX,nextY, width, move_range=random.randint(50, 100), vertical=random.choice([True, False]))
        elif Plats == BouncyPlatform:
            return BouncyPlatform(nextX,nextY, width, random.uniform(1.4, 1.9) )
        elif Plats == Spring:
            return Spring(nextX,nextY, width=40, boost_power=-24)
        elif Plats == CrumblingPlatform:
            return CrumblingPlatform(nextX,nextY, width)
        else:
            return Platform(nextX,nextY, width)
    
    def _makeThing(self,plat,diff):
        things = []
        px, py, pw = plat.x, plat.y, plat.width
        if random.random() < (0.2 + diff * 0.3) and pw >= 120:
            tType = random.choice(['spike', 'enemy', 'gaze_door'])
            if tType  == 'spike' and not isinstance(plat, (MovingPlatform, CrumblingPlatform)):
                things.append(Spike(px + pw / 2 - 15, py - 30))
            elif tType  == 'enemy' and pw >= 160:
                things.append(Enemy(px + pw / 2, py - 60, patrol_range=min(60, pw // 4)))
            elif tType  == 'gaze_door' and diff > 0.4:
                things.append(GazeDoor(px + pw / 2 - 40, py - 100, 80, 100))
        elif random.random() < 0.5:
            item_type = random.choice(['coin', 'gem'])
            if item_type == 'coin':
                things.append(Coin(px + pw / 2, py - 35))
            else:
                things.append(Gem(px + pw / 2, py - 35))
                
        return things
    def draw(self, app):
        for v in self.spawned:
            if getattr(v, 'is_active', True):
                v.draw(app)
    def checkCollision(self,player,app):
        pass