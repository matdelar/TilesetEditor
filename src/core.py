import pygame, abc

class SceneBase(abc.ABC):
    def __init__(self):
        self.context = None
        self.content = None
    
    def setContext(self,context):
        self.context = context
    
    def update(self,screen):
        if self.content != None:
            for component in self.content:
                if self.content[component].autoUpdate:
                    self.content[component].update(screen)

class ComponentBase(abc.ABC):
    def __init__(self):
        self.context = None
        self.properties = None
        self.autoUpdate = True
    
    def setProperties(self,**kwargs):
        for arg in kwargs:
            self.properties[arg] = kwargs[arg]

    def setContext(self,context):
        self.context = context
    
    def update(self):
        pass
        