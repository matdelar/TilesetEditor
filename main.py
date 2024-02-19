import src.core as cr
import src.builtin as bi
import src.manager as mg
import src.globals as g
import pygame

import json


class TileSelect(cr.SceneBase):
    def __init__(self):
        super().__init__()
        self.content = {
            'tileset' : bi.Tileset(gridSize=[20,20]),
            'spriteSheet': bi.RenderObject((0,0),None,'assets/image/terrain.png'),
            'hSliderSprite': bi.Slider((16, 392), False, 608, handleSize=(32, 16)),
            'vSliderSprite': bi.Slider((632, 16), True, 352, handleSize=(16, 32)),

            'hSliderTileset': bi.Slider((656, 712), False, 608, handleSize=(32, 16)),
            'vSliderTileset': bi.Slider((1272, 16), True, 672, handleSize=(16, 32)),
            
            'txtGridWidth': bi.Text((0,400),"grid width:",32,(230,230,230)),
            'btngwm': bi.Button((60,60,60),(20,20),(128,400),"-",32,(230,230,230)), # button grid width minus
            'gridWidth': bi.Text((160,400),"10",32,(230,230,230)),
            'btngwp': bi.Button((60,60,60),(20,20),(192,400),"+",32,(230,230,230)), # button grid width plus

            'txtGridHeight': bi.Text((0,432),"grid height:",32,(230,230,230)),
            'btnghm': bi.Button((60,60,60),(20,20),(128,432),"-",32,(230,230,230)), # button grid height minus
            'gridHeight': bi.Text((160,432),"15",32,(230,230,230)),
            'btnghp': bi.Button((60,60,60),(20,20),(192,432),"+",32,(230,230,230)) # button grid height plus
        }
        self.size = [32, 32]
        self.isHolding = False

        self.content['spriteSheet'].autoUpdate = False
        self.content['tileset'].autoUpdate = False
        self.spriteSheetSurf = pygame.Surface((624, 384))
        self.mapSurf = pygame.Surface((624, 704))
        self.spriteCamera = [0, 0]
        self.mapCamera = [0, 0]
        self.tileBoundRect = pygame.Rect(0, 0, 624, 384)
        self.mouseBlock = False

    def update(self, screen):
        if pygame.key.get_pressed()[pygame.K_w]:
            self.saveJson()
        elif pygame.key.get_pressed()[pygame.K_s]:
            self.loadJson()



        super().update(screen)
        

        self.mapSurf.fill((10,10,30))
        

        # easy acess variables
        hSpriteSlider = self.content['hSliderSprite'].getValue()
        vSpriteSlider = self.content['vSliderSprite'].getValue()

        hTilesetSlider = self.content['hSliderTileset'].getValue()
        vTilesetSlider = self.content['vSliderTileset'].getValue()

        spriteSheetWidth = self.content['spriteSheet'].size[0]
        spriteSheetHeight = self.content['spriteSheet'].size[1]

        spriteDeltaX = spriteSheetWidth-self.spriteSheetSurf.get_width()
        spriteDeltaY = spriteSheetHeight-self.spriteSheetSurf.get_height()

        # apply camera on spriteSheet
        if spriteDeltaX > 0:
            self.spriteCamera[0] = hSpriteSlider*spriteDeltaX
        if spriteDeltaY > 0:
            self.spriteCamera[1] = vSpriteSlider*spriteDeltaY

        # invert camera and apply on the spriteSheet
        spritePos = -self.spriteCamera[0], -self.spriteCamera[1]

        self.content['spriteSheet'].update(
            self.spriteSheetSurf)  # draw on secondary surf
        # draw secondary surface on actual display
        screen.blit(self.spriteSheetSurf, spritePos)

        # Screen Division lines
        pygame.draw.line(screen, (20, 20, 20), (640, 0), (640, 720), 1)
        pygame.draw.line(screen, (20, 20, 20), (0, 400), (640, 400), 1)
        pygame.draw.rect(screen, (255, 255, 0), self.tileBoundRect, 1)

        mpos = pygame.mouse.get_pos()
        ssRect = self.content['spriteSheet'].getRect().copy()

        


        if ssRect.collidepoint(mpos) and self.tileBoundRect.collidepoint(mpos):
            # tile on tilesheet on mouse pos
            tile = ((mpos[0]-spritePos[0])//self.size[0]) * \
                self.size[0], ((mpos[1]-spritePos[1]) //
                               self.size[1])*self.size[1]

            tile = pygame.Rect(tile,self.size)

            # vizualize selectedTile
            selectTile = pygame.Rect(
                tile[0]-self.spriteCamera[0], tile[1]-self.spriteCamera[1], self.size[0], self.size[1])

            pygame.draw.rect(screen, (255, 0, 0), selectTile,
                             2)  # highlight selected tile

            self.mouseUpdate(tile)
        
        self.updateGroupTile(screen)
        self.updateGrid()

        #tileset 
        boundRect = self.content['tileset'].getBoundRect()

        mapDeltaX = boundRect.width-self.mapSurf.get_width()
        mapDeltaY = boundRect.height-self.mapSurf.get_height()


        if mapDeltaX > 0:
            self.mapCamera[0] = hTilesetSlider*mapDeltaX
        if mapDeltaY > 0:
            self.mapCamera[1] = vTilesetSlider*mapDeltaY


        mapPos = -self.mapCamera[0],-self.mapCamera[1]



        self.content['tileset'].update(self.mapSurf,mapPos)
        screen.blit(self.mapSurf,(640,0))

        boundRect.x += 640

        mouseMapBound = mpos[0]-boundRect.x+self.mapCamera[0],mpos[1]-boundRect.y+self.mapCamera[1]

        #get the surf rect add the position
        b = self.mapSurf.get_rect() 
        b.x += 640

        
        

        if boundRect.collidepoint(mpos) and g.selected != None and b.collidepoint(mpos):
            xy = self.content['tileset'].getTilePos(mouseMapBound) # get tile coord
            index = self.content['tileset'].getTileIndex(xy) # get tile index to use in the tile array
            tile = self.content['tileset'].getTile(xy) # get tile rect

            tileHighlight = (tile.rect.x+640+self.mapCamera[0],tile.rect.y+self.mapCamera[1]),tile.size

            pygame.draw.rect(screen,(0,255,255),tileHighlight,3) ## draw highlight
            
            self.placeTile(tile,xy,index)
        
        

    def placeTile(self,tile,xy,index):
        if pygame.mouse.get_pressed()[0]:
                #self.isHolding = True
                w,h = self.content['tileset'].gridSize
                tw,th = self.size


                for q,i in enumerate(range(xy[0],xy[0]+g.group_columns)):
                    if 0 <= i < w:
                        for a,j in enumerate(range(xy[1],xy[1]+g.group_rows)):
                            if 0 <= j < h:

                                subSurfaceRect = g.topleft_tile.topleft
                                subSurfaceRect = [subSurfaceRect[0],subSurfaceRect[1]]
                                subSurfaceRect[0] += q*tw
                                subSurfaceRect[1] += a*th

                                tilePos = tile.rect.topleft
                                tilePos = [tilePos[0],tilePos[1]]
                                tilePos[0] += q*tw
                                tilePos[1] += a*th

                                t = self.content['tileset'].grid[j*w+i]
                                tex2d = self.content['spriteSheet'].sampleTex
                                t.anim = bi.RenderObject(tilePos,t.size,tex2d,pygame.Rect(subSurfaceRect,t.size))
        elif pygame.mouse.get_pressed()[2]:
            self.content['tileset'].grid[index].anim = None
    
        pygame.event.clear(pygame.MOUSEBUTTONDOWN|pygame.MOUSEBUTTONUP)

    def updateGroupTile(self,screen):
         # Group Select

        if g.first_tile != None and g.last_tile != None:
            # get all positions
            # first left,first top ...
            fl, ft = g.first_tile.topleft
            fr, fb = g.first_tile.bottomright

            # last left,last top ...
            ll, lt = g.last_tile.topleft
            lr, lb = g.last_tile.bottomright

            # pos and size of selected group
            x = min(fl, ll)
            y = min(ft, lt)
            w = max((lr-fl), (fr-ll))
            h = max((lb-ft), (fb-lt))

            g.topleft_tile = pygame.Rect((x,y),self.size)

            g.group_columns = int(w / self.size[0])
            g.group_rows = int(h / self.size[1])

            group_rect = x-self.spriteCamera[0], y-self.spriteCamera[1], w, h

            # draw/reset group
            if self.content['vSliderSprite'].hasChangedValue():
                pygame.draw.rect(screen, (255, 255, 255), group_rect, 2)
            else:
                g.first_tile = None
                g.last_tile = None

    def mouseUpdate(self, selectTile):
        
        for b in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if b.button == 1:
                g.first_tile = selectTile
                g.selected = selectTile
                self.isHolding = True
        if self.isHolding:
            g.last_tile = selectTile
            g.selected = selectTile
        

        for b in pygame.event.get(pygame.MOUSEBUTTONUP):
            if b.button == 1 and self.isHolding:
                g.last_tile = selectTile
                g.selected = selectTile
                self.isHolding = False

    def updateGrid(self):
        newHeigh = self.content['btnghp'].get_click()-self.content['btnghm'].get_click()

        if newHeigh > 0:
            for t in range(self.content['tileset'].gridSize[0]):
                tile_rect = pygame.Rect((t*self.size[0]+self.content['tileset'].origin[0],(self.content['tileset'].gridSize[1])*self.size[1]+self.content['tileset'].origin[1]),self.size)
                tile = bi.Tile(tile_rect.topleft,tile_rect.size)
                self.content['tileset'].grid.append(tile)
            self.content['tileset'].gridSize[1] += 1
        elif newHeigh < 0:
            self.content['tileset'].gridSize[1] -= 1
            for t in range(self.content['tileset'].gridSize[0]):
                self.content['tileset'].grid.pop()
            
        newWidth = self.content['btngwp'].get_click()-self.content['btngwm'].get_click()

        if newWidth > 0:
            for t in range(self.content['tileset'].gridSize[1]):
                tile_rect = pygame.Rect((self.content['tileset'].gridSize[0]*self.size[0]+self.content['tileset'].origin[0],(t*self.size[1]+self.content['tileset'].origin[1])),self.size)
                tile = bi.Tile(tile_rect.topleft,tile_rect.size)
                self.content['tileset'].grid.append(tile)
            self.content['tileset'].gridSize[0] += 1
            self.content['tileset'].resetIndex()
        elif newWidth < 0:
            self.content['tileset'].gridSize[0] -= 1
            for t in range(self.content['tileset'].gridSize[1]):
                pass

        
        self.content['tileset'].updateBoundRect()

        self.content['gridWidth'].setText(self.content['tileset'].gridSize[0]) 
        self.content['gridHeight'].setText(self.content['tileset'].gridSize[1])
    
    def loadJson(self):
        with open('level.txt','r') as f:
            data = json.load(f)

        for i,tile in enumerate(self.content['tileset'].grid):
            try:
                tile = (data[i+1]['subSurface'])
                img = None
                if tile != None:
                    x,y,w,h = tile[0],tile[1],tile[2],tile[3]
                    tile = pygame.Rect(x,y,w,h)
                    img = self.content['spriteSheet'].sampleTex
                self.content['tileset'].grid[i].updateAnim(img,tile)
            except KeyError:
                print(i+1,data[i+1],data[i+1]['subSurface'])
            

    def saveJson(self):

        data = []

        header = {
            'gridWidth' : self.content['tileset'].gridSize[0],
            'gridHeight' : self.content['tileset'].gridSize[1],
            'tileWidth' : self.content['tileset'].tileSize[0],
            'tileHeight' : self.content['tileset'].tileSize[1],
        }

        data.append(header)
        for tile in self.content['tileset'].grid:
            t = {
                'subSurface' : tile.toJson()
            }
            data.append(t)

        with open('level.txt','w') as ts:
            json.dump(data,ts)

if __name__ == '__main__':
    manager = mg.Manager()
    manager.scenes = {
        'tileSelect': TileSelect()
    }
    manager.setProperties(
        fps=60,
        startScene='tileSelect',
        backgroundColor=(10,10,10)
    )
    manager.start()
