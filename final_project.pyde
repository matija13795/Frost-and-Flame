add_library('minim')
import os, time

RESOLUTION_W = 1280
RESOLUTION_H = 720
GROUND = 605
path   = os.getcwd()
player = Minim(this)


# as yeti and mage have a lot of atributes and methods in common, it is useful to have a parent class they can inherit fromn
class Character:
    
    def __init__(self, x, y, r, img, img_w, img_h, slices):
        self.x = x
        self.y = y
        self.r = r
        self.ground = GROUND
        self.vx = 0
        self.vy = 0
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h
        self.slices = slices
        self.dir = RIGHT
        
    def gravity(self):
        for platform in game.platforms:
            if self.y + 2 * self.r <= platform.y and self.x + 75>= platform.x and self.x + self.r  <= platform.x + platform.w:
                self.ground = platform.y
                break
            else:
                self.ground = GROUND
        
        if self.y +  2 *self.r <= self.ground:
            self.vy += 0.3
            if self.y + 2 * self.r + self.vy > self.ground:
                self.vy = self.ground - (self.y + 2 * self.r)
        else:
            self.vy = 0     
            
    def update(self):
        self.gravity()
        self.x += self.vx
        self.y += self.vy
    
  
      
class Yeti(Character):
    
    def __init__(self, x, y, r, img, img_w, img_h, slices):
        Character.__init__(self, x, y, r, img, img_w, img_h, slices)
        self.key_handler = {LEFT:False, RIGHT:False, UP:False, "attack": False}
        self.alive = True
        self.slice = 0
        self.action = None     # attribute to specify what animation the character has to perform
        self.run_jump = False  # if yeti jumps while on ice, we want him to keep the momentum
        
    def update(self):
        
        self.gravity()
        
        if self.key_handler[LEFT] == True:
            self.dir = LEFT
            self.vx = -7
            
            if self.y + 2*64 == self.ground: # if yeti jumps while on ice tile, we want him to maintain the momentum until "self.y + 2*64" (he hits the ground)
                self.run_jump = False
            if self.run_jump == True:
                self.vx = -14
            
            if len(yeti_ice) != 0:   # yeti_ice is a list that holds all the ice tiles
                for tile in yeti_ice:
                    x1 = tile[0]   # starting point of the tile
                    x2 = x1 + 350  # starting point + the width of the ice tile image
                    y = tile[1]
                    if self.x + 75 > x1 and self.x + 55 < x2 and self.y + 128 == y:   # if yeti is on the tile then he has increased speed
                        self.vx = -14
                        if self.key_handler[UP] == True:
                            self.run_jump = True
                            break   # if he jumps while on ice tile, there is no need to iterate over all other tiles

        elif self.key_handler[RIGHT] == True:
            self.dir = RIGHT
            self.vx = 7
            
            if self.y + 2*64 == self.ground: # if yeti jumps while on ice tile, we want him to maintain the momentum until self.y + 2*64 (he hits the ground)
                self.run_jump = False
            if self.run_jump == True:
                self.vx = 14
            
            if len(yeti_ice) != 0:
                for tile in yeti_ice:
                    x1 = tile[0]
                    x2 = x1 + 350
                    y = tile[1]
                    if self.x + 75 > x1 and self.x + 55 < x2 and self.y + 128 == y:
                        self.vx = 14
                        if self.key_handler[UP] == True:
                            self.run_jump = True
                            break            
        else:
            self.vx = 0
          
          
        if self.key_handler[UP] == True and self.y + 2 * self.r == self.ground:      # jumping
            self.vy = -10

        if frameCount % 6 == 0:
            
            # because yeti did not have an adequate attack animation in the original sprite, we had to improvise. the attack ends on the second slice of the jump animation and starts on the third (see below)
            # but we wanted it to linger a bit on the first slice, just because it looks cooler. and frameCount % wasn't consistent on higher values, so we made our own count
            if self.action == "attack":
                if frameCount % 2 == 0: # THIS IS REDUNDANT, because if it's divisible by 6, it's also divisible by 2!
                    self.slice = (self.slice + 1) % self.slices
                    if self.slice == 2:
                        global count
                        if count != 6:
                            self.slice = 1
                            count = count+1

            # THIS PART IS NOT REDUNDANT. it might seem like it is, but if you do this the attack animation is going to speed up way too much. There might be a way to go around this
            elif self.vx != 0 and self.vy == 0:
                self.slice = (self.slice + 1) % self.slices
            elif self.vx == 0:
                self.slice = (self.slice + 1) % self.slices
        
        if self.alive:
            # allow yeti to move only if the distance between them is less than the resolution width - 250
            if self.vx > 0 and (self.x - game.mage.x) < RESOLUTION_W - 128 - 250:
                self.x += self.vx
            elif self.x > 0 and self.vx < 0 and (game.mage.x - self.x) < RESOLUTION_W - 128 - 250:
                self.x += self.vx
            
            self.y += self.vy
            
            if len(game.objects) != 0:    # game.objects is a list of all the objects in the game. this check prevents characters from moving through an unpassable object until they destroy it
                for obstacle in game.objects:
                    if self.y + self.img_h <= obstacle.y + 188 and self.dir == RIGHT and self.x + self.img_w - 30 >= obstacle.x and self.x + self.img_w - 30 <= obstacle.x + 20:
                        self.x = self.x - self.vx
        
    def get_action(self):
        temp = self.action
        
        if self.vy > 0:
            self.action = "jump down"
        elif self.vy < 0:
            self.action = "jump up"
            
        elif self.vx == -7 or self.vx == 7:
            self.action = "walk"
            
        elif self.vx == -14 or self.vx == 14:
            self.action = "run"
        
        elif self.key_handler["attack"] == True and self.vx == 0: # if attack button is pressed
            if self.slice == 2 and self.action != "idle":         # if slice number reaches two, the animation ends
                self.key_handler["attack"] = False
                
                global count  # this is the count from above that helps make the first slice linger a bit more. But here, after the animation ends, it has to be brought back to one
                count = 1
            self.action = "attack"

        elif self.vx == 0:
            self.action = "idle"
    
        if self.alive == False:
            self.action = "dead"
        
        if self.action != temp:  #if there is a change in action, set the slice to start from 0, so it starts at the beggining of the animation
            if self.action == "attack":
                self.slice = 3   # unless the action is attack, in which case we want it to start from the thrid slice because it looks cooler.


    def ice(self):
        
        if self.action == "attack" and self.slice == 1:  # self.slice == 1 because we want the ice to appear after yeti stomps the ground, and that particular frame is the first slice
            
            if self.dir == RIGHT:
                x = self.x + 25
                y = self.y + 2*self.r
                return x, y

            elif self.dir == LEFT:
                x = self.x - 250
                y = self.y + 2*self.r
                return x, y
            
        return None
    
    
    def display(self):

        self.update()
        self.get_action()
        

        if self.ice() != None:
            # every tile is a list, where tile[0] = x, tile[1] = y, and tile[2] = cnt. the count is useful because we want the tile to linger a bit, but we don't want it to stay permanent.
            cnt = 0
            tile = list(self.ice())
            tile.append(cnt)
            
            if len(yeti_ice) != 0 and yeti_ice[-1][0] == tile[0] and yeti_ice[-1][1] == tile[1] and 0 == tile[2]:  # there is a more elegant solution here probably, but this works
                pass
                
            else:
                yeti_ice.append(tile)   # yeti_ice is now a two-dimensional list. yeti_ice holds all tiles (so that the player can place multiple tiles at once)
        
        if len(yeti_ice) != 0:
            for tile in yeti_ice:
                tile[2] = tile[2] + 1   # incrementing count, i.e. how long the tile is going to stay. Display is called 60 times a second in draw, so number of count divided by 60 gives how many seconds the tile is going to appear for
                if tile[2] > 480:
                    yeti_ice.remove(tile)
                else:
                    image(game.ice_img, tile[0] - game.x_shift, tile[1], 350, 35)
            
        if self.action == "dead":
            image(self.img, self.x - game.x_shift, self.y + 3, self.img_w, self.img_h, 64, 256, 128, 320)
            game.game_over = True
        elif self.action == "walk":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y, self.img_w, self.img_h, self.slice * 64, 64, (self.slice + 1) * 64, 64*2)
            else:
                image(self.img, self.x - game.x_shift, self.y, self.img_w, self.img_h, (self.slice + 1) * 64, 64, self.slice * 64, 64*2)
    
        elif self.action == "run":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y, self.img_w, self.img_h, self.slice * 64, 64*2, (self.slice + 1) * 64, 64*3)
            else:
                image(self.img, self.x - game.x_shift, self.y, self.img_w, self.img_h, (self.slice + 1) * 64, 64*2, self.slice * 64, 64*3)
                
       
                 
        elif self.action == "idle":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, self.slice * 64, 0, (self.slice + 1) * 64, 64)
            elif self.dir == LEFT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice +1) * 64, 0, self.slice * 64, 64)
        elif self.action == "jump down":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 320, 192, 384, 256) 
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 384, 192, 320, 256)
        elif self.action == "jump up":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 256, 192, 320, 256) 
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 320, 192, 256, 256)
        elif self.action == "attack":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, self.slice * 64, 64*3, (self.slice + 1) * 64, 64*4)
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h , (self.slice + 1) * 64, 64*3, self.slice * 64, 64*4)


