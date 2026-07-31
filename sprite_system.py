from cmu_graphics import *
from PIL import Image

class SpriteSheet:
    def __init__(self, path, rows, cols):
        self.sheet = Image.open(path)
        if self.sheet.mode != 'RGBA':
            self.sheet = self.sheet.convert('RGBA')
        self.rows = rows
        self.cols = cols
        self.frameWidth = self.sheet.size[0] / self.cols
        self.frameHeight = self.sheet.size[1] / self.rows
        self.frames = {}
        self.loadFrames()
    
    def getOriginalFrameSize(self):
        return int(self.frameWidth), int(self.frameHeight)

    def loadFrames(self):
        for row in range(self.rows):
            self.frames[row] = []
            for col in range(self.cols):
                left = int(self.frameWidth * col)
                top = int(self.frameHeight * row)
                right = int(left + self.frameWidth)
                bottom = int(top + self.frameHeight)
                frame = self.sheet.crop((left, top, right, bottom))
                if frame.mode != 'RGBA':
                    frame = frame.convert('RGBA')
                cmu_frame = CMUImage(frame)
                self.frames[row].append(cmu_frame)

    def getFrame(self, direction, frameIndex):
        return self.frames[direction][frameIndex]


class AnimatedSprite:
    def __init__(self, spriteSheet, startX, startY, width, height):
        self.spriteSheet = spriteSheet
        self.x = startX
        self.y = startY
        self.width = width
        self.height = height
        self.frameIndex = 0
        self.animTimer = 0
        self.animSpeed = 5
    
    def update(self, dx, dy):
        self.x += dx
        self.y += dy
    
    def updateAnimation(self):
        self.animTimer += 1
        if self.animTimer >= self.animSpeed:
            self.animTimer = 0
            self.frameIndex = (self.frameIndex + 1) % self.spriteSheet.cols
    
    def draw(self, app):
        currentFrame = self.spriteSheet.getFrame(0, self.frameIndex)
        drawImage(currentFrame, self.x, self.y, align='center', 
                  width=self.width, height=self.height)
