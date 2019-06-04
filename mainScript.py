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
gameStarted = "STARTUP"
curStage = "ruin"

screen = pygame.display.set_mode(size)

#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#sounds
sounds = ["sounds/dig_2.wav", "sounds/dig_0.wav", "sounds/Item_10.wav", "sounds/dig_1.wav", "sounds/Jump_0.wav", "sounds/hurt.wav"]

        
#___MUSIC___
musicPosition = 0
musicList = [r"sounds/background.mp3", r"sounds/396082__romariogrande__space-pea-lava-dance.mp3",  r"sounds/388337__adnova__wishing.wav", r"sounds/Droobaxe Main.mp3"]
currMusicPlaying = r"sounds/background.mp3"
pygame.mixer.music.load(r"sounds/background.mp3")
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

pygame.mixer.music.set_volume(0.5)
    
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

#darkness = Surface(width, height)
#darkness.fill((0,0,0))

#___LOAD_SHEETS___
def newTileSheet(im, tw, th, upTileNum, acrossTileNum):
    tileImg = pygame.image.load(im)#.convert_alpha()
    tileImages = []
    for a in range(upTileNum):
        for b in range(acrossTileNum):
            surf = pygame.Surface((tw,th),pygame.SRCALPHA)
            surf.fill((255,0,255))
            surf.set_colorkey((255,0,255))
            surf.blit(tileImg,(-b*tw,-a*th))
            surf.set_alpha(0)
            surf = pygame.transform.scale(surf,(tw, th))
            tileImages.append(surf.convert_alpha())
    return tileImages

#___SET_ICON___
gameIcon = cropImage(r"images/gameIcon.png")
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


mouseColBox = colBox(cropImage(r"images/mouseColBox.png"), 0, 0)


#___Title_Screen_Items___
titleScreenItemGroup = pygame.sprite.Group()

