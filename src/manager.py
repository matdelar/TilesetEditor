import pygame
import sys
from array import array

import pygame
import moderngl

class Manager:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()

        self.properties = {
            'name': "MyGame",
            'size': [1280, 720],
            'icon': None,
            'startScene': 'menu',
            'fps': 0,
            'backgroundColor': (0, 0, 0)
        }
        self.mainScreen = pygame.display.set_mode(self.properties['size'])
        #print(pygame.display.get_init())
        self.lastScene = self.properties['startScene']
        self.currentScene = self.lastScene
        self.running = True
        self.scenes = None
        self.consoleDebug = False
        self.applyProperties()

    def applyProperties(self):
        self.clock = pygame.time.Clock()
        self.mainScreen = pygame.display.set_mode(self.properties['size'])
        self.screen = pygame.Surface(self.properties['size'])
        pygame.display.set_caption(self.properties['name'])
        self.lastScene = self.properties['startScene']
        self.currentScene = self.lastScene
        try:
            i = pygame.image.load(self.properties['icon'])
            pygame.display.set_caption(self.properties['name'])
        except:
            if self.consoleDebug:
                print("No icon found, using default")

    def setProperties(self, **kwargs):
        for arg in kwargs:
            self.properties[arg] = kwargs[arg]
        self.applyProperties()

    def start(self):
        if self.scenes == None:
            raise ValueError("No scenes declared")
        else:
            while self.running:
                self.screen.fill(self.properties['backgroundColor'])
                for e in pygame.event.get(pygame.QUIT):
                    if e.type == pygame.QUIT:
                        self.running = False
                newScene = self.scenes[self.currentScene].update(self.screen)
                if newScene != None:
                    self.lastScene = self.currentScene
                    self.currentScene = newScene
                    if newScene == 'quit':
                        self.running = False

                self.mainScreen.blit(self.screen, (0, 0))
                pygame.display.update()
                self.clock.tick(self.properties['fps'])
            pygame.quit()
