import pygame
import math
import random

BLACK = (0,0, 0)
WHITE = (255, 255,255)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
GREEN = (50, 255, 50)
RED = (255, 0, 0)

LOOT_TYPES = ["weapon", "bullets", "paramedics", "armour"]
WEAPON_TYPES = ["glock", "ak47", "shotgun"]
BULLET_TYPES = ["pistols", "rifles", "shotguns"]
ARMOUR_TYPES = ["heavy", "medium", "light"]
PARAMEDIC_TYPES = ["heavy", "medium", "light"]

pygame.init()

size = (1000, 1000)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

clock = pygame.time.Clock()
#font
mainFont = pygame.font.SysFont("comicsans", 30)
secondaryFont = pygame.font.SysFont("comicsans", 20)

#classes

#People base class for player and enemy
class People(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, speed, health, bricks):
        self.bricks = bricks
        self.width = width
        self.height = height
        self.health = health
        self.speed = speed
        self.color = color
        self.bullets_list = pygame.sprite.Group()

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.playerX = 0
        self.playerY = 0

        #health bar component
        self.health_bar = HealthBar(self.rect.x, self.rect.y, self.width*2, self.height/3, self.health)

    def updatePlayerPosition(self, x, y):
        self.playerX = x
        self.playerY = y

    def getXPosition(self):
        return self.rect.x
    
    def getYPosition(self):
        return self.rect.y

    #method for wall colisions
    def isCollision(self):
        player_hit_group = pygame.sprite.spritecollide(self, self.bricks, False)
        flag = False
        direction = ""
        x = None
        y = None

        no_direction=["", "", "", ""]

        for hit in player_hit_group:
            flag = True
            #print("hit.rect.y: "+str(hit.rect.y))
            #print("self.rect.y: "+str(self.rect.y))
            x = hit.rect.x
            y = hit.rect.y

            if(self.rect.y == y+39):
                no_direction[0] = "up"
                self.rect.y = y+40
                print("up")

            if(self.rect.y+19 == y):
                no_direction[1] = "down"
                self.rect.y = y-20
                print("down")

            if(self.rect.x == x+39):
                no_direction[2] = "left"
                self.rect.x = x+40
                print("left")

            if(self.rect.x+19 == x):
                no_direction[3] = "right"
                self.rect.x = x-20
                print("right")


        return no_direction

    #move method
    def move(self):
        pass
    
    def setSpeed(self, speed):
        self.speed = speed

    #shooting method
    def shoot(self):
        #create a bullet object of type "pistol"
        bullet = Bullet(self.rect.x, self.rect.y, 10, 20, WHITE, "pistols")
        self.bullets_list.add(bullet)

    def drawHealthBar(self):
       
       if(self.health < 100):
           #print("Health: "+str(self.health))
           self.health_bar.update(self, self.health, True)
           self.health_bar.draw()




#brick class
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, brickSide):
        super().__init__()
        self.side = brickSide
        self.image = pygame.Surface([self.side, self.side])
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class ScoreBoard():
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.x = x
        self.y = y

    def draw(self, kills, score):
        kills_label = mainFont.render("Kills: "+str(kills), 1, WHITE)
        score_label = mainFont.render("Score: "+str(score), 1, WHITE)
        
        screen.blit(kills_label, (self.x, self.y))
        screen.blit(score_label, (self.x, self.y+40))
        

