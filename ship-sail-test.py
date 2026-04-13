import pygame
import random
import math

display_dist = 20

def update_rect(sprite): 
    # image scaling
    scale_factor = display_dist / sprite.pos.magnitude()
    display_size = sprite.size * scale_factor
    sprite.image = pygame.transform.scale(sprite.original_image, (display_size, display_size))

    # location on screen
    lr_display_pos = math.atan(sprite.pos.x / sprite.pos.y) * (WIDTH / WIDTH_ANGLE) + (WIDTH / 2)
    ud_display_pos = math.atan(sprite.pos.z / math.sqrt(sprite.pos.x ** 2 + sprite.pos.y ** 2)) * (HEIGHT / HEIGHT_ANGLE) * (-1) + (HEIGHT / 2)
    sprite.rect = sprite.image.get_rect(center=(lr_display_pos, ud_display_pos))

class Ship(pygame.sprite.Sprite): # (x,y,z) = (left/right, near/far, up/down)

    def __init__(self, y_val):
        super().__init__() 
        self.original_image = pygame.image.load('ship.png') 
        self.size = 750
        self.pos = pygame.math.Vector3(-2*y_val, y_val, 0) 
        self.vel = pygame.math.Vector3(1,0,0)
        update_rect(self)
    
    def update(self):
        self.pos += self.vel
        update_rect(self)
        if self.pos.x > 70: # pause island ships
            self.vel = pygame.math.Vector3(0,0,0)
            
            

ships = pygame.sprite.Group()

pygame.init()

CANNON_FIRED_EVENT = pygame.event.custom_type()

TITLE_EVENT = pygame.event.custom_type()
GAME_OVER_EVENT = pygame.event.custom_type()
LEVEL_SELECT_EVENT = pygame.event.custom_type()

# create screen

WIDTH = 1920
WIDTH_ANGLE = 2*math.pi/3 # 120 degrees
HEIGHT = 1080 
HEIGHT_ANGLE = math.pi/2 # 90 degrees
screen = pygame.display.set_mode((WIDTH, HEIGHT))

sky_color = (0, 157, 255) # light blue
water_color = (2, 71, 181) # dark blue
island_color = (6, 64, 43) # dark green
damage_color = (179, 27, 27) # red
border_color = (0, 0, 0) # balck

# time stuff
clock = pygame.time.Clock()
framerate = 60
next_ship_time = random.randint(1*framerate, 2*framerate) # [1 second, 2 seconds]

second = -1
red_island = False # If the island is taking damage this tick
island_health = 50 # The island starting health

run = True
while run:
    clock.tick(framerate)
    second+=1
    if second >= 60:
        second = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.event.post(pygame.event.Event(CANNON_FIRED_EVENT))
        if event.type == CANNON_FIRED_EVENT:
            print("cannon_fired")
    
    if (next_ship_time == 0): # time to create another ship
        new_ship = Ship(random.randint(50,300))
        ships.add(new_ship)
        next_ship_time = random.randint(60,120) # set countdown for next ship

    for ship in ships: # damages the island if a ship has 0 velocity
        if ship.vel == pygame.math.Vector3(0,0,0) and second == 0:
            red_island = True
            island_health -=1
        elif second >= 5:
            red_island = False

    next_ship_time -= 1

    ships.update() # move ships to the right

    # draw stuff

    pygame.draw.rect(screen, sky_color, (0,0,WIDTH, HEIGHT/2))
    pygame.draw.rect(screen, water_color, (0,HEIGHT/2,WIDTH, HEIGHT/2))

    pygame.draw.rect(screen, border_color, ((WIDTH-(WIDTH/3))-2,(HEIGHT/5)-2,(50*(WIDTH/200))+4, (HEIGHT/30)+4))

    if red_island == True: # draws island red or green
        pygame.draw.polygon(screen, damage_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2], [WIDTH, 4*HEIGHT/7], [WIDTH, 3*HEIGHT/7]])
        pygame.draw.rect(screen, damage_color, (WIDTH-(WIDTH/3),HEIGHT/5,island_health*(WIDTH/200), HEIGHT/30))
    else:
        pygame.draw.polygon(screen, island_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2], [WIDTH, 4*HEIGHT/7], [WIDTH, 3*HEIGHT/7]])
        pygame.draw.rect(screen, island_color, (WIDTH-(WIDTH/3),HEIGHT/5,island_health*(WIDTH/200), HEIGHT/30))

    ships.draw(screen)

    pygame.display.flip() # update screen

pygame.quit()
