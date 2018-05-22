import pygame, sys, math, time, os, random, pickle, datetime, webbrowser, copy
#import sys, pygame, copy
from pygame.locals import *
pygame.mixer.pre_init(44100, 16, 9999, 4096)
pygame.init()


size = width, height = 684, 684
speed = [2, 2]
black = 0, 0, 0
displayPlayfeild = True

screen = pygame.display.set_mode(size)
#sounds
sounds = ["sounds\dig_2.wav", "sounds\dig_0.wav", "sounds\Item_10.wav", "sounds\dig_1.wav", "sounds\Jump_0.wav"]

pygame.mixer.music.load(r"sounds\background.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)
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

#heartFrames = cropImage("heartFull.png")

#___PLAYER___
class player(pygame.sprite.Sprite):
    def __init__(self, im, s, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(im)#im
        self.rect = self.image.get_rect()
        self.speed = s
        self.rect.x = rx
        self.rect.y = ry
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
        blocks_hit_list = pygame.sprite.spritecollide(self, wallsGroup, False)
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

def damagePlayer(d):
    damageLeft = d
    while damageLeft > 0:
        theIndex = 0
        for i in healthBar:
            if i.full == True:
                i.thumpHeart()
                healthBar[theIndex].full = False
                damageLeft -= 1
                break
            theIndex += 1
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
    def __init__(self, im, s, rx, ry):
        pygame.sprite.Sprite.__init__(self)
        self.speed = s
        self.image = im#pygame.image.load(im)
        self.rect = self.image.get_rect()
        self.rect.x = rx
        self.rect.y = ry
        self.ProID = random.randint(-9999999999, 9999999999)
    def moveProjectile(self):
        self.rect = self.rect.move(self.speed)
        for currList in [wallsGroup, doorsGroup]:
            blocks_hit_list = pygame.sprite.spritecollide(self, currList, False)
            for i in blocks_hit_list:
                #self.speed = [-self.speed[0], -self.speed[1]]
                sounds[4]
                self.kill()

def newProjectile(im, s, rx, ry):
    theProjectile = projectile(im, s, rx, ry)
    projectilesGroup.add(theProjectile)
    
def launchProjectile(launchSource, targetDirection, projectileImage, projectileSpeedMult=1):
    projectileSlope = [targetDirection[0] - launchSource[0], targetDirection[1] - launchSource[1]]
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
    newProjectile(projectileImage, projectileSpeed, launchSource[0], launchSource[1])
    playSound(sounds[2])

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
        elif self.doorType == "DEMON":
            self.image = pygame.image.load(r"images\doors\demonDoor.png")
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
    for i in rooms[theId][1]:
        doorsGroup.add(i)
    theI = 0
    for i in rooms[theId][2]:
        if i == "NONE":
            rooms[theId][2][theI] = currentRoomPos[theI]
        theI += 1
    if not rooms[theId][2] in roomPositions:
        roomPositions.append(rooms[theId][2])
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
            rooms[roomId] = [[], [], ["NONE", "NONE"]]

def newWall(image, x, y, roomId):
    theWall = wall(image, x, y)
    while True:
        try:
            rooms[roomId][0].append(theWall)
            break
        except KeyError:
            rooms[roomId] = [[], [], ["NONE", "NONE"]]
            
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

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                blueMan.speed[1] = -1
            if event.key == pygame.K_a:
                blueMan.speed[0] = -1
            if event.key == pygame.K_s:
                blueMan.speed[1] = 1
            if event.key == pygame.K_d:
                blueMan.speed[0] = 1

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
            blueMan.moveNpc(event)
            checkDoorCol()

        if event.type == 2:
            for i in projectilesGroup:
                i.moveProjectile()
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            launchProjectile([blueMan.rect.x + 16, blueMan.rect.y + 16], pygame.mouse.get_pos(), cropImage(r"images\projectiles\smallFireball.png", 200))
            

        pygame.time.set_timer(1, 10)
        pygame.time.set_timer(2, 10)
    screen.fill(black)
    screen.blit(blueMan.image, blueMan.rect)
    #print(wallsGroup)#DEBUG
    for i in wallsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
    for i in doorsGroup.sprites():
        if displayPlayfeild == True:
            screen.blit(i.image, i.rect)
    for i in healthBar:
        screen.blit(i.image, i.rect)
    #for i in projectilesGroup.sprites():
        #screen.blit(i.image, i.rect)
    projectilesGroup.draw(screen)
    pygame.display.flip()
