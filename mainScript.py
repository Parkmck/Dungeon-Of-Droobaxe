import pygame, sys, math, time, os, random, pickle, datetime, webbrowser, copy, math
#import sys, pygame, copy
from pygame.locals import *
pygame.mixer.pre_init(44100, 16, 9999, 4096)
pygame.init()

pygame.display.set_caption("Dungeon of Droobaxe")


size = width, height = 684, 684
speed = [2, 2]
black = 0, 0, 0
displayPlayfeild = True
gamePaused = False

screen = pygame.display.set_mode(size)

#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#sounds
sounds = ["sounds\dig_2.wav", "sounds\dig_0.wav", "sounds\Item_10.wav", "sounds\dig_1.wav", "sounds\Jump_0.wav", "sounds\hurt.wav"]
#___MUSIC___
musicPosition = 0
musicList = [r"sounds\background.mp3", r"sounds\Ruins_Background.mp3"]
currMusicPlaying = r"sounds\background.mp3"
pygame.mixer.music.load(r"sounds\background.mp3")
pygame.mixer.music.play(-1)

def changeMusic(newSong):
    global musicPosition, currMusicPlaying
    if newSong == musicList[1]:
        musicPosition = pygame.mixer.music.get_pos()
    pygame.mixer.music.fadeout(10)
    pygame.mixer.music.load(newSong)
    if not newSong == musicList[1]:
        #pygame.mixer.music.set_pos(musicPosition)
        pygame.mixer.music.play(-1, musicPosition)
    else:
        pygame.mixer.music.play(-1)
    currMusicPlaying = newSong

changeMusic(musicList[0]) 

pygame.mixer.music.set_volume(0.1)
    
#___SOUNDS___
def loadSounds():
    global sounds
    theI = 0
    for i in sounds:
        sounds[theI] = pygame.mixer.Sound(i)
        theI +=1
loadSounds()

def playSound(s):
    theSound = s
    theSound.play()

#print(sounds[2])
#___IMAGES___
def cropImage(im, transparency=0):
    img = pygame.image.load(im)
    #surf = pygame.Surface((int(17),int(16)))
    surf = pygame.Surface(img.get_rect().size)
    surf.fill((255,0,255))
    surf.set_colorkey((255,0,255))
    surf.blit(img,(0,0))
    if not transparency == 0:
        surf.set_alpha(transparency)
    return surf

#___SET_ICON___
gameIcon = cropImage(r"images\gameIcon.png")
pygame.display.set_icon(gameIcon)