class HealthBar():
    def __init__(self, objX, objY, width, height, initHealth):
        self.maxHealth = initHealth
        self.outterContainer = pygame.Surface([width, height])
        self.outterContainer.fill(WHITE)
        self.rectOutter = self.outterContainer.get_rect()
        self.rectOutter.x = objX
        self.rectOutter.y = objY

        self.innerContainer = pygame.Surface([width, height])
        self.innerContainer.fill(GREEN)
        self.rectInner = self.innerContainer.get_rect()
        self.rectInner.x = objX
        self.rectInner.y = objY
        self.maxWidth = width
        self.height = height

    def update(self, player, health, isPlayer):
        percent = health/self.maxHealth
        newWidth = int(self.maxWidth * percent)

        if (newWidth <= 0):
            newWidth = 0

        self.innerContainer = pygame.Surface([newWidth, self.height])
        self.innerContainer.fill(GREEN)
        self.rectInner = self.innerContainer.get_rect()
        self.rectInner.x = player.rect.x-player.width/2
        

        self.rectOutter.x = player.rect.x-player.width/2
        if (isPlayer):
            self.rectOutter.y = player.rect.y + player.height + 10
            self.rectInner.y = player.rect.y + player.height + 10
        else:
            print(self)

            self.rectOutter.y = player.rect.y - 10
            self.rectInner.y = player.rect.y - 10

        self.draw()

    def draw(self):
        screen.blit(self.outterContainer, (self.rectOutter.x, self.rectOutter.y))
        screen.blit(self.innerContainer, (self.rectInner.x, self.rectInner.y))