class titleScreenItem(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

def newTitleScreenItem(im, x, y):
    theTitleScreenItem = titleScreenItem(cropImage(im), x, y)
    titleScreenItemGroup.add(theTitleScreenItem)

newTitleScreenItem(r"images/pauseScreen/topBorder.png",0 ,0)
newTitleScreenItem(r"images/pauseScreen/topBorder.png",0 ,height - 36)

#___Sliding_Title_Screen_Tiles___
slidingTitleScreenTileGroup = pygame.sprite.Group()

class slidingTitleScreenTile(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

    def move(self):
        self.rect = self.rect.move(0, -1)
        
def newSlidingTile(im, x, y):
    theSlidingTile = slidingTitleScreenTile(cropImage(im), x, y)
    slidingTitleScreenTileGroup.add(theSlidingTile)

def startSlidingTiles():
    for a in range((height // 36) + 1):
        newSlidingTile(r"images/pauseScreen/titleTile.png",0, a * 36)
        
    

#___PAUSESCREEN___
borderTilesGroup = pygame.sprite.Group()
menuButtonsGroup = pygame.sprite.Group()
floorMapGroup = pygame.sprite.Group()

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
        global gamePaused, healthBar, rooms, numOfRooms, currentRoomPos, roomPositions, roomBoss, bossDoorSpawned, Ecombs, currentRoom
        #print(self.buttonType)#DEBUG
        if not gameStarted == False and not gamePaused == False:
            if self.buttonType == "unpause":
                #print("UNPAUSED")#DEBUG
                gamePaused = False
            if self.buttonType == "quit":
                atStartup()
                
                #ResetHealth
                healthBar = []
                newHeart()
                newHeart()
                newHeart()
                newHeart()
                newHeart()
                newHeart()
                newHeart()
                newHeart()
                refreshHealthBar()

                Ecombs = ["NONE"]
                currentRoomPos = [0,0]
                roomPositions = []
                roomBoss = False
                bossDoorSpawned = False
                currentRoom = "1"
                numOfRooms = 1
                rooms = {}
                propTypes = [
                    [[cropImage(r"images/props/pots/clayPot.png"), cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
                    [[cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
                    [[cropImage(r"images/props/lights/light1.png"), cropImage(r"images/props/lights/light1Broken.png")], 100]
                ]
                
                #OTHER
                for i in projectilesGroup:
                    i.kill()
                    
                for i in doorsGroup:
                    i.kill()

                for i in wallsGroup:
                    i.kill()

                for i in enemysGroup:
                    i.kill()

                for i in bodysGroup:
                    i.kill()

                for i in propsGroup:
                    i.kill()
                    
                #RUNNING = False
                #pygame.display.quit()
                #pygame.quit()
                #sys.exit()
        if gameStarted == False:
            if self.buttonType == "startGame":
                startGame()
            
            
            
        
def newMenuBorder(im, rx, ry):
    theMenuBorder = pauseScreenPart(im, rx, ry)
    borderTilesGroup.add(theMenuBorder)
    
def newMenuButton(im, rx, ry, t):
    theMenuButton = pauseScreenPart(im, rx, ry)
    theMenuButton.makeButton(t)
    menuButtonsGroup.add(theMenuButton)
    
def newMapRoom(im, rx, ry):
    theMapRoom = pauseScreenPart(im, 342 + (rx * 9), 242 + (ry * 9))#Make Scale With Room Size #Make Smaller
    floorMapGroup.add(theMapRoom)

menuShade = pauseScreenPart(cropImage(r"images/pauseScreen/blackBlank.png", 200), 0, 0)
menuShade.resizePart(width, height)

blankShade = pauseScreenPart(cropImage(r"images/pauseScreen/blackBlank.png"), 0, 0)
blankShade.resizePart(width, height)

titleShade = pauseScreenPart(cropImage(r"images/pauseScreen/blackBlank.png", 175), 0, 0)
titleShade.resizePart(width, 78)

menuGameTile = pauseScreenPart(cropImage(r"images/pauseScreen/title.png"), 0, 39 - 19.5)
menuGameTile.centerPart()

mainGameTile = pauseScreenPart(cropImage(r"images/pauseScreen/title.png"), 0, 44)
mainGameTile.resizePart(634, 47)
mainGameTile.centerPart()


newMenuButton(cropImage(r"images/pauseScreen/button_x.png"), ((width // 36) * 36) - (36 + 18), 18, "unpause")
newMenuButton(cropImage(r"images/pauseScreen/button_quit.png"), 18, 18, "quit")

#Game Start Button
startGameButton = pauseScreenPart(cropImage(r"images/pauseScreen/button_start.png"), 0, 0)
startGameButton.centerPart()
startGameButton.makeButton("startGame")
menuButtonsGroup.add(startGameButton)


#Pause Screen Border
for i in range(0, height // 36):
    newMenuBorder(cropImage(r"images/pauseScreen/borderTileLeft.png"), 0, i * 36)

for i in range(0, height // 36):
    newMenuBorder(cropImage(r"images/pauseScreen/borderTileRight.png"), ((width // 36) * 36) - 73, i * 36)

mapRoomTiles = newTileSheet(r"images/pauseScreen/mapRooms.png", 9, 9, 2, 10)

def addRoomToMap(rt, rx, ry):
    global mapRoomTiles
    theRoomTypeImage = mapRoomTiles[0]
    if rt == "NORM":
        theRoomTypeImage = mapRoomTiles[0]
    elif rt == "TRAN":
        theRoomTypeImage = mapRoomTiles[1]
    elif rt == "BOSS":
        theRoomTypeImage = mapRoomTiles[1]
        
    newMapRoom(theRoomTypeImage,rx , ry * -1)

    
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
    def respawn(self):
        self.rect.x = 324
        self.rect.y = 324
#Health
try:
    if healthBar > 0:
        healthBar = healthBar
except NameError:
    healthBar = []
class heart:
    def __init__(self):
        self.image = cropImage(r"images/health/heartFull.png")#pygame.image.load("door.png")
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.full = True

    def thumpHeart(self):
        lastImage = self.image
        self.image = cropImage(r"images/health/heartFull.png")
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
            i.image = cropImage(r"images/health/heartFull.png", 200)
        else:
            #print("Empty")#DEBUG
            i.image = cropImage(r"images/health/heartEmpty.png", 200)
        
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
    newHeart()
    newHeart()
    newHeart()
    newHeart()
refreshHealthBar()
blueMan = player(random.choice([r"images/player/player_Andre.png", r"images/player/player_Grenwald.png", r"images/player/player_Victoria.png", r"images/player/player_Viper.png"]), [0, 0], 36, 36)

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

        blocks_hit_list = pygame.sprite.spritecollide(self, propsGroup, False)
        for i in blocks_hit_list:
            if i.isBroken == False:
                i.damageProp()
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
    def __init__(self, im, db, s, rx, ry, ad, es, si, h, nst, li, sd):
        pygame.sprite.Sprite.__init__(self)
        self.speed = s
        self.enemySpeed = es
        self.esI = es
        self.frames = self.enlargeFrames(si, im)
        self.image =  pygame.transform.scale(im[0], (int(im[0].get_width() * si), int(im[0].get_height() * si)))
        self.deadBody = pygame.transform.scale(db, (int(db.get_width() * si), int(db.get_height() * si)))
        self.theSize = si
        self.onFrame = 0
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.x = rx
        self.y = ry
        self.anamationDelay = ad
        self.adI = ad
        self.direction = "LEFT"
        self.nextStage = nst
        self.shootingData = sd #SHOOT- [canShoot, image, speed, size, fireRate, spread, gunBarrelPos] #SPAWN- [canShoot, spawnType, spawnRate, spawnPos]
        self.health = h
        self.hasLight = li
        if not self.shootingData[0] == False and not self.shootingData[0] == "SPAWN":
            self.shootingData[6] = self.shootingData[6] * si
            self.shootingDelay = self.shootingData[4]
            self.sdI = self.shootingData[4]
        elif self.shootingData[0] == "SPAWN":
            self.shootingDelay = self.shootingData[2]
            self.sdI = self.shootingData[2]
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

    def enlargeFrames(self, si, im):
        enlargedList = []
        for i in im:
            enlargedList.append(pygame.transform.scale(i, (int(i.get_width() * si), int(i.get_height() * si))))
        return enlargedList
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
                self.damage()
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
        if not self.shootingData[0] == False and not self.shootingData[0] == "SPAWN":
            if self.sdI <= 0:
                launchProjectile([self.rect.x + self.shootingData[6][0], self.rect.y + self.shootingData[6][1]], [blueMan.rect.x + 16, blueMan.rect.y + 16], cropImage(self.shootingData[1]), self.shootingData[3], self.shootingData[2], self.shootingData[5], True)
                self.sdI = self.shootingData[4]
            else:
                self.sdI -= 1
        elif self.shootingData[0] == "SPAWN":
            if self.sdI <= 0:
                spawnEnemy(self.shootingData[1], self.rect.x + self.shootingData[3][0], self.rect.y + self.shootingData[3][1])
                self.sdI = self.shootingData[2]
            else:
                self.sdI -= 1
            
    def damage(self):
        self.health -= 1
        #print("Damaged!")#DEBUG
        if self.health <= 0:
            newBody(self.deadBody, self.x, self.y)
            if not self.nextStage == "NONE":
                spawnEnemy(self.nextStage, self.rect.x, self.rect.y)
            self.kill()

def newEnemy(im, db, s, rx, ry, ad, es, si, h, nst, li, sd=[False]):
    theEnemy = enemy(im, db, s, rx, ry, ad, es, si, h, nst, li, sd)
    enemysGroup.add(theEnemy)
    
def randomSpawnPoint(w):
    return random.randint(36, w -36)

#___ruinImages___
ruinBeatleImages = newTileSheet(r"images/enemies/ruinBeatle.png", 33, 33, 2, 5)
ruinBossImages = newTileSheet(r"images/enemies/bosses/ruinBoss.png", 33, 20, 2, 5)
ruinBeatleEggImages = newTileSheet(r"images/enemies/beatleEgg.png", 33, 33, 2, 5)
redRuinBeatleImages = newTileSheet(r"images/enemies/redRuinBeatle.png", 33, 33, 2, 5)
greenRuinBeatleImages = newTileSheet(r"images/enemies/greenRuinBeatle.png", 33, 33, 2, 5)

#___caveImages___
flyImages = newTileSheet(r"images/enemies/fly.png", 33, 33, 2, 5)

#___cryptImages___
bonesImages = newTileSheet(r"images/enemies/bones.png", 33, 33, 2, 5)
bonesMageImages = newTileSheet(r"images/enemies/bonesMage.png", 33, 33, 2, 5)
bonesDarkMageImages = newTileSheet(r"images/enemies/bonesDarkMage.png", 33, 33, 2, 5)

def spawnEnemy(name, x="RAND", y="RAND"):
    if x == "RAND":
        x = randomSpawnPoint(width)
    if y == "RAND":
        y = randomSpawnPoint(height)
        
    #___ruin___
    if name == "RuinBeatle":
        newEnemy([ruinBeatleImages[1], ruinBeatleImages[2], ruinBeatleImages[1], ruinBeatleImages[3]], ruinBeatleImages[0], [0,0], x, y, 15, 3, 1, 2, "NONE", False)

    elif name == "Fly":
        newEnemy([flyImages[1], flyImages[2], flyImages[3], flyImages[2]], flyImages[0], [0,0], x, y, 2, 7, 1, 1, "NONE", False,
        [True, r"images/projectiles/smallFlyAcid.png", 1, 0.5, 250, 30, [16, 15]])

    elif name == "RuinBossStage1":
        newEnemy([ruinBossImages[2], ruinBossImages[3], ruinBossImages[2], ruinBossImages[4]], ruinBossImages[1], [0,0], x, y, 15, 5, 5, 30, "RuinBossStage2", False,
        ["SPAWN", "ruinBeatleEgg", 250, [16, 10]])#RedRuinBeatle

    elif name == "RuinBossStage2":
        newEnemy([ruinBossImages[2], ruinBossImages[3], ruinBossImages[2], ruinBossImages[4]], ruinBossImages[0], [0,0], x, y, 15, 2, 5, 30, "NONE", False,
        ["SPAWN", "RedRuinBeatle", 210, [16, 10]])#RedRuinBeatle

    elif name == "ruinBeatleEgg":
        newEnemy([ruinBeatleEggImages[0]], ruinBeatleEggImages[1], [0,0], x, y, 15, 9999 * 9999 * 9999, 0.5, 1, "RedRuinBeatle", False)

    elif name == "RedRuinBeatle":
        newEnemy([redRuinBeatleImages[1], redRuinBeatleImages[2], redRuinBeatleImages[1], redRuinBeatleImages[3]], redRuinBeatleImages[0], [0,0], x, y, 15, 1, 0.7, 1, "NONE", False)

    elif name == "GreenRuinBeatle":
        newEnemy([greenRuinBeatleImages[1], greenRuinBeatleImages[2], greenRuinBeatleImages[1], greenRuinBeatleImages[3]], greenRuinBeatleImages[0], [0,0], x, y, 15, 4, 2.5, 4, "NONE", False)

    #___cave___
    elif name == "Fly":
        newEnemy([flyImages[1], flyImages[2], flyImages[3], flyImages[2]], flyImages[0], [0,0], x, y, 2, 7, 1, 1, "NONE", False,
        [True, r"images/projectiles/smallFlyAcid.png", 1, 0.5, 250, 30, [16, 15]])
        
    #___crypt___
    elif name == "Bones":
        newEnemy([bonesImages[1], bonesImages[2]], bonesImages[0], [0,0], x, y, 40, 4, 1, 3, "NONE", False)

    elif name == "BonesMage":
        newEnemy([bonesMageImages[1], bonesMageImages[2]], bonesMageImages[0], [0,0], x, y, 2, 7, 1, 2, "NONE", 60,
        [True, r"images/projectiles/smallFireball.png", 1, 0.7, 120, 30, [5, 32]])

    elif name == "BonesDarkMage":
        newEnemy([bonesDarkMageImages[1], bonesDarkMageImages[2]], bonesDarkMageImages[0], [0,0], x, y, 2, 7, 1, 2, "NONE", 65,
        [True, r"images/projectiles/darkFireball.png", 1, 0.7, 50, 30, [5, 32]])

    #elif name == "CryptBossStage1":
        #newEnemy([cropImage(r"images/enemies/bosses/crypt/frame_0.png", 0), cropImage(r"images/enemies/bosses/crypt/frame_1.png", 0)], cropImage(r"images/enemies/bosses/crypt/dead_1.png"), [0,0], x, y, 15, 5, 5, 30, "RuinBossStage2", False,
        #["SPAWN", "RedRuinBeatle", 250, [16, 10]]) #PUT BACK IN

#___PROPS___
propsGroup = pygame.sprite.Group()
class prop(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry, l=False):
        pygame.sprite.Sprite.__init__(self)
        self.images = im
        self.image = im[0]
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.isBroken = False
        self.currImage = 0
        self.hasLight = l

    def damageProp(self):
        if self.currImage == len(self.images) - 2:
            #playSound(sounds[6])
            #self.kill()
            self.image = self.images[len(self.images) - 1]
            self.isBroken = True
        else:
            self.currImage += 1
            self.image = self.images[self.currImage]
    
def newProp(im, rx, ry, l=False):
    theProp = prop(im, rx, ry, l)
    #propsGroup.add(theProp)
    return theProp

def randSpot(a, propSize):
    return 36 + (propSize * random.randint(0, (a - (36 * 2)) // propSize))

propTypes = [
    [[cropImage(r"images/props/pots/clayPot.png"), cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
    [[cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
    [[cropImage(r"images/props/lights/light1.png"), cropImage(r"images/props/lights/light1Broken.png")], 100]
]

propImages = newTileSheet(r"images/props/pots/propPots.png", 33, 33, 6, 10)

def makeProps(isP=False, p=[]):
    theProps = []
    for i in range(5):
        if isP == True:
            thePropData = random.choice(p)
        else:
            thePropData = random.choice(propTypes)
        theProps.append(newProp(thePropData[0], randSpot(width, 33), randSpot(height, 33), thePropData[1]))
    print(theProps)
    return theProps

        
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
            self.image = pygame.image.load(r"images/doors/door.png")
            self.defDoor = pygame.image.load(r"images/doors/door.png")
        elif self.doorType == "NORMBOSS":
            self.image = pygame.image.load(r"images/doors/bossDoorBack.png")
            self.defDoor = pygame.image.load(r"images/doors/bossDoorBack.png")
        elif self.doorType == "DEMON":
            self.image = pygame.image.load(r"images/doors/demonDoor.png")
            self.defDoor = pygame.image.load(r"images/doors/demonDoor.png")
        elif self.doorType == "DUNFRONT":
            self.image = pygame.image.load(r"images/doors/dungeonFrontEntrance.png")
            self.defDoor = pygame.image.load(r"images/doors/dungeonFrontEntrance.png")
        elif self.doorType == "BOSS":
            self.image = pygame.image.load(r"images/doors/bossDoor2.png")
            self.defDoor = pygame.image.load(r"images/doors/bossDoor2.png")
        self.rect = self.image.get_rect()
        self.rect.x = rx - 1
        self.rect.y = ry - 1
        self.doorId = did
        self.targetRoom = tgr
        self.targetDoor = tgd
        self.doorMat = dm

    def useDoor(self):
        global numOfRooms, currentRoom, displayPlayfeild, currentRoomPos, rooms, propsGroup, roomBoss, bossDoorSpawned
        rooms[currentRoom][4] = []
        for i in propsGroup:
            rooms[currentRoom][4].append(i)
        for i in propsGroup:
            i.kill()
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
                if self.doorType == "BOSS":
                    print("Boss Room Entered!")
                    IDsToUse = [a]
                    doorSpotsToUse = ["BOTTOM"]
                    roomBoss = True
                
                #encaseRoom(self.targetRoom, randomWallTiles([[r"images/walls/ruin/wallRuinPlain.png", 3], [r"images/walls/ruin/wallRuinDamaged.png", 1], [r"images/walls/ruin/wallRuinOvergrown.png", 1]]))
                if self.rect.y + 1 == ((height // 36) - 1) * 36:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    if self.doorType == "BOSS":
                        newDoor(self.rect.x + 1, 0, self.targetRoom, currentRoom, theId, self.doorId, "UP", "NORMBOSS")
                    else:
                        newDoor(self.rect.x + 1, 0, self.targetRoom, currentRoom, theId, self.doorId, "UP")
                    print("New top door made! DoorID:", theId)
                    doorSpotsToUse.remove("TOP")
                    IDsToUse.remove(theId)
                    self.targetDoor = theId
                    theId = None
                elif self.rect.y + 1 == 0:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    if self.doorType == "BOSS":
                        newDoor(self.rect.x + 1, ((height // 36) * 36) - 36, self.targetRoom, currentRoom, theId, self.doorId, "DOWN", "NORMBOSS")
                    else:
                        newDoor(self.rect.x + 1, ((height // 36) * 36) - 36, self.targetRoom, currentRoom, theId, self.doorId, "DOWN")
                    print("New bottom door made! DoorID:", theId)
                    doorSpotsToUse.remove("BOTTOM")
                    IDsToUse.remove(theId)
                    self.targetDoor = theId
                    theId = None
                elif self.rect.x + 1 == 0:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    if self.doorType == "BOSS":
                        newDoor(((width // 36) * 36) - 36, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "RIGHT", "NORMBOSS")
                    else:
                        newDoor(((width // 36) * 36) - 36, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "RIGHT")
                    print("New right door made! DoorID:", theId)
                    doorSpotsToUse.remove("RIGHT")
                    self.targetDoor = theId
                    IDsToUse.remove(theId)
                    theId = None
                elif self.rect.x + 1 == ((width // 36) * 36) - 36:
                    theId = IDsToUse[len(IDsToUse) - 1]
                    if self.doorType == "BOSS":
                        newDoor(0, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "LEFT", "NORMBOSS")
                    else:
                        newDoor(0, self.rect.y + 1, self.targetRoom, currentRoom, theId, self.doorId, "LEFT")
                    print("New left door made! DoorID:", theId)
                    doorSpotsToUse.remove("LEFT")
                    self.targetDoor = theId
                    IDsToUse.remove(theId)
                    theId = None
                    
                encaseRoom(self.targetRoom, randomTiles(tileSets))
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
                                        if random.randint(1,1) == 1 and not bossDoorSpawned == True and numOfRooms >= 15:
                                            newDoor((((width // 36) * 36) - 36) / 2, 0, self.targetRoom, "NONE", IDa, "a", "UP", "BOSS")
                                            bossDoorSpawned = True
                                        else:
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
numOfRooms = 1#CHANGE BACK TO 1
currentRoomPos = [0,0]
roomPositions = []
roomBoss = False
bossDoorSpawned = False
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
    for i in rooms[theId][4]:
        print(i)
        propsGroup.add(i)
    theI = 0
    for i in rooms[theId][2]:
        if i == "NONE":
            rooms[theId][2][theI] = currentRoomPos[theI]
            if roomBoss == True:
                addRoomToMap("BOSS", currentRoomPos[0], currentRoomPos[1])
            else:
                addRoomToMap("NORM", currentRoomPos[0], currentRoomPos[1])
            print("Created Map Room")#DEBUG
        theI += 1
    if not rooms[theId][2] in roomPositions:
        roomPositions.append(rooms[theId][2])
        addRoomToMap("REPLACE", currentRoomPos[0], currentRoomPos[1])#REPLACE Text
        print("Created Map Room")#DEBUG
    
    for i in rooms[theId][3]:
        spawnEnemy(i)
    rooms[theId][3] = []
    print('Loaded room "' + str(theId) + '"!')
    #print(rooms[theId][2], currentRoomPos)#DEBUG
    

class wall(pygame.sprite.Sprite):
    def __init__(self, im, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        if isinstance(im, str):
            self.image = pygame.image.load(im)
        else:
            self.image = im
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry

      
Ecombs = ["NONE"]
isDarkInRoom = False

def newDoor(x, y, roomId, targetRoom, doorId, targetDoor, doorMat, doorType="NORM"):
    global roomBoss, propImages
    theDoor = door(x, y, doorId, targetRoom, targetDoor, doorMat, doorType)
    def randomEnemies(e):
        return random.choice(e)
    while True:
        try:
            rooms[roomId][1].append(theDoor)
            for i in rooms[roomId][0]:
                if i.rect.x == theDoor.rect.x + 1 and i.rect.y == theDoor.rect.y + 1:
                    rooms[roomId][0].remove(i)
            break
        except KeyError:
            if not roomBoss == True:
                rooms[roomId] = [[], [], ["NONE", "NONE"], randomEnemies(copy.deepcopy(Ecombs)), makeProps(), isDarkInRoom]
            else:
                print("Spawning Boss!")
                if curStage == "ruin":
                    print("Ruin Boss!")
                    rooms[roomId] = [[], [], ["NONE", "NONE"], ["RuinBossStage1"], makeProps(True, [
                        [[propImages[3], propImages[4]], 0],
                        [[propImages[5], propImages[6]], 0]
                    ]), False]
                    roomBoss = False
                elif curStage == "ruin":
                    rooms[roomId] = [[], [], ["NONE", "NONE"], ["CryptBossStage1"], [], False]
                    roomBoss = False

def newWall(image, x, y, roomId):
    theWall = wall(image, x, y)
    def randomEnemies(e):
        return random.choice(e)
    while True:
        try:
            rooms[roomId][0].append(theWall)
            break
        except KeyError:
            rooms[roomId] = [[], [], ["NONE", "NONE"], randomEnemies(copy.deepcopy(Ecombs)), makeProps(), isDarkInRoom]
            
def encaseRoom(roomId, theImages, whatSides=[True, True, True, True]): #[Top, Left, Bottom, Right]
    if whatSides[0] == True:
        for i in range(0, width // 36):
            newWall(random.choice(theImages), i * 36 , 0, roomId)
            
    if whatSides[1] == True:
        for i in range(1, height // 36):
            newWall(random.choice(theImages), 0 , i * 36, roomId)

    if whatSides[2] == True:
        for i in range(0, width // 36):
            newWall(random.choice(theImages), i * 36 , ((height // 36) - 1) * 36, roomId)

    if whatSides[3] == True:
        for i in range(1, height // 36):
            newWall(random.choice(theImages), ((width // 36) - 1) * 36, i * 36, roomId)

tranTiles = newTileSheet(r"images/walls/tran/tran.png", 36, 36, 3, 5)
ruinTranTiles = newTileSheet(r"images/walls/tran/ruinTran.png", 36, 36, 3, 5)


#___Create Tran Room___
def createTranRoom(cS):
    global tranTiles, ruinTranTiles

    if cS == "ruin":
        encaseRoom("1", randomWallTiles([[ruinTranTiles[0], 10], [ruinTranTiles[1], 3], [ruinTranTiles[5], 2]]), [True, False, False, False])
        encaseRoom("1", randomWallTiles([[ruinTranTiles[2], 3], [ruinTranTiles[3], 2], [ruinTranTiles[4], 1]]), [False, True, True, True])
        
        
    else:
        encaseRoom("1", randomWallTiles([[tranTiles[0], 15], [tranTiles[1], 2], [tranTiles[2], 1]]))
        
def randomTiles(t):
    return randomWallTiles(random.choice(t))

#Walls Below
#encaseRoom("1", randomWallTiles([[tranTiles[0], 10], [tranTiles[1], 1], [tranTiles[2], 1]]))
#randomWallTiles([[r"images/walls/purple/wallPurple.png", 90], [r"images/walls/purple/wallPurpleText1.png", 1], [r"images/walls/purple/wallPurpleEye.png", 1], [r"images/walls/purple/wallPurpleText2.png", 1]])
#randomWallTiles([[r"images/walls/ruin/wallRuinPlain.png", 30], [r"images/walls/ruin/wallRuinDamaged.png", 10], [r"images/walls/ruin/wallRuinOvergrown.png", 10], [r"images/walls/ruin/wallRuinText1.png", 1], [r"images/walls/ruin/wallRuinText2.png", 1]])
#randomWallTiles([[r"images/walls/ruin/wallRuinPlain.png", 3], [r"images/walls/ruin/wallRuinDamaged.png", 1], [r"images/walls/ruin/wallRuinOvergrown.png", 1]])

#encaseRoom("2", "wallPurple.png")
#newWall("wall.png", 0, 36, "1")

#Doors Below
#newDoor((((width // 36) * 36) - 36) / 2, ((width // 36) * 36) - 36, "1", "NONE", "b", "a", "DOWN", "NORM")
#newDoor(0, (((height // 36) * 36) - 36) / 2, "1", "NONE", "c", "a", "LEFT", "NORM")
#newDoor(((width // 36) * 36) - 36, (((height // 36) * 36) - 36) / 2, "1", "NONE", "d", "a", "RIGHT", "NORM")
#newDoor(108, ((height // 36) * 36) - 36, "2", "1", "b", "a", "DOWN")

#___SET_FLOOR____

def setFloorSets(f):
    global tileSets, Ecombs, propTypes, isDarkInRoom
    ruinTiles = newTileSheet(r"images/walls/ruin/ruin.png", 36, 36, 3, 5)
    caveTiles = newTileSheet(r"images/walls/cave/cave.png", 36, 36, 3, 5)
    cryptTiles = newTileSheet(r"images/walls/crypt/crypt.png", 36, 36, 3, 5)
    
    if f == "ruin":
        changeMusic(musicList[0]) 
        
        isDarkInRoom = False
        tileSets = [
            [[ruinTiles[6], 30], [ruinTiles[0], 10], [ruinTiles[3], 10], [ruinTiles[7], 1], [ruinTiles[8], 1]],
            [[ruinTiles[6], 3], [ruinTiles[0], 1], [ruinTiles[3], 1]],
            [[ruinTiles[6], 3], [ruinTiles[0], 1], [ruinTiles[3], 1]],
            [[ruinTiles[6], 3], [ruinTiles[0], 1], [ruinTiles[3], 1]],
            [[ruinTiles[0], 1], [ruinTiles[1], 3], [ruinTiles[2], 2], [ruinTiles[4], 1], [ruinTiles[5], 1], [ruinTiles[3], 1]]
        ]
        Ecombs = [
            ["RuinBeatle", "RuinBeatle"],
            ["RedRuinBeatle", "RedRuinBeatle", "RuinBeatle", "GreenRuinBeatle"],
            ["RedRuinBeatle", "RedRuinBeatle"],
            ["RedRuinBeatle", "RedRuinBeatle"],
            ["RuinBeatle", "RuinBeatle", "GreenRuinBeatle"],
            ["RuinBeatle", "GreenRuinBeatle"],
            ["RedRuinBeatle", "RedRuinBeatle"],
            ["RuinBeatle"],
            ["RuinBeatle", "RuinBeatle"],
            ["GreenRuinBeatle"]
        ]
        propTypes = [
            [[cropImage(r"images/props/pots/clayPot.png"), cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
            [[cropImage(r"images/props/pots/clayPotOvergrown.png"), cropImage(r"images/props/pots/clayPotBroken.png")], 0],
            [[cropImage(r"images/props/lights/light1.png"), cropImage(r"images/props/lights/light1Broken.png")], 100]
        ]

    if f == "cave":
        changeMusic(musicList[0]) 

        isDarkInRoom = False
        
        tileSets = [
            [[caveTiles[0], 30], [caveTiles[1], 5]],
            [[caveTiles[0], 30], [caveTiles[1], 5]],
            [[caveTiles[1], 30], [caveTiles[0], 5]],
            [[caveTiles[1], 30], [caveTiles[0], 5]],
            [[caveTiles[0], 10], [caveTiles[1], 1], [caveTiles[2], 2], [caveTiles[3], 2], [caveTiles[4], 2]],
            [[caveTiles[1], 20], [caveTiles[0], 4], [caveTiles[5], 2]],
        ]
        Ecombs = [
            ["Bones", "BonesMage"],
            ["BonesDarkMage"],
        ]
        propTypes = [
            [[cropImage(r"images/props/pots/bonePile.png"), cropImage(r"images/props/pots/bonePileBroken.png")], 0],
            [[cropImage(r"images/props/lights/light1.png"), cropImage(r"images/props/lights/light1Broken.png")], 80],
            [[cropImage(r"images/props/lights/bonePileCandle.png"), cropImage(r"images/props/lights/bonePileCandleBroken.png")], 75]
        ]
        
    if f == "crypt":
        changeMusic(musicList[0]) 

        isDarkInRoom = True
        
        tileSets = [
            [[cryptTiles[1], 30], [cryptTiles[0], 5], [cryptTiles[3], 1], [cryptTiles[4], 1], [cryptTiles[5], 1], [cryptTiles[6], 1]],
            
        ]
        Ecombs = [
            ["Bones", "BonesMage"],
            ["BonesDarkMage"],
        ]
        propTypes = [
            [[cropImage(r"images/props/pots/bonePile.png"), cropImage(r"images/props/pots/bonePileBroken.png")], 0],
            [[cropImage(r"images/props/lights/light1.png"), cropImage(r"images/props/lights/light1Broken.png")], 80],
            [[cropImage(r"images/props/lights/bonePileCandle.png"), cropImage(r"images/props/lights/bonePileCandleBroken.png")], 75]
        ]

def atStartup():
    global gamePaused, gameStarted
    changeMusic(musicList[3])
    gamePaused = True
    gameStarted = False
    if len(slidingTitleScreenTileGroup) <= 0:
        startSlidingTiles()
    
def startGame():
    global gamePaused, gameStarted, Ecombs, curStage
    Ecombs = ["NONE"]
    curStage = "ruin"#ruin
    createTranRoom(curStage)
    #encaseRoom("1", randomWallTiles([[tranTiles[0], 10], [tranTiles[1], 1], [tranTiles[2], 1]]))
    if curStage == "ruin":
        newDoor((((width // 36) * 36) - 36) / 2, 0, "1", "NONE", "a", "b", "UP", "DUNFRONT")#DEMON
    else:
        newDoor((((width // 36) * 36) - 36) / 2, 0, "1", "NONE", "a", "b", "UP", "DEMON")#Change to Tran door!
    if len(wallsGroup) == 0 and len(doorsGroup) == 0:
        loadRoom(currentRoom)
    setFloorSets(curStage)
    blueMan.respawn()
    gamePaused = False
    gameStarted = True
    

RUNNING = True
while RUNNING == True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if gamePaused == True:
                RUNNING = False
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            else:
                gamePaused = True
            
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
                launchProjectile([blueMan.rect.x + 16, blueMan.rect.y + 16], pygame.mouse.get_pos(), cropImage(r"images/projectiles/smallFireball.png"), 1, 1, 0, False)

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
            if gameStarted == False:
                for i in slidingTitleScreenTileGroup:
                    if i.rect.y <= -36:
                        newSlidingTile(r"images/pauseScreen/titleTile.png",i.rect.x, 684)
                        i.kill()
                    i.move()
                

                
            if not gamePaused == True or findLivesLeft() <= 0:
                for i in enemysGroup:
                    i.nextFrame()
                    if not findLivesLeft() <= 0:
                        i.moveEnemy()

                if findLivesLeft() <= 0:
                    gamePaused = True
                    
            for a in propsGroup:
                blocks_hit_list = pygame.sprite.spritecollide(a, wallsGroup, False)
                for i in blocks_hit_list:
                    a.kill()
        if event.type == 6:
            if gamePaused == True:
                for i in theColBlock:
                    i.updatePosition()
            #for i in doorsGroup.sprites():
                #if len(enemysGroup) >= 0:
                    #screen.blit(cropImage(r"images/doors/battle Gate.png"), copy.deepcopy(i.rect))
        
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
    screen.fill((15, 15, 15))
    #print(wallsGroup)#DEBUG
    for i in wallsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
    for i in doorsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
        if len(enemysGroup) > 0 and len(doorOverlayGroup) < len(doorsGroup):
            newDoorOverlay(cropImage(r"images/doors/battle Gate.png", 200), i.rect.x, i.rect.y)
        elif len(enemysGroup) <= 0 and len(doorOverlayGroup) > 0:
            print("Room Cleared!")
            for b in doorOverlayGroup:
                b.kill()
    doorOverlayGroup.draw(screen)
    bodysGroup.draw(screen)
    propsGroup.draw(screen)
    screen.blit(blueMan.image, blueMan.rect)
    enemysGroup.draw(screen)
    projectilesGroup.draw(screen)

    def drawDarkness():
        if rooms[currentRoom][5] == True:
            surf = pygame.Surface((width, height))
            img = pygame.Surface((width, height))
            surf.fill((0, 0, 0))
            pygame.draw.circle(img, (225,0,225),(blueMan.rect.x + 16, blueMan.rect.y + 16), 100)
            for m in projectilesGroup:
                pygame.draw.circle(img, (225,0,225),(m.rect.x + (m.image.get_width() // 2), m.rect.y + (m.image.get_height() // 2)), 40)
            
            for m in propsGroup:
                if not m.hasLight == False and m.isBroken == False:
                    pygame.draw.circle(img, (225,0,225),(m.rect.x + (m.image.get_width() // 2), m.rect.y + (m.image.get_height() // 2)), m.hasLight)

            for m in enemysGroup:
                if not m.hasLight == False:
                    pygame.draw.circle(img, (225,0,225),(m.rect.x + (m.image.get_width() // 2), m.rect.y + (m.image.get_height() // 2)), m.hasLight)

            for m in doorOverlayGroup:
                pygame.draw.circle(img, (225,0,225),(m.rect.x + (m.image.get_width() // 2), m.rect.y + (m.image.get_height() // 2)), 40)


            surf.set_colorkey((225,0,225))
            #surf.set_alpha(50)
            surf.blit(img, (0,0))
            screen.blit(surf, (0,0))
    if gameStarted == True:       
        drawDarkness()
    for i in healthBar:
        screen.blit(i.image, i.rect)

    #Game Over Screen
    myfont = pygame.font.Font(r"fonts/slkscr.ttf", 110)
    gameOverTextF = myfont.render('Game Over', True, (238, 227, 238))
    gameOverTextB = myfont.render('Game Over', True, (49, 30, 49))
    
    #Menu Screen Items Below
    if gamePaused == True and not gameStarted == False:
        #if not currMusicPlaying == musicList[1]:
            #changeMusic(musicList[1])
        if not findLivesLeft() <= 0:
            screen.blit(menuShade.image, menuShade.rect)
            screen.blit(blankShade.image, blankShade.rect)
            borderTilesGroup.draw(screen)
            floorMapGroup.draw(screen)
            screen.blit(menuGameTile.image, menuGameTile.rect)

        if findLivesLeft() <= 0:
            screen.blit(menuShade.image, menuShade.rect)
            screen.blit(gameOverTextB,(-5,300))
            screen.blit(gameOverTextF,(5,300))
                    
        for i in menuButtonsGroup:
            if i.buttonType == "unpause":
                if not findLivesLeft() <= 0:
                    screen.blit(i.image, i.rect)
            else:
                if i.buttonType == "quit" or not findLivesLeft() <= 0:
                    if not i.buttonType == "startGame":
                        screen.blit(i.image, i.rect)

    if gameStarted == False:
        screen.blit(blankShade.image, blankShade.rect)
        slidingTitleScreenTileGroup.draw(screen)
        borderTilesGroup.draw(screen)
        titleScreenItemGroup.draw(screen)
        screen.blit(mainGameTile.image, mainGameTile.rect)
        for i in menuButtonsGroup:
            if i.buttonType == "startGame":
                screen.blit(i.image, i.rect)

        #menuButtonsGroup.draw(screen)
    #else:
        #if not currMusicPlaying == musicList[0]:
            #changeMusic(musicList[0])

    #KEEP LAST!
    if gameStarted == "STARTUP":
        atStartup()
    
    pygame.display.flip()
    
