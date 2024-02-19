import math
import src.core as core
import src.globals as g
import pygame


class Text(core.ComponentBase):
    def __init__(self, pos=(0, 0), text="SampleText", fontSize=20, textColor=(255, 255, 255), font=None, antialiased=False):
        super().__init__()
        pygame.font.init()
        self.pos = pos
        self.text = text
        self.size = fontSize
        self.color = textColor
        self.font = pygame.font.Font(font, self.size)
        self.antialiased = antialiased
        self.render = self.font.render(self.text, antialiased, self.color)

    def update(self, screen):
        screen.blit(self.render, self.pos)

    def setText(self, newText):
        self.render = self.font.render(
            str(newText), self.antialiased, self.color)


class Button(Text):
    def __init__(self, backGroundColor=(20, 20, 20), size=(50, 50), pos=(0, 0), text="Button", fontSize=20, color=(255, 255, 255), font=None, antialiased=False):
        super().__init__(pos=pos, text=text, fontSize=fontSize,
                         textColor=color, font=font, antialiased=antialiased)
        self.size = size
        self.bgColor = backGroundColor
        self.rect = pygame.Rect(self.pos, self.size)
        self.pos = self.rect.centerx-self.render.get_width()/2, self.rect.centery - \
            self.render.get_height()/2

    def update(self, screen):
        pygame.draw.rect(screen, self.bgColor, self.rect)
        super().update(screen)

    def get_click(self):
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            for e in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if e.type == pygame.MOUSEBUTTONDOWN:
                    return True
        return False


class Transition(core.ComponentBase):
    def __init__(self, color=(30, 20, 40)):
        super().__init__()
        self.color = color
        self.state = True
        self.size = pygame.display.get_surface().get_size()
        self.startPos = [0, 0]
        self.endPos = [0, self.size[1]]
        self.currentPos = self.startPos

    def update(self, screen):
        pygame.draw.rect(screen, self.color, (self.currentPos, self.size))
        if self.state:
            # Lerp: a + (b - a) * t
            self.currentPos[1] += (self.endPos[1]-self.currentPos[1])*0.125
        elif self.state == False:
            self.currentPos[1] += -self.currentPos[1] * 0.125

        super().update()

    def progress(self):
        return self.currentPos[1]/self.endPos[1]

    def prepare(self):
        self.state = False

    def is_ready(self):
        return self.progress() < 0.01 and self.state == False


class Slider(core.ComponentBase):
    def __init__(self, pos=(25, 25), vertical=False, sizeX=250,handleSize=(16,16), bgColor=(100, 100, 100), fgColor=(200, 200, 200), width=5):
        super().__init__()
        self.pos = pos
        self.size = sizeX
        self.width = width
        self.endpos = [pos[0]+self.size *
                       (not vertical), pos[1]+self.size*vertical]
        self.bgColor = bgColor
        self.fgColor = fgColor
        self.handleRect = pygame.Rect((0, 0), handleSize)
        self.handleRect.center = self.pos
        self.handleRect.update(self.handleRect)
        self.isHolding = False
        self.value = 0
        self.lastvalue = 0
        self.isVertical = vertical

    def hasChangedValue(self):
        return self.value == self.lastvalue
    
    def getHover(self,x,y):
        return self.handleRect.collidepoint(x, y)

    def update(self, screen):
        super().update()
        pygame.draw.line(screen, self.bgColor, self.pos,
                         self.endpos, self.width)
        pygame.draw.rect(screen, self.fgColor, self.handleRect)
        self.lastvalue = self.value

        x, y = pygame.mouse.get_pos()
        if self.getHover(x,y):
            for e in pygame.event.get(pygame.MOUSEBUTTONDOWN):
                if e.type == pygame.MOUSEBUTTONDOWN:
                    self.isHolding = True
        

        if self.isHolding:
            if self.isVertical:
                self.handleRect.centery = min(max(y, self.pos[1]), self.endpos[1])
                self.handleRect.update(self.handleRect)

                self.value = 1 - \
                    (self.endpos[1]-self.handleRect.centery) / \
                    (self.endpos[1]-self.pos[1])
            else:
                self.handleRect.centerx = min(max(x, self.pos[0]), self.endpos[0])
                self.handleRect.update(self.handleRect)

                self.value = 1 - \
                    (self.endpos[0]-self.handleRect.centerx) / \
                    (self.endpos[0]-self.pos[0])
            
            for e in pygame.event.get(pygame.MOUSEBUTTONUP):
                if e.type == pygame.MOUSEBUTTONUP:
                    self.isHolding = False

    def getValue(self):
        return self.value