#___colBox___
class colBox(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

    def updatePosition(self):
        self.rect.x = pygame.mouse.get_pos()[0]
        self.rect.y = pygame.mouse.get_pos()[1]


mouseColBox = colBox(cropImage(r"images\mouseColBox.png"), 0, 0)

#___PAUSESCREEN___
borderTilesGroup = pygame.sprite.Group()
menuButtonsGroup = pygame.sprite.Group()

class pauseScreenPart(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.x = rx
        self.y = ry
        self.partType = "tile"
        
        #Buttons
        self.buttonType = "none"
        self.defaultImage = im

    def resizePart(self, w, h):
        self.image = pygame.transform.scale(self.image, (w, h))
        
    def centerPart(self):
        theX = (width / 2) - (self.image.get_width() / 2)
        self.rect.x = theX

    def makeButton(self, buttonType):
        self.partType = "button"
        self.buttonType = buttonType

    def enlargeButton(self):
        self.rect.x = self.x - (((self.defaultImage.get_width() * 1.3) / 2) - (self.defaultImage.get_width() / 2))
        self.rect.y = self.y - (((self.defaultImage.get_height() * 1.3) / 2) - (self.defaultImage.get_height() / 2))
        self.image = pygame.transform.scale(self.defaultImage, (int(self.defaultImage.get_width() * 1.3), int(self.defaultImage.get_height() * 1.3)))

    def shrinkButton(self):
        self.image = self.defaultImage
        self.rect.x = self.x
        self.rect.y = self.y

    def useButton(self):
        global gamePaused 
        #print(self.buttonType)#DEBUG
        if self.buttonType == "unpause":
            #print("UNPAUSED")#DEBUG
            gamePaused = False
            
        
def newMenuBorder(im, rx, ry):
    theMenuBorder = pauseScreenPart(im, rx, ry)
    borderTilesGroup.add(theMenuBorder)

def newMenuButton(im, rx, ry, t):
    theMenuButton = pauseScreenPart(im, rx, ry)
    theMenuButton.makeButton(t)
    menuButtonsGroup.add(theMenuButton)

menuShade = pauseScreenPart(cropImage(r"images\pauseScreen\blackBlank.png", 200), 0, 0)
menuShade.resizePart(width, height)

titleShade = pauseScreenPart(cropImage(r"images\pauseScreen\blackBlank.png", 175), 0, 0)
titleShade.resizePart(width, 78)

menuGameTile = pauseScreenPart(cropImage(r"images\pauseScreen\title.png"), 0, 39 - 19.5)
menuGameTile.centerPart()

newMenuButton(cropImage(r"images\pauseScreen\button_x.png"), ((width // 36) * 36) - (36 + 18), 18, "unpause")

for i in range(0, height // 36):
    newMenuBorder(cropImage(r"images\pauseScreen\borderTileLeft.png"), 0, i * 36)

for i in range(0, height // 36):
    newMenuBorder(cropImage(r"images\pauseScreen\borderTileRight.png"), ((width // 36) * 36) - 73, i * 36)

#___DoorOverlays___
doorOverlayGroup = pygame.sprite.Group()
class doorOverlay(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        
def newDoorOverlay(im, rx, ry):
    theDoorOverlay = doorOverlay(im, rx, ry)
    doorOverlayGroup.add(theDoorOverlay)

#___PLAYER___
class player(pygame.sprite.Sprite):
    def __init__(self, im, s, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = cropImage(im)#im
        self.rect = self.image.get_rect()
        self.speed = s
        self.rect.x = rx
        self.rect.y = ry
        self.defDamageCooldown = 150
        self.damageCooldown = 0
    def canMove(self):
        if self.rect.left < 0 or self.rect.right > width:
            return False
        elif self.rect.top < 0 or self.rect.bottom > height:
            return False
        else:
            return True
        
    def moveNpc(self, event):
        global size
        if not self.speed == [0, 0]:
            self.rect = self.rect.move(self.speed)
            
        #Wall col
        for currGroup in [wallsGroup, doorOverlayGroup]:
            blocks_hit_list = pygame.sprite.spritecollide(self, currGroup, False)
            for i in blocks_hit_list:
                self.rect = self.rect.move([-self.speed[0] * 2, self.speed[1]])
                self.rect = self.rect.move([self.speed[0], -self.speed[1] * 2])
                self.speed = [0, 0]
        
        #Border Col L-R
        if self.rect.left < 0 or self.rect.right > width:
            self.speed[0] = 0#-self.speed[0]
            if self.rect.left < 0:
                self.rect = self.rect.move([1, self.speed[1]])
            elif self.rect.right > width:
                self.rect = self.rect.move([-1, self.speed[1]])

        #Border Col U-D
        if self.rect.top < 0 or self.rect.bottom > height:
            self.speed[1] = 0#-self.speed[1]
            if self.rect.top < 0:
                self.rect = self.rect.move([self.speed[0], 1])
            elif self.rect.bottom > height:
                self.rect = self.rect.move([self.speed[0], -1])

#Health
try:
    if healthBar > 0:
        healthBar = healthBar
except NameError:
    healthBar = []
class heart:
    def __init__(self):
        self.image = cropImage(r"images\health\heartFull.png")#pygame.image.load("door.png")
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.full = True

    def thumpHeart(self):
        lastImage = self.image
        self.image = cropImage(r"images\health\heartThump.png")
        #pygame.time.wait(1000)
        self.image = lastImage

def newHeart():
    theHeart = heart()
    healthBar.append(theHeart)

def refreshHealthBar():
    theIndex = 0
    for i in healthBar:
        if i.full == True:
            #print("Full")#DEBUG
            i.image = cropImage(r"images\health\heartFull.png", 200)
        else:
            #print("Empty")#DEBUG
            i.image = cropImage(r"images\health\heartEmpty.png", 200)
        
        i.rect.x = ((width - 5) - 18) - (18 * theIndex)
        i.rect.y = 5
        theIndex += 1

def findLivesLeft():
    livesLeft = 0
    for i in healthBar:
        if i.full == True:
            livesLeft += 1
    return livesLeft

def damagePlayer(d):
    damageLeft = d
    while damageLeft > 0:
        theIndex = 0
        if findLivesLeft() - 1 >= 0:
            for i in healthBar:
                if i.full == True:
                    i.thumpHeart()
                    healthBar[theIndex].full = False
                    damageLeft -= 1
                    break
                theIndex += 1
        else:
            break
    playSound(sounds[5])
    refreshHealthBar()


#Starter Hearts
if len(healthBar) <= 0:
    newHeart()
    newHeart()
    newHeart()
    newHeart()
    #sff
    newHeart()
    newHeart()
    newHeart()
    newHeart()
refreshHealthBar()
blueMan = player(r"images\player\player.png", [0, 0], 36, 36)

#___PROJECTILES___
projectilesGroup = pygame.sprite.Group()

class projectile(pygame.sprite.Sprite):
    def __init__(self, im, s, rx, ry, si, chp):
        pygame.sprite.Sprite.__init__(self)
        self.speed = s
        #im = pygame.image.load(im)
        self.image = pygame.transform.scale(im, (int(im.get_width() * si), int(im.get_height() * si)))#pygame.image.load(im)
        #surf = pygame.Surface(img.get_rect().size)
        #surf.fill((255,0,255))
        #surf.set_colorkey((255,0,255))
        #surf.blit(img,(0,0))
        #surf.set_alpha(200)
        #self.image = surf
        
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.ProID = random.randint(-9999999999, 9999999999)
        self.canHurtPlayer = chp
    def moveProjectile(self):
        self.rect = self.rect.move(self.speed)
        for currList in [wallsGroup, doorsGroup]:
            blocks_hit_list = pygame.sprite.spritecollide(self, currList, False)
            for i in blocks_hit_list:
                #self.speed = [-self.speed[0], -self.speed[1]]
                sounds[4]
                self.kill()

        #for currList in [enemysGroup]:
            #blocks_hit_list = pygame.sprite.spritecollide(self, currList, False)
            #for i in blocks_hit_list:
                #self.speed = [-self.speed[0], -self.speed[1]]
                #if self.canHurtPlayer == False:
                    #sounds[4]
                    #self.kill()

def newProjectile(im, s, rx, ry, si, chp):
    theProjectile = projectile(im, s, rx, ry, si, chp)
    projectilesGroup.add(theProjectile)
    
def launchProjectile(launchSource, targetDirection, projectileImage, size, projectileSpeedMult, spread, canHurtPlayer):
    projectileSlope = [(targetDirection[0] + random.randint(-spread, spread)) - launchSource[0], (targetDirection[1] + random.randint(-spread, spread)) - launchSource[1]]
    #print(projectileSlope)#DEBUG
    projectileRun, projectileRise = projectileSlope
    divider = 1
    while True:
        if (abs(projectileRise) / divider <= 4 and abs(projectileRun) / divider <= 4):
            projectileSpeed = [projectileRun / divider, projectileRise / divider] * projectileSpeedMult
            break
        else:
            if divider >= 999:
                print("ERROR INFENENT LOOP DETECTED!")
                projectileSpeed = [0, 0]
                break
            divider += 0.1
    #print(projectileSpeed)#DEBUG
    newProjectile(projectileImage, projectileSpeed, launchSource[0], launchSource[1], size, canHurtPlayer)
    playSound(sounds[2])

#__ENEMYS___
enemysGroup =  pygame.sprite.Group()
bodysGroup = pygame.sprite.Group()

class body(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

def newBody(im, rx, ry):
    theBody = body(im, rx, ry)
    bodysGroup.add(theBody)
        
class enemy(pygame.sprite.Sprite):
    def __init__(self, im, db, s, rx, ry, ad, es, sd):
        pygame.sprite.Sprite.__init__(self)
        self.speed = s
        self.enemySpeed = es
        self.esI = es
        self.frames = im
        self.image = im[0]
        self.deadBody = db
        self.onFrame = 0
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.x = rx
        self.y = ry
        self.anamationDelay = ad
        self.adI = ad
        self.direction = "LEFT"
        self.shootingData = sd #[canShoot, image, speed, size, fireRate, spread, gunBarrelPos]
        if not self.shootingData[0] == False:
            self.shootingDelay = self.shootingData[4]
            self.sdI = self.shootingData[4]
        else:
            self.shootingDelay = 0
            self.sdI = 0

    def nextFrame(self):
        if self.adI <= 0:
            if self.onFrame + 1 >= len(self.frames):
                self.onFrame = 0
            else:
                self.onFrame += 1
            self.image = self.frames[self.onFrame]
            self.rect = self.image.get_rect()
            self.adI = self.anamationDelay
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.adI -= 1

    def chaseQuar(self, targetDirection):
        projectileSlope = [targetDirection[0] - self.rect.x, targetDirection[1] - self.rect.y]
        #print(projectileSlope)#DEBUG
        projectileRun, projectileRise = projectileSlope
        divider = 1
        while True:
            if (abs(projectileRise) / divider <= 3 and abs(projectileRun) / divider <= 3):
                self.speed = [projectileRun / divider, projectileRise / divider]# * projectileSpeedMult
                break
            else:
                if divider >= 999:
                    print("ERROR INFENENT LOOP DETECTED!")
                    #self.speed = [0, 0]
                    self.speed = [projectileRun / divider, projectileRise / divider]
                    break
                divider += 0.1

    def moveEnemy(self):
        blocks_hit_list = pygame.sprite.spritecollide(self, projectilesGroup, False)
        for i in blocks_hit_list:
            if i.canHurtPlayer == False:
                sounds[4]
                if self.direction == "RIGHT":
                    self.deadBody = pygame.transform.flip(self.deadBody, True, False)
                newBody(self.deadBody, self.x, self.y)
                self.kill()
                i.kill()
        if self.esI <= 0:            
            if True == True:
                def flipFrames(a):
                    INnum = 0
                    for i in a.frames:
                        a.frames[INnum] = pygame.transform.flip(i, True, False)
                        INnum += 1
                self.chaseQuar([blueMan.rect.x, blueMan.rect.y])
                if blueMan.rect.x <= self.x and not self.direction == "LEFT":
                    self.image = pygame.transform.flip(self.image, True, False)
                    flipFrames(self)
                    self.direction = "LEFT"
                elif blueMan.rect.x > self.x and not self.direction == "RIGHT":
                    self.image = pygame.transform.flip(self.image, True, False)
                    flipFrames(self)
                    self.direction = "RIGHT"
            self.rect = self.rect.move(self.speed)
            self.x = self.rect.x
            self.y = self.rect.y
            self.esI = self.enemySpeed
        else:
            self.esI -= 1

    def shoot(self):
        if not self.shootingData[0] == False:
            if self.sdI <= 0:
                launchProjectile([self.rect.x + self.shootingData[6][0], self.rect.y + self.shootingData[6][1]], [blueMan.rect.x + 16, blueMan.rect.y + 16], cropImage(self.shootingData[1]), self.shootingData[3], self.shootingData[2], self.shootingData[5], True)
                self.sdI = self.shootingData[4]
            else:
                self.sdI -= 1
    def damage(self):
        
        self.kill()
def newEnemy(im, db, s, rx, ry, ad, es, sd=[False]):
    theEnemy = enemy(im, db, s, rx, ry, ad, es, sd)
    enemysGroup.add(theEnemy)
    
def randomSpawnPoint(w):
    return random.randint(36, w -36)

def spawnEnemy(name, x="RAND", y="RAND"):
    if x == "RAND":
        x = randomSpawnPoint(width)
    if y == "RAND":
        y = randomSpawnPoint(height)
        
    if name == "RuinBeatle":
        newEnemy([cropImage(r"images\enemies\RuinBeatle\frame_0.png", 0), cropImage(r"images\enemies\RuinBeatle\frame_1.png", 0), cropImage(r"images\enemies\RuinBeatle\frame_0.png", 0), cropImage(r"images\enemies\RuinBeatle\frame_2.png", 0)], cropImage(r"images\enemies\RuinBeatle\dead_0.png"), [0,0], x, y, 15, 3)
    elif name == "Fly":
        newEnemy([cropImage(r"images\enemies\Fly\frame_0.png", 0), cropImage(r"images\enemies\Fly\frame_1.png", 0), cropImage(r"images\enemies\Fly\frame_2.png", 0), cropImage(r"images\enemies\Fly\frame_1.png", 0)], cropImage(r"images\enemies\Fly\dead_0.png"), [0,0], x, y, 2, 7,
        [True, r"images\projectiles\smallFlyAcid.png", 1, 0.5, 250, 30, [16, 15]])

#___PROPS___
propsGroup = pygame.sprite.Group()
class prop(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

def newProp(im, rx, ry):
    theProp = prop(im, rx, ry)
    propsGroup.add(theProp)

#newProp(cropImage(r"images\props\pots\clayPot.png"), 120, 120)
        
#___ROOMS___
def randomWallTiles(tileList):
    theTiles = []
    for tile in tileList:
        for i in range(tile[1] + 1):
            theTiles.append(tile[0])
    random.shuffle(theTiles)
    #print(theTiles)#DEBUG
    return theTiles

class door(pygame.sprite.Sprite):
    def __init__(self, rx, ry, did, tgr, tgd, dm, dt="NORM"):
        pygame.sprite.Sprite.__init__(self)
        self.doorType = dt
        if self.doorType == "NORM":
            self.image = pygame.image.load(r"images\doors\door.png")
            self.defDoor = pygame.image.load(r"images\doors\door.png")
        elif self.doorType == "DEMON":
            self.image = pygame.image.load(r"images\doors\demonDoor.png")
            self.defDoor = pygame.image.load(r"images\doors\demonDoor.png")
        self.rect = self.image.get_rect()
        self.rect.x = rx - 1
        self.rect.y = ry - 1
        self.doorId = did
        self.targetRoom = tgr
        self.targetDoor = tgd
        self.doorMat = dm

    def useDoor(self):
        global numOfRooms, currentRoom, displayPlayfeild, currentRoomPos
        exitLoop = False
        while exitLoop == False:
            if not self.targetRoom == "NONE":
                pygame.draw.rect(screen, [0, 0, 0], [0, 0, width, height])
                pygame.display.flip()
                displayPlayfeild = False
                pygame.time.wait(1000)
                displayPlayfeild = True
                blueMan.speed = [0, 0]
                
                #SetRoomPos
                if self.doorMat == "UP":
                    currentRoomPos[1] += 1
                elif self.doorMat == "DOWN":
                    currentRoomPos[1] -= 1
                elif self.doorMat == "LEFT":
                    currentRoomPos[0] -= 1
                elif self.doorMat == "RIGHT":
                    currentRoomPos[0] += 1

                loadRoom(self.targetRoom)
                currentRoom = self.targetRoom
                if self.doorType == "DEMON":
                    damagePlayer(1)
                for i in rooms[self.targetRoom][1]:
                    #print("i.doorId:", i.doorId, "| self.targetDoor:", self.targetDoor)#DEBUG
                    if i.doorId == self.targetDoor:
                        #print("DOOR ID:", i.doorMat)#DEBUG
                        if i.doorMat == "UP":
                            blueMan.rect.y = i.rect.y + 38
                            exitLoop = True
                            playSound(sounds[0])
                            break
                        elif i.doorMat == "DOWN":
                            blueMan.rect.y = i.rect.y - 38
                            exitLoop = True
                            playSound(sounds[0])
                            break
                        elif i.doorMat == "LEFT":
                            blueMan.rect.x = i.rect.x + 38
                            exitLoop = True
                            playSound(sounds[0])
                            break
                        elif i.doorMat == "RIGHT":
                            blueMan.rect.x = i.rect.x - 38
                            exitLoop = True
                            playSound(sounds[0])
                            break
                    #else:#DEBUG
                        #print("i.doorId:", i.doorId, "| self.targetDoor:", self.targetDoor)#DEBUG
            else:
                self.targetRoom = str(numOfRooms + 1)
                numOfRooms += 1
                IDsToUse = ["c", "d", "b", "a"]
                doorSpotsToUse = ["TOP", "BOTTOM", "LEFT", "RIGHT"]
                
                encaseRoom(self.targetRoom, randomWallTiles([[r"images\walls\ruin\wallRuinPlain.png", 3], [r"images\walls\ruin\wallRuinDamaged.png", 1], [r"images\walls\ruin\wallRuinOvergrown.png", 1]]))
                if self.rect.y + 1 == ((height // 36) - 1) * 36:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    newDoor(self.rect.x + 1, 0, self.targetRoom, currentRoom, theId, self.doorId, "UP")
                    print("New top door made! DoorID:", theId)
                    doorSpotsToUse.remove("TOP")
                    IDsToUse.remove(theId)
                    self.targetDoor = theId
                    theId = None
                elif self.rect.y + 1 == 0:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    newDoor(self.rect.x + 1, ((height // 36) * 36) - 36, self.targetRoom, currentRoom, theId, self.doorId, "DOWN")
                    print("New bottom door made! DoorID:", theId)
                    doorSpotsToUse.remove("BOTTOM")
                    IDsToUse.remove(theId)
                    self.targetDoor = theId
                    theId = None
                elif self.rect.x + 1 == 0:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    newDoor(((width // 36) * 36) - 36, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "RIGHT")
                    print("New right door made! DoorID:", theId)
                    doorSpotsToUse.remove("RIGHT")
                    self.targetDoor = theId
                    IDsToUse.remove(theId)
                    theId = None
                elif self.rect.x + 1 == ((width // 36) * 36) - 36:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    newDoor(0, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "LEFT")
                    print("New left door made! DoorID:", theId)
                    doorSpotsToUse.remove("LEFT")
                    self.targetDoor = theId
                    IDsToUse.remove(theId)
                    theId = None

                def getOffset(d):
                    if d == "UP":
                        return [0, 1]
                    if d == "DOWN":
                        return [0, -1]
                    if d == "LEFT":
                        return [-1, 0]
                    if d == "RIGHT":
                        return [1, 0]
                def canDoorBePlaced(d):
                    def doorInWay(p):
                        #print(p)#DEBUG
                        #print(roomPositions)#DEBUG
                        if p in roomPositions:
                            return True
                        
                    for key, i in rooms.items():
                        #print("roomID:", i, "| roomsList:", rooms)#DEBUG
                        if d == "TOP":
                            if doorInWay([currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] + 1) + getOffset(self.doorMat)[1]]) == True:
                                #print("GHOST ROOM BLOCK UP")#DEBUG
                                return False
                        elif d == "BOTTOM":
                            if doorInWay([currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] - 1) + getOffset(self.doorMat)[1]]) == True:
                                #print("GHOST ROOM BLOCK DOWN")#DEBUG
                                return False
                        elif d == "LEFT":
                            if doorInWay([(currentRoomPos[0] - 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]]) == True:
                                #print("GHOST ROOM BLOCK LEFT")#DEBUG
                                return False
                        elif d == "RIGHT":
                            if doorInWay([(currentRoomPos[0] + 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]]) == True:
                                #print("GHOST ROOM BLOCK RIGHT")#DEBUG
                                return False
                        
    
                while not len(doorSpotsToUse) <= 0:
                    for IDa in IDsToUse:
                        #print("BEFORE:", IDa, IDsToUse)#DEBUG
                        for IDb in doorSpotsToUse:
                            #print(IDb, doorSpotsToUse)#DEBUG
                            if random.randint(0,2) == 1:#random.randint(0,2)
                                doorSpotsToUse.remove(IDb)
                                #print("SPOT REMOVED!:", IDb)#DEBUG
                                break
                            else:
                                if IDb == "TOP":
                                    if not canDoorBePlaced(IDb) == False:
                                        newDoor((((width // 36) * 36) - 36) / 2, 0, self.targetRoom, "NONE", IDa, "a", "UP")
                                        print("New top door made! DoorID:", IDa)
                                        IDsToUse.remove(IDa)
                                        if not [currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] + 1) + getOffset(self.doorMat)[1]] in roomPositions:
                                            roomPositions.append([currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] + 1) + getOffset(self.doorMat)[1]])
                                            #print("New", IDb, "GHOST ROOM CREATED AT", [currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] + 1) + getOffset(self.doorMat)[1]])#DEBUG
                                    #print("REMOVED:", IDa, IDb)#DEBUG
                                    doorSpotsToUse.remove(IDb)
                                    break
                                elif IDb == "BOTTOM":
                                    if not canDoorBePlaced(IDb) == False:
                                        newDoor((((width // 36) * 36) - 36) / 2, ((height // 36) * 36) - 36, self.targetRoom, "NONE", IDa, "a", "DOWN")
                                        print("New bottom door made! DoorID:", IDa)
                                        IDsToUse.remove(IDa)
                                        if not [currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] - 1) + getOffset(self.doorMat)[1]] in roomPositions:
                                            roomPositions.append([currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] - 1) + getOffset(self.doorMat)[1]])
                                            #print("New", IDb, "GHOST ROOM CREATED AT", [currentRoomPos[0] + getOffset(self.doorMat)[0], (currentRoomPos[1] - 1) + getOffset(self.doorMat)[1]])#DEBUG
                                    #print("REMOVED:", IDa, IDb)#DEBUG
                                    doorSpotsToUse.remove(IDb)
                                    break
                                elif IDb == "RIGHT":
                                    if not canDoorBePlaced(IDb) == False:
                                        newDoor(((width // 36) * 36) - 36, (((height // 36) * 36) - 36) / 2, self.targetRoom, "NONE", IDa, "a", "RIGHT")
                                        print("New right door made! DoorID:", IDa)
                                        IDsToUse.remove(IDa)
                                        if not [(currentRoomPos[0] + 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]] in roomPositions:
                                            roomPositions.append([(currentRoomPos[0] + 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]])
                                            #print("New", IDb, "GHOST ROOM CREATED AT", [(currentRoomPos[0] + 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]])#DEBUG
                                    #print("REMOVED:", IDa, IDb)#DEBUG
                                    doorSpotsToUse.remove(IDb)
                                    break
                                elif IDb == "LEFT":
                                    if not canDoorBePlaced(IDb) == False:
                                        newDoor(0, (((height // 36) * 36) - 36) / 2, self.targetRoom, "NONE", IDa, "a", "LEFT")
                                        print("New left door made! DoorID:", theId)
                                        IDsToUse.remove(IDa)
                                        if not [(currentRoomPos[0] - 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]] in roomPositions:
                                            roomPositions.append([(currentRoomPos[0] - 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]])
                                            #print("New", IDb, "GHOST ROOM CREATED AT", [(currentRoomPos[0] - 1) + getOffset(self.doorMat)[0], currentRoomPos[1] + getOffset(self.doorMat)[1]])#DEBUG
                                    #print("REMOVED:", IDa, IDb)#DEBUG
                                    doorSpotsToUse.remove(IDb)
                                    break
                        #print("AFTER:", IDa, IDsToUse)#DEBUG
                            
                #KEEP LAST
                theId = None
                #IDsToUse = ["d", "c", "b", "a"]
                #print(IDsToUse)#DEBUG
                

                
                
                

def checkDoorCol():
    blocks_hit_list = pygame.sprite.spritecollide(blueMan, doorsGroup, False)
    for i in blocks_hit_list:
        if not len(enemysGroup) > 0:
            playSound(sounds[1])
            i.useDoor()
            print("Colided with door!")

rooms = {}
numOfRooms = 1
currentRoomPos = [0,0]
roomPositions = []
try:
    currentRoom = currentRoom
except NameError:
    currentRoom = "1"
wallsGroup = pygame.sprite.Group()
doorsGroup = pygame.sprite.Group()

def loadRoom(theId):
    global wallsGroup, doorsGroup, rooms, currentRoomPos
    wallsGroup = pygame.sprite.Group()
    doorsGroup = pygame.sprite.Group()
    for i in rooms[theId][0]:
        wallsGroup.add(i)
    for i in projectilesGroup:
        i.kill()
    for i in bodysGroup:
        i.kill()
    for i in rooms[theId][1]:
        doorsGroup.add(i)
    theI = 0
    for i in rooms[theId][2]:
        if i == "NONE":
            rooms[theId][2][theI] = currentRoomPos[theI]
        theI += 1
    if not rooms[theId][2] in roomPositions:
        roomPositions.append(rooms[theId][2])
    
    for i in rooms[theId][3]:
        spawnEnemy(i)
    rooms[theId][3] = []
    print('Loaded room "' + str(theId) + '"!')
    #print(rooms[theId][2], currentRoomPos)#DEBUG
    

class wall(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(im)
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

      

def newDoor(x, y, roomId, targetRoom, doorId, targetDoor, doorMat, doorType="NORM"):
    theDoor = door(x, y, doorId, targetRoom, targetDoor, doorMat, doorType)
    while True:
        try:
            rooms[roomId][1].append(theDoor)
            for i in rooms[roomId][0]:
                if i.rect.x == theDoor.rect.x + 1 and i.rect.y == theDoor.rect.y + 1:
                    rooms[roomId][0].remove(i)
            break
        except KeyError:
            rooms[roomId] = [[], [], ["NONE", "NONE"], ["Fly", "RuinBeatle", "RuinBeatle"]]

def newWall(image, x, y, roomId):
    theWall = wall(image, x, y)
    while True:
        try:
            rooms[roomId][0].append(theWall)
            break
        except KeyError:
            rooms[roomId] = [[], [], ["NONE", "NONE"], ["Fly", "RuinBeatle", "RuinBeatle"]]
            
def encaseRoom(roomId, theImages):
    for i in range(0, width // 36):
        newWall(random.choice(theImages), i * 36 , 0, roomId)
    for i in range(1, height // 36):
        newWall(random.choice(theImages), 0 , i * 36, roomId)
    for i in range(0, width // 36):
        newWall(random.choice(theImages), i * 36 , ((height // 36) - 1) * 36, roomId)
    for i in range(1, height // 36):
        newWall(random.choice(theImages), ((width // 36) - 1) * 36, i * 36, roomId)

#Walls Below
encaseRoom("1", randomWallTiles([[r"images\walls\ruin\wallRuinPlain.png", 30], [r"images\walls\ruin\wallRuinDamaged.png", 10], [r"images\walls\ruin\wallRuinOvergrown.png", 10], [r"images\walls\ruin\wallRuinText1.png", 1], [r"images\walls\ruin\wallRuinText2.png", 1]]))
#randomWallTiles([[r"images\walls\purple\wallPurple.png", 90], [r"images\walls\purple\wallPurpleText1.png", 1], [r"images\walls\purple\wallPurpleEye.png", 1], [r"images\walls\purple\wallPurpleText2.png", 1]])
#randomWallTiles([[r"images\walls\ruin\wallRuinPlain.png", 30], [r"images\walls\ruin\wallRuinDamaged.png", 10], [r"images\walls\ruin\wallRuinOvergrown.png", 10], [r"images\walls\ruin\wallRuinText1.png", 1], [r"images\walls\ruin\wallRuinText2.png", 1]])
#randomWallTiles([[r"images\walls\ruin\wallRuinPlain.png", 3], [r"images\walls\ruin\wallRuinDamaged.png", 1], [r"images\walls\ruin\wallRuinOvergrown.png", 1]])

#encaseRoom("2", "wallPurple.png")
#newWall("wall.png", 0, 36, "1")

#Doors Below
newDoor((((width // 36) * 36) - 36) / 2, 0, "1", "NONE", "a", "b", "UP", "DEMON")#DEMON
#newDoor((((width // 36) * 36) - 36) / 2, ((width // 36) * 36) - 36, "1", "NONE", "b", "a", "DOWN", "NORM")
#newDoor(0, (((height // 36) * 36) - 36) / 2, "1", "NONE", "c", "a", "LEFT", "NORM")
#newDoor(((width // 36) * 36) - 36, (((height // 36) * 36) - 36) / 2, "1", "NONE", "d", "a", "RIGHT", "NORM")
#newDoor(108, ((height // 36) * 36) - 36, "2", "1", "b", "a", "DOWN")


if len(wallsGroup) == 0 and len(doorsGroup) == 0:
    loadRoom(currentRoom)

RUNNING = True
while RUNNING == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
            pygame.display.quit()
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if not findLivesLeft() <= 0:
                    if gamePaused == False:
                        gamePaused = True
                        #pygame.time.wait(100)
                    elif gamePaused == True:
                        #pygame.time.wait(100)
                        gamePaused = False
            
            if not gamePaused == True:
                if event.key == pygame.K_w:
                    blueMan.speed[1] = -1
                if event.key == pygame.K_a:
                    blueMan.speed[0] = -1
                if event.key == pygame.K_s:
                    blueMan.speed[1] = 1
                if event.key == pygame.K_d:
                    blueMan.speed[0] = 1
            else:
                blueMan.speed[1] = 0
                blueMan.speed[0] = 0
                

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                blueMan.speed[1] = 0
            if event.key == pygame.K_a:
                blueMan.speed[0] = 0
            if event.key == pygame.K_s:
                blueMan.speed[1] = 0
            if event.key == pygame.K_d:
                blueMan.speed[0] = 0
                
        if event.type == 1:
            if not gamePaused == True:
                if not blueMan.damageCooldown <= 0:
                    blueMan.damageCooldown -= 1
                blueMan.moveNpc(event)
                checkDoorCol()
                blocks_hit_list = pygame.sprite.spritecollide(blueMan, projectilesGroup, False)
                for i in blocks_hit_list:
                    if i.canHurtPlayer == True:
                        damagePlayer(1)
                        i.kill()
                blocks_hit_list = pygame.sprite.spritecollide(blueMan, enemysGroup, False)
                for i in blocks_hit_list:
                    if blueMan.damageCooldown <= 0:
                        damagePlayer(1)
                        blueMan.damageCooldown = blueMan.defDamageCooldown
                    
            
            theColBlock = pygame.sprite.Group()
            theColBlock.add(mouseColBox)
            
            for a in menuButtonsGroup:
                
                mbMouseCol = False
                blocks_hit_list = pygame.sprite.spritecollide(a , theColBlock, False)
                for i in blocks_hit_list:
                    a.enlargeButton()
                    mbMouseCol = True
                if mbMouseCol == False:
                    a.shrinkButton()

        if event.type == 2:
            if not gamePaused == True:
                for i in projectilesGroup:
                    i.moveProjectile()
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not gamePaused == True:
                launchProjectile([blueMan.rect.x + 16, blueMan.rect.y + 16], pygame.mouse.get_pos(), cropImage(r"images\projectiles\smallFireball.png"), 1, 1, 0, False)

            if gamePaused == True:
                for a in menuButtonsGroup:
                    #print(a.partType)#DEBUG
                    if a.partType == "button":
                        blocks_hit_list = pygame.sprite.spritecollide(a , theColBlock, False)
                        for i in blocks_hit_list:
                            if a.buttonType == "unpause":
                                if not findLivesLeft() <= 0:
                                    a.useButton()
                            else:
                                a.useButton()
                    
        if event.type == 3:
            if not gamePaused == True:
                for i in enemysGroup:
                    i.nextFrame()
                    i.moveEnemy()

                if findLivesLeft() <= 0:
                    gamePaused = True
                
        if event.type == 6:
            if gamePaused == True:
                for i in theColBlock:
                    i.updatePosition()
            #for i in doorsGroup.sprites():
                #if len(enemysGroup) >= 0:
                    #screen.blit(cropImage(r"images\doors\battle Gate.png"), copy.deepcopy(i.rect))
        
        if not gamePaused == True:
            if event.type == 4:
                for i in enemysGroup:
                    if not i.shootingData[0] == False:
                        i.shoot()

        pygame.time.set_timer(1, 10)
        pygame.time.set_timer(2, 10)
    pygame.time.set_timer(3, 10)
    pygame.time.set_timer(4, 10)
    pygame.time.set_timer(6, 10)
    screen.fill(black)
    #print(wallsGroup)#DEBUG
    for i in wallsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
    for i in doorsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
        if len(enemysGroup) > 0 and len(doorOverlayGroup) < len(doorsGroup):
            newDoorOverlay(cropImage(r"images\doors\battle Gate.png", 200), i.rect.x, i.rect.y)
        elif len(enemysGroup) <= 0 and len(doorOverlayGroup) > 0:
            print("Room Cleared!")
            for b in doorOverlayGroup:
                b.kill()
    doorOverlayGroup.draw(screen)
    for i in healthBar:
        screen.blit(i.image, i.rect)
    bodysGroup.draw(screen)
    propsGroup.draw(screen)
    screen.blit(blueMan.image, blueMan.rect)
    enemysGroup.draw(screen)
    projectilesGroup.draw(screen)
    enemysGroup.draw(screen)
    #Menu Screen Items Below
    if gamePaused == True:
        #if not currMusicPlaying == musicList[1]:
            #changeMusic(musicList[1])
        screen.blit(menuShade.image, menuShade.rect)
        screen.blit(titleShade.image, titleShade.rect)
        borderTilesGroup.draw(screen)
        screen.blit(menuGameTile.image, menuGameTile.rect)
        for i in menuButtonsGroup:
            if i.buttonType == "unpause":
                if not findLivesLeft() <= 0:
                    screen.blit(i.image, i.rect)
            else:
                screen.blit(i.image, i.rect)
        #menuButtonsGroup.draw(screen)
    #else:
        #if not currMusicPlaying == musicList[0]:
            #changeMusic(musicList[0])

    #KEEP LAST!
    #if gamePaused == True:
        #theColBlock.draw(screen)
    #screen.blit(mouseColBox.image, mouseColBox.rect)
    pygame.display.flip()
    