#Player class
class Player(People, pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, speed, health, bricks, loot, inventory_capacity):
        super().__init__(x, y, width, height, color, speed, health, bricks)
        pygame.sprite.Sprite.__init__(self)
        self.weight_capacity = inventory_capacity
        self.inventory = []
        self.selectedWeapon = -1
        #declare the list of the number of bullets, where 0 - pistols bullets, 1 - rifles bullet, 2 - gunshot bullets
        self.bullets = [0, 0, 0]
        #weapons[0] for glocks, 1 for ak47, 2 for shotguns
        self.weapons = [False, False, False]
        self.max_amount_weapons = 3
        self.loot_group = loot

    def getInventoryWeight(self):
        weight = 0
        for item in self.inventory:
            weight += item.weight
        
        return weight

    def setSelectedWeapon(self, val):
        if(val <= len(self.weapons)):
            self.selectedWeapon = val-1
        print(self.selectedWeapon)

    #def rotatePlayer(self):
        #rot_image = pygame.transform.rotate(self.image, 1)
        #rot_image.get_rect(center=self.rect.center)
        #self.image = rot_image
        #self.rect = rot_image.get_rect()

    def heal(self, indx):
        medicine = self.getMedicineKitsAmount()
        val = 0
        if (len(medicine[indx-1]) > 0):
            arr = medicine[indx-1]
            val = arr[len(arr)-1].healing
            print(val)
            self.inventory.remove(arr[len(arr)-1])

        if (self.health + val >= 100):
            self.health = 100
        else:
            self.health += val


    def getWeaponsList(self):
        return self.weapons

    def getBulletsList(self):
        return self.bullets

    def checkLootCollision(self):
        total_weight = 0
        loot_hit_group = pygame.sprite.spritecollide(self, self.loot_group, False)
        for hit in loot_hit_group:
            if(hit.weight + self.getInventoryWeight() <= self.getWeightCapacity()):

                if(hit.name == "glock" and self.weapons[0] == 1) or (hit.name == "ak47" and self.weapons[1] == 1) or (hit.name == "shotgun" and self.weapons[2] == 1):
                    print("The weapon already exist")
                else:
                    self.inventory.append(hit)
                
                self.loot_group.remove(hit)

                if(hit.name == "bullet pistols"):
                    self.bullets[0] += hit.amount
                elif(hit.name == "bullet rifles"):
                    self.bullets[1] += hit.amount
                elif(hit.name == "bullet gunshots"):
                    self.bullets[2] += hit.amount

                if(hit.loot_type == "weapon"):
                    if (hit.name == "glock"):
                        self.weapons[0] = True
                    elif(hit.name == "ak47"):
                        self.weapons[1] = True
                    elif(hit.name == "shotgun"):
                        self.weapons[2] = True

                    print(self.weapons)
            print(hit.loot_type+ " was added to inventory!")

    def getInventory(self):
        return self.inventory

    def getWeightCapacity(self):
        return self.weight_capacity

    def getMousePosition(self):
        return pygame.mouse.get_pos()
    
    def getPlayerDirection(self):
        x, y = self.getMousePosition()
        vector = [0, 0]
        vector[0] = x - self.rect.x
        vector[1] = y - self.rect.y
        return vector

    def getPlayerBearing(self):
        vector = self.getPlayerDirection()
        fraction = vector[1]/vector[0]
        print("Tan: "+str(fraction))
        angle = math.atan(fraction)*180/math.pi

        if (vector[0]>0 and vector[1] < 0):
            angle *= -1
        elif (vector[0] > 0 and vector[1] > 0):
            angle += 90
        elif (vector[0] < 0 and vector[1] > 0):
            angle += 270
        elif (vector[0] < 0 and vector[1] < 0):
            angle += 270

        print(angle)
        return angle

    def getMedicineKitsAmount(self):
        counter = 0
        kits = []
        l = []
        m = []
        h = []
        for item in self.inventory:
            if (item.loot_type == "paramedic"):
                if(item.name == "paramedic light"):
                    l.append(item)
                elif(item.name == "paramedic medium"):
                    m.append(item)
                elif(item.name == "paramedic heavy"):
                    h.append(item)
            #increment the counter      
            counter += 1

        kits.append(l)
        kits.append(m)
        kits.append(h)

        return kits

    def isHitByEnemy(self, enemies):
        player_hit_group = pygame.sprite.spritecollide(self, enemies, False)

        for hit in player_hit_group:
           incrementKills()
           incrementScore(10)

    def isBulletCollisionWithEnemy(self, enemies, incrementKills, incrementScore):
        player_hit_group = pygame.sprite.groupcollide(self.bullets_list, enemies, True, True)

        for hit in player_hit_group:
           incrementKills()
           incrementScore(10)



    def shoot(self):
        self.getPlayerBearing()
       
        #check if there are any bullets for pistols
        if (self.bullets[0] > 0 and self.selectedWeapon == 0 and self.weapons[0]==True): 
            #create a bullet object of type "pistol"
            bullet = Bullet(self.rect.x, self.rect.y, 10, 20, WHITE, "pistols")
            self.bullets_list.add(bullet)
            self.bullets[0] -= 1
        elif(self.bullets[1] > 0 and self.selectedWeapon == 1 and self.weapons[1]==True):
            bullet = Bullet(self.rect.x, self.rect.y, 10, 20, GREEN, "rifles")
            self.bullets_list.add(bullet)
            self.bullets[1] -= 1
        elif(self.bullets[2] > 0 and self.selectedWeapon == 2 and self.weapons[2]==True):
            bullet = Bullet(self.rect.x, self.rect.y, 10, 20, BLUE, "gunshots")
            self.bullets_list.add(bullet)
            self.bullets[2] -= 1


    #move method for the player
    def move(self, direction):
        no_direction=self.isCollision()
        #check the collision with loot
        self.checkLootCollision()
        if (direction=="up" and no_direction[0]!="up"):
            self.rect.y -= self.speed
        elif(direction == "down" and no_direction[1]!="down"):
            self.rect.y += self.speed
        elif(direction == "left" and no_direction[2]!="left"):
            self.rect.x -= self.speed
        elif(direction == "right" and no_direction[3]!="right"):
            self.rect.x += self.speed

        self.updatePlayerPosition(self.rect.x, self.rect.y)

class Loot(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, loot_type, name):
        super().__init__()
        self.weight = 1 #default value for item weight
        self.name = loot_type+" "+name
        self.loot_type = loot_type
        self.width = width
        self.height = height
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Paramedic(Loot):
    def __init__(self, x, y, width, height, color, paramedicType):
        super().__init__(x, y, width, height, color, "paramedic", paramedicType)
        if (paramedicType == "light"):
            self.healing = 25
            self.weight = 2
        elif(paramedicType == "medium"):
            self.healing = 50
            self.weight = 5
        elif(paramedicType == "heavy"):
            self.healing = 75
            self.weight = 10