class Tile(core.ComponentBase):
    def __init__(self, pos=[0, 0], size=[32, 32], animation=None, type=None):
        super().__init__()
        self.anim = animation
        self.pos = pos
        self.size = size
        self.type = type
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self, screen,cam=[0,0]):

        super().update()
        if self.anim != None:
            self.anim.update(screen,cam)

    def getRect(self):
        return self.rect

    def toJson(self):
        if self.anim == None:
            return None
        else:
            x,y = self.anim.subSurfRect.topleft
            w,h = self.anim.subSurfRect.size


            return [x,y,w,h]
    
    def updateAnim(self,tex2d:pygame.Surface|None,newAnim:pygame.Rect|None):
        if tex2d == None:
            self.anim = None
        elif tex2d != None:
            self.anim = RenderObject(self.pos,self.size,tex2d,newAnim)




class Tileset(core.ComponentBase):
    def __init__(self, origin=[0, 0], tileSize=[32, 32], gridSize=[10, 10]):
        super().__init__()
        self.origin = origin
        self.tileSize = tileSize
        self.gridSize = gridSize

        self.color = (255, 0, 0)
        self.grid = []

        w, h = self.tileSize

        self.boundRect = pygame.Rect(
            self.origin, (w*self.gridSize[0], self.gridSize[1]*h))

        x, y = self.gridSize

        for j in range(y):
            for i in range(x):
                self.grid.append(
                    Tile((i*w+self.origin[0], j*h+self.origin[1]), self.tileSize))
    
    def resetIndex(self):
        newGrid = [core.ComponentBase]*(self.gridSize[0]*self.gridSize[1])
        for tile in self.grid:
            xy = tile.pos
            ox,oy = self.origin
            txy = (xy[0]-ox)//tile.size[0],(xy[1]-oy)//tile.size[1]
            newIndex = txy[0]+txy[1]*self.gridSize[0]
            newGrid[newIndex] = tile
        self.grid = newGrid

    def update(self, screen,cam=[0,0]):
        super().update()
        for tile in self.grid:
            tile.update(screen,cam)

    def updateBoundRect(self):
        w, h = self.tileSize
        self.boundRect = pygame.Rect(
            self.origin, (w*self.gridSize[0], self.gridSize[1]*h))

    def getBoundRect(self):
        return self.boundRect

    def getTilePos(self, point: list = [0, 0]):
        x, y = point
        x1, y1 = self.origin
        w, h = self.tileSize

        tx, ty = (int(x)-x1)//w, (int(y)-y1)//h

        return tx, ty

    def getTileIndex(self, pos):
        x, y = pos
        return y*self.gridSize[0]+x

    def getTile(self, pos):
        i = self.getTileIndex(pos)
        return self.grid[i]

    def getTileType(self, pos):
        i = self.getTileIndex(pos)
        return self.grid[i].type

    def worldCoord(self, pos):
        '''returns the topleft position in screen space'''
        x, y = pos
        x = x*self.tileSize[0]+self.origin[0]
        y = y*self.tileSize[1]+self.origin[1]
        return [x, y]

    def normalizedWorldCoord(self, pos):
        ''' return the tile World position in screen space'''
        xy = self.getTilePos(pos)
        xy = self.worldCoord(xy)

        return xy

    def getCamTilePos(self, pos):
        npos = pos[0]-g.camera[0], pos[1]-g.camera[1]
        return npos

    def getCamTileRect(self, pos):
        npos = pos[0]-g.camera[0], pos[1]-g.camera[1]
        print(npos)
        return npos, self.tileSize

#support for:
#simple sprite
#subsurf
#pygame draw

class RenderObject(core.ComponentBase):
    def __init__(self,pos,size,sampleTex:pygame.Surface|str,subSurfRect:pygame.Rect = None,frames=1,framespeed=10,layer=0):
        self.pos = pos
        self.sampleTex = sampleTex.convert_alpha() if(isinstance(sampleTex,pygame.Surface)) else pygame.image.load(sampleTex).convert_alpha()
        self.size = size if(size != None) else self.sampleTex.get_size()
        self.subSurfRect = subSurfRect
        self.frames = frames
        self.framespeed = framespeed
        self.tick = 0
        self.currentImage = 0
        self.images = []
        self.layer = layer
        self.alpha = 255
        self.blendMode = None

        if (self.sampleTex != None):
            if (self.subSurfRect != None):
                # get all images in the spriteSheet and resize them 
                for j in range(self.frames):
                    nrect = pygame.Rect((j*self.subSurfRect.w+self.subSurfRect.x,self.subSurfRect.y),(self.subSurfRect.size))
                    i = self.sampleTex.subsurface(nrect)
                    i = pygame.transform.scale(i,self.size)
                    self.images.append(i)
            else:
                    # without subSurfRect simply scale the sample Texture to the size
                    i = pygame.transform.scale(self.sampleTex,self.size)
                    self.images.append(i)
    
    def update(self,screen:pygame.Surface,cam=[0,0]):
        self.tick += 1
        if self.tick > self.framespeed:
            self.tick = 0
            self.currentImage = (self.currentImage+1)%self.frames
        
        x,y = self.pos
        cx,cy = cam

        screen.blit(self.images[self.currentImage],(cx+x,cy+y))
    
    def getRect(self):
        nrect = pygame.Rect(self.pos,self.size)
        return nrect
    
    def toJson(self):
        pass


