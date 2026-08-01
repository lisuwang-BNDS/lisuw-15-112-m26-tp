class TutorialStory:
    def __init__(self):
        self.current_step = 0
        self.completed = False
        self.story_steps = self._create_story()
        
    def _create_story(self):
        return  [
    {
        'id': 'intro',
        'title': 'WELCOME TO ENVISION 112',
        'text': 'Welcome, Envisioner 112. In this darkness,\nyou need adaptive perception to navigate the unseen.',
        'color': 'cyan',
        'instruction': 'Press [SPACE] to continue'
    },
    {
        'id': 'vision_intro',
        'title': 'OCULAR INTERFACE SYNC',
        'text': 'First, we calibrate your ocular matrix.\nThis allows you to guide your path.',
        'color': 'magenta',
        'instruction': 'Press [SPACE] to begin calibration'
    },
    {
        'id': 'calibration',
        'title': 'SIGHT CALIBRATION',
        'text': 'Look at the point. press space to start to collect info \nHold your focus steady until the bar fills.',
        'color': 'yellow',
        'instruction': 'Calibrating...'
    },
    {
        'id': 'hand_intro',
        'title': 'TACTILE ASSIST SYSTEM',
        'text': 'Outstanding >_<  Now, bridge touch with perception.\nPinch to leap, fist to dash left or right depends on the postion of your fist, and pistol to strike.',
        'color': 'lime',
        'instruction': 'Press [SPACE] to learn gestures'
    },
    {
        'id': 'hand_practice',
        'title': 'GESTURE PRACTICE',
        'text': 'Feel the motion cues:\nPINCH - Jump\nFIST - Dash\nPISTOL - Aim / Shoot',
        'color': 'white',
        'instruction': 'Practicing gestures...'
    },
    {
        'id': 'mission',
        'title': 'PROTOCOL 112 INITIATED',
        'text': 'Your sensory bridge is online. \nHello World!',
        'color': 'cyan',
        'instruction': 'Press [SPACE] to launch'
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