class InventoryList():
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    
    def draw(self, inventory, weight, maxWeight, bullets, weapons):
        header = mainFont.render("Inventory("+str(weight)+"/"+str(maxWeight)+"): ", 1, WHITE)
        counter = 0
        i = 0

        #for weapon in weapons:
        #    if(counter == 0):
        #        name = "glock pistol"
        #    elif(counter == 1):
        #        name = "ak47 rifle"
        #    elif(counter == 2):
        #        name = "shotgun"
        #    
        #    weapon_label = secondaryFont.render(name+" ("+str(weapons[i])+")", 1, WHITE)
        #    screen.blit(weapon_label, (self.x, self.y+counter*20))
        #    counter +=1

        #for bullet in bullets:
        #    
        #    if (i == 0):
        #        name = "weapon glock"
        #    elif(i == 1):
        #        name = "weapon rifles"
        #    elif(i == 2):
        #        name = "weapon shotguns"

        #    bullets_label = secondaryFont.render(name+" ("+str(bullets[i])+")", 1, WHITE)
        #    screen.blit(item_label, (self.x, self.y+counter*20))
        #    i += 1

        
        for item in inventory:
            counter+=1

            if (item.loot_type == "bullet"):
                if(item.name == "bullet glock"):
                    i = 0
                elif(item.name == "bullet rifles"):
                    i = 1
                elif(item.name == "bullet shotguns"):
                    i = 2

                item_label = secondaryFont.render(item.name+" ("+str(item.amount)+")", 1, WHITE)
            else:
                item_label = secondaryFont.render(item.name, 1, WHITE)

            screen.blit(item_label, (self.x, self.y+counter*20))
            
        
        screen.blit(header, (self.x, self.y))
        


class Weapon(Loot):
    def __init__(self, x, y, width, height, color, name):
        super().__init__(x, y, width, height, color, "weapon", name)
        #self.clip = clip
        if(name == "glock"):
            self.name = "glock"
            self.clip = 11
            self.quickness = 5
            self.damage = 10
            self.weight = 2
        elif(name == "ak47"):
            self.name = "ak47"
            self.clip = 50
            self.quickness = 10
            self.damage = 25
            self.weight = 5
        elif(name == "shotgun"):
            self.name = "shotgun"
            self.clip = 10
            self.quickness = 3
            self.damage = 45
            self.weight = 6

#class FireArm(Weapon):
#    def __init__(self, )
#        super().__init__()

class Enemy(People):
    def __init__(self, x, y, width, height, color, speed, health, bricks, player):
        super().__init__(x, y, width, height, color, speed, health, bricks)
        pygame.sprite.Sprite.__init__(self)
        self.attackVector = [0, 0, 0]
        self.player = player
        self.fieldView = 400

    def attack(self):
        
        if (self.attackVector[2] <= self.fieldView):
            self.move()

    def moveX(self, x):
        #print("VectorX: "+str(self.attackVector[0])+"   VectorY: "+str(self.attackVector[1]))
        pass

    def moveY(self, y):
        pass

    def move(self):
        no_direction=self.isCollision()
        if (self.attackVector[0] == 0):
            fraction = 0
        else:
            fraction = self.attackVector[1] / self.attackVector[0]

        xSpeed = self.speed/(math.sqrt(1+pow(fraction, 2)))
        ySpeed = xSpeed*fraction
        
        #print(ySpeed)
        if (self.attackVector[0] < 0):
            #left
            self.rect.x -= math.ceil(xSpeed)
        else:
            #right
            self.rect.x += math.ceil(xSpeed)


        if (self.attackVector[1] < 0):
            #down
            self.rect.y += math.ceil(ySpeed)
        else:
            #up
            self.rect.y -= (-1)*math.floor(ySpeed)


    def getVector(self):
        return self.attackVector

    def update(self):
        
        self.attackVector[0] = self.player.rect.x-self.rect.x
        self.attackVector[1] = self.rect.y-self.player.rect.y
        self.attackVector[2] = math.sqrt(pow(self.attackVector[0], 2)+pow(self.attackVector[1], 2))
        #print(self.attackVector)
        #print("playerX: "+str(self.player.rect.x)+"  enemyX: "+str(self.rect.x))
        if (self.attackVector[2] <= self.fieldView):
            self.attack()

        #print(self.attackVector[2])


