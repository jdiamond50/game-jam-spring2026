import pygame
import random

class Ship(pygame.sprite.Sprite):
    def __init__(self, y_val):
        super().__init__()
        image = pygame.image.load('ship.png')
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.topleft = (0,y_val)
    
    def update(self):
        self.rect.x += 1

# time stuff

pygame.init()
clock = pygame.time.Clock()
framerate = 60
next_ship_time = random.randint(60, 120)

WIDTH = 400
HEIGHT = 300

screen = pygame.display.set_mode((WIDTH, HEIGHT))
ships = pygame.sprite.Group()

run = True
while run:
    clock.tick(framerate)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # update stuff (mathematically)
    
    if (next_ship_time == 0):
        new_ship = Ship(random.randint(0, HEIGHT-50))
        ships.add(new_ship)
        next_ship_time = random.randint(60,120)
    next_ship_time -= 1

    prev_time = pygame.time.get_ticks()

    ships.update()

    # draw stuff

    screen.fill((0, 157, 255))
    ships.draw(screen)

    pygame.display.flip()

pygame.quit()