class Mage(Character):
    
    def __init__(self, x, y, r, img, img_w, img_h, slices):
        Character.__init__(self, x, y, r, img, img_w, img_h, slices)
        self.key_handler = {"A":False, "D":False, "W":False, "attack":False}
        self.alive = True
        self.slice = 0
        self.action = "idle"
        self.action_handler = {"idle":14, "walk":6, "run":8, "attack":7, "hit":4, "jump down":2, "jump up":2, "dead":9}   # bcs each animation doesn't have the same number of frames 
        # form - {"action" : number of slices}
        
        self.death_img = loadImage(path + "/images/mage_death.png")
        
        # FIRE attributes
        self.fire_img = loadImage(path + "/images/fire.png")
        self.fire_slice = 0
        self.fire_exist = False
        self.fire_x = 0
        self.fire_y = 0
        self.fire_x_original = 0
        self.fire_dir = None
        self.fire_collision = False
        self.shuffle_count = 0
        self.update_hit_count = False
        
    def update(self):
        self.gravity()
       
        if self.key_handler["A"] == True:
            self.vx = -7
            self.dir = LEFT
        elif self.key_handler["D"] == True:
            self.vx = 7
            self.dir = RIGHT
        else:
            self.vx = 0
          
        if self.key_handler["W"] == True and self.y + 2 * self.r == self.ground:
            self.vy = -10
            #self.jump_sound.rewind()
            #self.jump_sound.play()

        if frameCount % 5 == 0:
            self.slice = (self.slice + 1) % self.action_handler[self.action]

        if self.alive:
            # allow mage to move only if the distance between them is less than the resolution width - 250
            if self.vx > 0 and (self.x - game.yeti.x) < RESOLUTION_W - 128 - 250:
                self.x += self.vx
            elif self.x > 0 and self.vx < 0 and (game.yeti.x - self.x) < RESOLUTION_W - 128 - 250:
                self.x += self.vx
            
            self.y += self.vy
            
            if len(game.objects) != 0:
                for obstacle in game.objects:
                    if self.y + self.img_h - 10 <= obstacle.y + 188 and self.dir == RIGHT and self.x + self.img_w - 55 >= obstacle.x and self.x + self.img_w - 55 <= obstacle.x + 20:
                        self.x = self.x - self.vx
    
                
    def get_action(self):
        
        temp = self.action
        
        if self.vy > 0:
            self.action = "jump down"
        elif self.vy < 0:
            self.action = "jump up"
            
        elif self.key_handler["attack"] == True and self.vx == 0: # if attack button pressed
            if self.slice == 6 and self.action != "idle":
                    self.key_handler["attack"] = False
            self.action = "attack"
            
        elif self.vx != 0:
            self.action = "walk"
        elif self.vx == 0:
            self.action = "idle"
    
        if self.alive == False:
            self.action = "dead"
            self.vx = 0
            self.vy = 0
            
        if self.action != temp:  #if there is a change in action, set the slice to start from 0
            self.slice = 0    
    
    def display_fire(self):
        
        if (self.fire_x - self.fire_x_original) % 20 == 0:
            if self.fire_collision and self.shuffle_count < 7:
                self.shuffle_count = 7
            #do shuffle 5 times between slice 1 and 3
            if self.shuffle_count < 7: # shuffle 5 times
                self.fire_slice = (self.fire_slice + 1) % 3
                if self.fire_slice == 0:
                    self.shuffle_count += 1
            elif self.shuffle_count == 7:
                self.fire_slice = 4
                self.shuffle_count += 1
            else:
                self.fire_slice = self.fire_slice + 1
                
            
        if self.fire_slice == 8:
            self.fire_exist = False
            self.fire_collision = False
            self.update_hit_count = False
        
        if self.fire_dir == RIGHT:
            image(self.fire_img, self.fire_x - game.x_shift , self.fire_y , 48, 48, self.fire_slice * 32, 0, (self.fire_slice + 1) * 32, 32)
            if self.shuffle_count < 7:
                self.fire_x = self.fire_x + 10
        elif self.fire_dir == LEFT:
            image(self.fire_img, self.fire_x - game.x_shift, self.fire_y , 48, 48, (self.fire_slice + 1) * 32, 0, self.fire_slice * 32, 32)
            if self.shuffle_count < 7:
                self.fire_x = self.fire_x - 10
        
        
    def display(self):
        
        self.update()
        self.get_action()    
        
        if self.action == "attack" and self.slice == 5:
            self.fire_exist = True
            self.fire_slice = 0
            self.shuffle_count = 0
            if self.dir == RIGHT:
                self.fire_x_original = self.x + 128
                self.fire_dir = RIGHT
            elif self.dir == LEFT:
                self.fire_x_original = self.x - 50
                self.fire_dir = LEFT
            self.fire_x = self.fire_x_original
            self.fire_y = self.y + 48
            self.display_fire()
        elif self.fire_exist == True:
            self.display_fire()
        
        if self.action == "dead":
            image(self.death_img, self.x - game.x_shift, self.y + 35, self.img_w, self.img_h, self.slice * self.img_w, 0, (self.slice +1) * self.img_w, 128)
            if self.slice == 8:
                game.game_over = True
        
        elif self.action == "jump down":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 512+34, 512, 640+34, 640) 
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 640+34, 512, 512+34, 640)
                
        elif self.action == "jump up":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 256+34, 512, 384+34, 640) 
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, 384+34, 512, 256+34, 640)
                
        elif self.action == "attack":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice * self.img_w) + 34, self.img_h*3, (self.slice + 1) * self.img_w + 34, self.img_h*4)
            else:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice + 1) * self.img_w + 34, self.img_h*3, (self.slice * self.img_w) + 34, self.img_h*4)
        
        elif self.action == "walk":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice * self.img_w) + 34, self.img_h, (self.slice + 1) * self.img_w + 34, self.img_h*2)
            elif self.dir == LEFT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice + 1) * self.img_w + 34, self.img_h, (self.slice * self.img_w) + 34, self.img_h*2)
        
        elif self.action == "idle":
            if self.dir == RIGHT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice * self.img_w) + 34, 0, (self.slice + 1) * self.img_w + 34, self.img_h)
            elif self.dir == LEFT:
                image(self.img, self.x - game.x_shift, self.y , self.img_w, self.img_h, (self.slice + 1) * self.img_w + 34, 0, (self.slice * self.img_w) + 34, self.img_h)                