class Armour(Loot):
    def __init__(self, x, y, width, height, color, Atype):
        super().__init__(x, y, width, height, color, "armour", Atype)
        if (Atype == "light"):
            self.armourHealth = 25
        elif (Atype == "medium"):
            self.armourHealth = 55
        elif(Atype == "heavy"):
            self.armourHealth = 100

class BulletsLoot(Loot):
    def __init__(self, x, y, width, height, color, bullet_type):
        super().__init__(x, y, width, height, color, "bullet", bullet_type)
        self.amount = random.randint(5, 50)
#Bullet class


class Bullet(pygame.sprite.Sprite):
    isVisible = False

    def __init__(self, x, y, width, height, color, bullet_type):
        super().__init__()
        self.name = "bullet "+bullet_type
        self.width = width
        self.height = height

        if(bullet_type == "pistols"):
            self.speed = 5
        elif(bullet_type == "rifles"):
            self.speed = 10
        elif(bullet_type == "shotguns"):
            self.speed = 3

        #surface
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def move(self):
        self.rect.y = self.rect.y - self.speed

    def draw(self):
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def update(self, group):
        self.move()
        if (self.rect.y < -20):
            group.remove(self)
            print("Remove the bullet")


#Game class
class Game():
    def __init__(self, brickSide):
        #pygame.mouse.set_visible(False)
        self.numBricks = 0
        self.brickSide = brickSide
        self.kills = 0
        self.score = 0
        self.wave = 1
        # declaration of sprite groups
        self.enemy_sprites_group = pygame.sprite.Group()
        self.all_sprites_group = pygame.sprite.Group()
        self.bricks_sprites_group = pygame.sprite.Group()
        self.loot_sprites_group = pygame.sprite.Group()

        #init the player and add him to the sprite group
        self.player = Player(100, 100, 20, 20, BLUE, 1, 100, self.bricks_sprites_group, self.loot_sprites_group, 50)
        self.all_sprites_group.add(self.player)

        self.done = False

        #init the inventory list board
        self.inventoryList = InventoryList(50, 50, 100, 100)

        #init the score board
        self.scoreBoard = ScoreBoard(830, 50, 100, 100)

        #create the border walls
        self.createOutterWalls()

        #randomly place the loot
        self.createLoot()
                    
        
        #creating the inner wall
        for i in range(5, 10):
            brick = Brick(i*self.brickSide, 5*40, self.brickSide)
            self.bricks_sprites_group.add(brick)
            self.numBricks += 1
        print(self.numBricks)



        

        #print(self.player)

    def incrementKills(self):
        self.kills += 1

    def incrementScore(self, val):
        self.score += val

    #randomly chosing the loot type and placing it on the map
    def createLoot(self):
        x = random.randint(40, 960)
        y = random.randint(40, 960)

        lootType = LOOT_TYPES[random.randint(0, len(LOOT_TYPES)-1)]
        if (lootType == "weapon"):
            weapon_type = WEAPON_TYPES[random.randint(0, len(WEAPON_TYPES)-1)]
            loot = Weapon(x, y, 20, 20, GREEN, weapon_type)
            print("The weapon "+weapon_type+"was added!")
        elif(lootType == "bullets"):
            bullet_type = BULLET_TYPES[random.randint(0, len(BULLET_TYPES)-1)]
            print("Bullets " + bullet_type + " were added!")
            loot = BulletsLoot(x, y, 20, 20, GREEN, bullet_type)
        elif(lootType == "paramedics"):
            paramedic_type = PARAMEDIC_TYPES[random.randint(0, len(PARAMEDIC_TYPES)-1)]
            print("Paramedic was added!")
            loot = Paramedic(x, y, 20, 20, GREEN, paramedic_type)
        elif(lootType == "armour"):
            armour_type = ARMOUR_TYPES[random.randint(0, len(ARMOUR_TYPES)-1)]
            print("Armour "+armour_type+" was added!")
            loot = Armour(x, y, 20, 20, GREEN, armour_type)

        #self.all_sprites_group.add(loot)
        self.loot_sprites_group.add(loot)
        
    def createOutterWalls(self):
        for row in range(0, int(1000/self.brickSide)) :
            for col in range(0, int(1000/self.brickSide)):
                if(row == 0) or (row == 1000/40-1):
                    #add block
                    brick = Brick(col*self.brickSide, row*self.brickSide, self.brickSide)
                    self.bricks_sprites_group.add(brick)
                    self.numBricks += 1
                elif(col == 0) or (col == 1000/40-1):
                    brick = Brick(col*self.brickSide, row*self.brickSide, self.brickSide)
                    self.bricks_sprites_group.add(brick)
                    self.numBricks += 1

    def start(self):
        self.done = False
        enemy = Enemy(600, 600, 20, 20, RED, 1, 100, self.bricks_sprites_group, self.player)
        self.enemy_sprites_group.add(enemy)
        self.all_sprites_group.add(enemy)
        self.mainLoop()

    def end(self):
        self.done = True

    def createEnemies(self, quantity):
        for i in range(quantity):
            x = random.randint(40, 940)
            y = random.randint(40, 940)

            enemy = Enemy(x, y, 20, 20, RED, 1, 100, self.bricks_sprites_group, self.player)
            self.enemy_sprites_group.add(enemy)
            self.all_sprites_group.add(enemy)

    def reRender(self):
        self.player.isBulletCollisionWithEnemy(self.enemy_sprites_group, self.incrementKills, self.incrementScore)
        self.enemy_sprites_group.update()
        self.player.bullets_list.update(self.player.bullets_list)
        #render the player
        self.all_sprites_group.draw(screen)
        self.player.bullets_list.draw(screen)
        self.player.drawHealthBar()
        self.bricks_sprites_group.draw(screen)
        self.loot_sprites_group.draw(screen)
        self.scoreBoard.draw(self.kills, self.score)
        self.inventoryList.draw(self.player.getInventory(), self.player.getInventoryWeight(), self.player.getWeightCapacity(), self.player.getBulletsList(), self.player.getWeaponsList())
        #self.loot_sprites_group.draw(screen)
        if (len(self.loot_sprites_group)==0):
            self.createLoot()
        
        if(len(self.enemy_sprites_group) == 0):
            self.wave += 1
            self.createEnemies(self.wave)

        pygame.display.update()

    def mainLoop(self):
        
        while not self.done:      
            screen.fill(BLACK)

            self.reRender()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end()
                if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1):
                    print("Left click!")
                    self.player.shoot()

            keys = pygame.key.get_pressed()

            if keys[pygame.K_a]:
                    #move the player to the right
                self.player.move("left")
            if keys[pygame.K_d]:
                    #move the player to the left
                self.player.move("right")
            if keys[pygame.K_w]:
                    #move the player up
                self.player.move("up")
            if keys[pygame.K_s]:
                #move the player down
                self.player.move("down")

            #selecting the weapon
            if keys[pygame.K_1]:
                self.player.setSelectedWeapon(1)
            if keys[pygame.K_2]:
                self.player.setSelectedWeapon(2)
            if keys[pygame.K_3]:
                self.player.setSelectedWeapon(3)

            if keys[pygame.K_t]:
                self.player.heal(1)
            if keys[pygame.K_y]:
                self.player.heal(2)
            if keys[pygame.K_u]:
                self.player.heal(3)

            if keys[pygame.K_LSHIFT]:
                #move the player down
                self.player.setSpeed(10)
            else:
                self.player.setSpeed(1)

            clock.tick(240)
        #EndWhile



game = Game(40)
game.start()

pygame.quit()
