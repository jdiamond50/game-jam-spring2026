import pygame
import random

class Ship(pygame.sprite.Sprite): 
    def __init__(self, y_val):
        super().__init__() 
        image = pygame.image.load('ship.png') 
        self.image = pygame.transform.scale(image, (50, 50)) 
        self.rect = self.image.get_rect() # gets rect = (x,y,width,height)
        self.rect.topright = (0,y_val)
    
    def update(self):
        self.rect.x += 1
        if self.rect.left > WIDTH: # remove offscreen ships
            self.kill()

ships = pygame.sprite.Group()

pygame.init()

# create screen

WIDTH = 400
HEIGHT = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# time stuff
clock = pygame.time.Clock()
framerate = 60
next_ship_time = random.randint(framerate, 2*framerate) # [1 second, 2 seconds]

run = True
while run:
    clock.tick(framerate)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            run = False
    
    if (next_ship_time == 0): # time to create another ship
        new_ship = Ship(random.randint(0, HEIGHT-50))
        ships.add(new_ship)
        next_ship_time = random.randint(60,120) # set countdown for next ship

    next_ship_time -= 1

    ships.update() # move ships to the right

    # draw stuff

    screen.fill((0, 157, 255)) # light blue
    ships.draw(screen)

    pygame.display.flip() # update screen

pygame.quit()