# class mainly for collision detection. other assets in the game inherit from this class:
class Object:
    
    def __init__(self,x, y, w, h, img, hit_count = None, hit_limit = None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = img
        self.hit_count = hit_count
        self.hit_limit = hit_limit
        
    def check_collision(self, other_x, other_y, other_w, other_h):
        if abs((self.x + self.w/2) - (other_x + other_w/2)) < self.w/2 + other_w/2  and abs((self.y + self.h/2) - (other_y + other_h/2)) < self.h/2 + other_h/2:
            return True
        else:
            return False
        
    def display(self):
        image(self.img,self.x - game.x_shift, self.y, self.w, self.h)
        
    def check_hit_limit(self):
        if self.hit_count == None or self.hit_count != self.hit_limit:
            return False
        else:
            return True
        

class Platform(Object):
    def __init__(self,x,y,middle = 1):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        
        self.m = middle
        self.tile_img = loadImage(path + "/images/tiles.png")
        self.w = 56 + self.m*78 + 60
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
    def display(self):
        self.update()
        
        image(self.tile_img, self.x - game.x_shift,self.y,56,64,128,32,156,64)
        for i in range(self.m):
            image(self.tile_img,self.x + 56 + i*78 - game.x_shift,self.y,78,64,158,32,194,64)
        image(self.tile_img,self.x + 56 + self.m*78 - game.x_shift,self.y,60,64, 194,32,224,64)


class Button:
    
    def __init__(self, x, y, elevator_number):
            self.x = x
            self.y = y
            self.number = elevator_number
            self.img = loadImage(path + "/images/button.png")
            self.pressed = False
            
    def press_check(self):
        
        if game.yeti.y + game.yeti.img_h == self.y + 23 and game.yeti.x + game.yeti.img_w - 30 >= self.x and game.yeti.x + game.yeti.img_w - 30 <= self.x + 130:
            
            self.pressed = True
            
            if self.number == 1:
                game.platforms[2].vy = -3
                if game.platforms[2].y < 170:
                    game.platforms[2].vy = 0
                    
                if game.mage.x + 75 > game.platforms[2].x and game.mage.x + game.mage.r < game.platforms[2].x + game.platforms[2].w and game.mage.y + game.mage.r*2 == game.platforms[2].y + 3:
                    game.mage.y += -3
                    
                mage_feet = game.mage.y + game.mage.r*2
                elevator_y = game.platforms[2].y
                
                
                if elevator_y < mage_feet and mage_feet < elevator_y + 3 and game.mage.x + 75 > game.platforms[2].x and game.mage.x + game.mage.r < game.platforms[2].x + game.platforms[2].w:
                    game.mage.y = (elevator_y) - game.mage.r*2

            elif self.number == 2:
                game.platforms[5].vx = -3
                if game.platforms[5].x < 2850:
                    game.platforms[5].vx = 0
                
                    
                    
                    
        elif game.mage.y + game.mage.img_h - 18 == self.y + 23 and game.mage.x + game.mage.img_w - 55 >= self.x and game.mage.x + game.mage.img_w - 55 <= self.x + 95:
            
            self.pressed = True
            if self.number == 1:
                game.platforms[2].vy = -3
                if game.platforms[2].y < 170:
                    game.platforms[2].vy = 0
                    
                if game.yeti.x + 75> game.platforms[2].x and game.yeti.x + game.yeti.r < game.platforms[2].x + game.platforms[2].w and game.yeti.y + game.yeti.r*2 == game.platforms[2].y + 3:
                    game.yeti.y += -3
                    
                yeti_feet = game.yeti.y + game.yeti.r*2
                elevator_y = game.platforms[2].y
                
                if elevator_y < yeti_feet and yeti_feet < elevator_y + 3 and game.yeti.x + 75 > game.platforms[2].x and game.yeti.x + game.yeti.r < game.platforms[2].x + game.platforms[2].w:
                    game.yeti.y = (elevator_y) - game.yeti.r*2
        
        else:
            
            self.pressed = False
            for button in game.buttons:
                if button.pressed == True:
                    return
                            
            if self.number == 1:
                game.platforms[2].vy = 3
                
                if game.platforms[2].y > 510:
                    game.platforms[2].vy = 0
                
                if game.mage.x + 75 > game.platforms[2].x and game.mage.x + game.mage.r < game.platforms[2].x + game.platforms[2].w and game.mage.y + game.mage.r*2 == game.platforms[2].y - game.platforms[2].vy  and  game.platforms[2].vy == 3:
                    game.mage.y += 3
                
                if game.yeti.x + 75 > game.platforms[2].x and game.yeti.x + game.yeti.r < game.platforms[2].x + game.platforms[2].w and game.yeti.y + game.yeti.r*2 == game.platforms[2].y - game.platforms[2].vy  and  game.platforms[2].vy == 3:
                    game.yeti.y += 3
                    
            if game.platforms[5].x < 2850:
                game.platforms[5].vx = 0
    
    def display(self):
        
        self.press_check()
        if self.pressed == False:
            image(self.img, self.x - game.x_shift, self.y, 62, 23, 0, 2, 186, 70)
        
        elif self.pressed == True:
            image(self.img, self.x - game.x_shift, self.y, 62, 23, 186, 0, 374, 70)
    

class Game:
    
    def __init__(self):
        self.w = RESOLUTION_W
        self.h = RESOLUTION_H
        self.ground = GROUND
        self.game_over  = False
        self.win_game = False
        self.game_over_screen = loadImage(path + "/images/game_over.png")
        self.bg_music = player.loadFile(path + "/images/background.mp3")
        self.bg_music.loop()
        self.yeti = Yeti(50, 400, 64, "yeti.png", 128, 128, 8)
        self.mage = Mage(10, 50, 55, "mage.png", 128, 128, 14)
        self.button1 = Button(1360, 427, 1)
        self.button2 = Button(1980, 147, 1)
        self.button3 = Button(3420, 247, 2)
        self.buttons = [self.button1, self.button2, self.button3]
        
        self.lava = loadImage(path + "/images/lava.png")
        self.castle = loadImage(path + "/images/castle.png")
        
        self.x_shift = 0
        
        self.ice_block = loadImage(path + "/images/ice_block.png")
        self.ice_img = loadImage(path + "/images/ice.png")
        
        self.platforms = []
        self.platforms.append(Platform(0,200,7))
        self.platforms.append(Platform(1050,450,6))
        self.platforms.append(Platform(1685,510,1)) # this is elevator1
        self.platforms.append(Platform(1920,170,8))
        self.platforms.append(Platform(3235,270,8))
        self.platforms.append(Platform(3235, 270, 1)) # this is elevator2
        
        self.objects = []    
        self.objects.append(Object(360,22, 250, 188, self.ice_block, 0, 3))
        self.objects.append(Object(3680, 92, 250, 188, self.ice_block, 0, 3))
        
        self.bg_images = []
        for i in range(5, 0, -1):
            self.bg_images.append(loadImage(path + "/images/layer_0" + str(i) + ".png"))
        
    def display(self):
        
        global start_screen
        if self.game_over == True:
            time.sleep(0.9)
            image(self.game_over_screen, 0, 0)
            fill(186, 54, 51)
            textSize(35)
            text("click anywhere to restart", 420, 500)
            self.bg_music.close()
            return
        elif self.win_game == True:
            time.sleep(0.9)
            image(start_screen, 0, 0, RESOLUTION_W, RESOLUTION_H)
            fill(200, 260, 0)
            textSize(60)
            text("CONGRAGULATIONS!", 330, 370)
            textSize(20)
            text("click anywhere to play again", 485, 540)
            self.bg_music.close()
            return

            
        x_shift = self.x_shift
        cnt = 0
        for bg_image in self.bg_images:
            if cnt == 0:
                x_shift = self.x_shift//3
            elif cnt == 1:
                x_shift = self.x_shift//2
            else:
                x_shift = self.x_shift
            
            width_right = x_shift % RESOLUTION_W
            width_left = RESOLUTION_W - width_right
            
            image(bg_image, 0, 0, width_left, RESOLUTION_H, width_right, 0, RESOLUTION_W, RESOLUTION_H)
            image(bg_image, width_left, 0, width_right, RESOLUTION_H, 0, 0, width_right, RESOLUTION_H)    
            
            cnt += 1
        
        for platform in self.platforms:
            platform.display()
                
        for object in self.objects:
            if not object.check_hit_limit():
                object.display()
            else:
                self.objects.remove(object)
                

        #if hit_limit reached, remove object from the list
        self.fire_x = 0
        self.fire_y = 0
        if self.mage.fire_exist == True:
            for object in self.objects:
                if object.check_collision(self.mage.fire_x, self.mage.fire_y, 48, 48):
                    self.mage.fire_collision = True
                    if self.mage.update_hit_count == False: 
                        object.hit_count += 1
                        self.mage.update_hit_count = True
                        
        self.mage_x_shift = self.mage.x  - 250
        self.yeti.x_shift = self.yeti.x  - 250
        
        self.x_shift = max(0, min(self.mage_x_shift, self.yeti.x_shift))                
        
        self.button1.display()
        self.button2.display()
        self.button3.display()
        
        image(self.castle, 4950 - self.x_shift, 230, 420, 391)
        
        self.mage.display()
        self.yeti.display()
        
        if (self.yeti.x > 1627 and self.yeti.x < 4310) and self.yeti.y + self.yeti.img_h > 585:
            self.yeti.alive = False    
        if (self.mage.x > 1627 and self.mage.x < 4310) and self.mage.y + self.mage.img_h > 585:
            self.mage.alive = False
        
        image(self.lava, 1690 - self.x_shift, 585) # make the lava longer. and change above code accordingly!
        image(self.lava, 2581 - self.x_shift, 585)
        image(self.lava, 2581+890 - self.x_shift, 585, 892, 130, 0, 0, 475, 130)
        
        if self.mage.x > 5090 and self.yeti.x > 5090:
            self.win_game = True
        
        
def keyPressed():
    
    global game_start
    if keyCode == 10:
        game_start = True

    
    # YETI
    if keyCode == LEFT and game.yeti.action != "attack":
        game.yeti.key_handler[LEFT] = True
    elif keyCode == RIGHT and game.yeti.action != "attack":
        game.yeti.key_handler[RIGHT] = True
    elif keyCode == UP and game.yeti.action != "attack":
        game.yeti.key_handler[UP] = True
    elif keyCode == 76:
        if game.yeti.action == "idle":
            game.yeti.key_handler["attack"] = True
    
    # MAGE
    elif keyCode == 65 and game.mage.action != "attack": # the game.mage.action makes it s. t. the character can't stop the animation of attack just by moving, the attack animation has to finish first
        game.mage.key_handler["A"] = True
    elif keyCode == 68 and game.mage.action != "attack": # but maybe this check would be more efficient if done somewhere else, this is to be investigated @AYYUB
        game.mage.key_handler["D"] = True
    elif keyCode == 87 and game.mage.action != "attack": # same should be done for yeti. but first, i want you to verify it.
        game.mage.key_handler["W"] = True
    elif keyCode == 82: # attack button (r) pressed!
        if game.mage.action == "idle" and game.mage.fire_exist == False:
            game.mage.key_handler["attack"] = True
        
        
        
def keyReleased():
    # YETI
    if keyCode == LEFT:
        game.yeti.key_handler[LEFT] = False
    elif keyCode == RIGHT:
        game.yeti.key_handler[RIGHT] = False
    elif keyCode == UP:
        game.yeti.key_handler[UP] = False
    
    # MAGE
    elif keyCode == 65:
        game.mage.key_handler["A"] = False
    elif keyCode == 68:
        game.mage.key_handler["D"] = False
    elif keyCode == 87:
        game.mage.key_handler["W"] = False
        
        
def setup():
    size(RESOLUTION_W, RESOLUTION_H)
    background(255,255,255)
    
def draw():
    
    global game_start, start_screen  
    if game_start == False:
        image(start_screen, 0, 0, RESOLUTION_W, RESOLUTION_H)
        fill(190, 250, 0)
        textSize(60)
        text("Yeti and Mage: a two player puzzle game", 35, 195)
        textSize(40)
        fill(200, 260, 0)
        text("Mage movement: WASD", 20, 320)
        text("Mage attack: r", 20, 370)
        text("Yeti movement: arrow keys", 610, 300)
        text("Yeti attack: l", 610, 350)
        text("(hint: Yeti is faster on ice block)", 610, 400)
        fill(39, 200, 20)
        textSize(50)
        text("press ENTER to start", 340, 550)
    else:
        game.display()

yeti_ice = []
count = 1
game_start = False
start_screen = loadImage(path + "/images/start_screen.png")
game = Game()

def mouseClicked():
    global game
    if game.yeti.alive == False or game.mage.alive == False or game.win_game == True:
        game = Game()
