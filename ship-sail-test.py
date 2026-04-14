import pygame
import random
import math

display_dist = 20

WIDTH = 1920
WIDTH_ANGLE = 2*math.pi/3 # 120 degrees
HEIGHT = 1080 
HEIGHT_ANGLE = math.pi/2 # 90 degrees

def update_rect(sprite): 
    # image scaling
    scale_factor = display_dist / sprite.pos.magnitude()
    display_size = sprite.size * scale_factor
    sprite.image = pygame.transform.scale(sprite.original_image, (display_size, display_size))

    # location on screen
    lr_display_pos = math.atan(sprite.pos.x / sprite.pos.y) * (WIDTH / WIDTH_ANGLE) + (WIDTH / 2)
    ud_display_pos = math.atan(sprite.pos.z / math.sqrt(sprite.pos.x ** 2 + sprite.pos.y ** 2)) * (HEIGHT / HEIGHT_ANGLE) * (-1) + (HEIGHT / 2)
    sprite.rect = sprite.image.get_rect(center=(lr_display_pos, ud_display_pos))

class Cannon(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('cannon.png'), (400,400))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect(center=(WIDTH/2, HEIGHT - 200))
        self.ud_angle = math.pi / 4
        self.lr_angle = 0

class Cannonball(pygame.sprite.Sprite):

    def __init__(self, cannon):
        super().__init__()
        self.original_image = pygame.image.load('cannonball.jpg')
        self.size = 100
        self.pos = pygame.math.Vector3(0,20,-20) # changed from (0,1,-40)
        init_velocity = 13
        self.vel = pygame.math.Vector3(
            init_velocity*math.cos(cannon.ud_angle)*math.sin(cannon.lr_angle),
            init_velocity*math.cos(cannon.ud_angle)*math.cos(cannon.lr_angle), 
            init_velocity*math.sin(cannon.ud_angle)
        )
        self.acc = pygame.math.Vector3(0,0,-0.5)
        self.fired = False
        update_rect(self)
    
    def update(self):
        self.pos += self.vel
        self.vel += self.acc
        # print("cannonball pos: ", self.pos)
        if self.pos.z >= 0: 
            self.fired = True
        update_rect(self)
        if self.pos.z < 0 and self.fired: # cannonball hits the water
            pygame.mixer.Sound.play(sound_miss)
            self.kill()

class Ship(pygame.sprite.Sprite): # (x,y,z) = (left/right, near/far, up/down)

    def __init__(self, y_val):
        super().__init__() 
        self.original_image = pygame.image.load('ship.png') 
        self.size = 750
        self.pos = pygame.math.Vector3(-2*y_val, y_val, 0) 
        self.vel = pygame.math.Vector3(1,0,0)
        update_rect(self)
    
    def update(self, curr_time, game_time):
        self.pos += self.vel
        update_rect(self)
        if self.pos.x > 70 and curr_time < game_time: # pause island ships
            self.vel = pygame.math.Vector3(0,0,0)      
        if self.pos.x < -2*self.pos.y: 
            self.kill()

pygame.init()

#sound and audio files

sound_hit = pygame.mixer.Sound("hit.wav")
sound_fire = pygame.mixer.Sound("cannon_fire.wav")
sound_miss = pygame.mixer.Sound("splash.wav")
sound_island_hurt = pygame.mixer.Sound("smash.wav")

# events

CANNON_FIRED_EVENT = pygame.event.custom_type()
SHIP_HIT = pygame.event.custom_type()
NIGHTFALL = pygame.event.custom_type()

TITLE_EVENT = pygame.event.custom_type()
GAME_OVER_EVENT = pygame.event.custom_type()
LEVEL_SELECT_EVENT = pygame.event.custom_type()

# create screen

screen = pygame.display.set_mode((WIDTH, HEIGHT))

day_sky_color = (0, 157, 255)
night_sky_color = (0, 0, 80)
day_water_color = (2, 71, 181)
night_water_color = (0, 2, 44)
island_color = (6, 64, 43) # dark green
damage_color = (179, 27, 27) # red
border_color = (0, 0, 0) # balck

# time stuff
clock = pygame.time.Clock()
framerate = 60

def get_color_gradient(start_color, end_color, parameter):
    # returns the color that is 0 <= parameter 1 <= of the way between start_color and end_color
    return (
        end_color[0] * parameter + start_color[0] * (1 - parameter),
        end_color[1] * parameter + start_color[1] * (1 - parameter),
        end_color[2] * parameter + start_color[2] * (1 - parameter)
    )

TITLE_SCREEN = 0
GAMEPLAY_SCREEN = 1
GAME_OVER_SCREEN = 2

run = True
game_state = TITLE_SCREEN

def title_loop():
    global run, game_state

    PLAY = 0
    QUIT = 1
    current_button_selected = PLAY

    on_title_screen = True
    while on_title_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_title_screen = False
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_button_selected == PLAY:
                        print("play button pressed")
                        game_state = GAMEPLAY_SCREEN
                        on_title_screen = False
                    elif current_button_selected == QUIT:
                        print("quit button pressed")
                        pygame.event.post(pygame.event.Event(pygame.QUIT)) 
                elif event.key == pygame.K_DOWN:
                    current_button_selected = QUIT
                    print("quit button selected")
                elif event.key == pygame.K_UP:
                    current_button_selected = PLAY
                    print("play button selected")
    
        # draw stuff

        pygame.draw.rect(screen, day_water_color, (0,0,WIDTH, HEIGHT)) # background

        # -- draw buttons -- 
        
        # highlight currently selected button
        if current_button_selected == PLAY:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2-255, 810, 210)) # play button highlight
        if current_button_selected == QUIT:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2+95, 810, 210)) # quit button highlight

        # button background
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2-250, 800, 200)) # play button
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200)) # quit button

        # button text
        font = pygame.font.Font('PirateJack-lglRX.otf',175) # Pirate Jack by font by Tigade Std
        play_text = font.render('PLAY', True, (255, 215, 0))
        quit_text = font.render('QUIT', True, (255, 215, 0))
        screen.blit(play_text,play_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
        screen.blit(quit_text,quit_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))

        pygame.display.flip() # update screen

def gameplay_loop():
    global run, game_state

    ships = pygame.sprite.LayeredUpdates()
    cannonballs = pygame.sprite.Group()
    cannon = Cannon()   

    on_gameplay_screen = True

    next_ship_time = random.randint(1*framerate, 2*framerate) # [1 second, 2 seconds]

    curr_time = -1 # measured in num frames
    game_time = 60*framerate # total length of the level
    is_red_island = False # If the island is taking damage this tick
    island_health = 50 # The island starting health
    previous_island_health = island_health # A variable for tracking if the island lost any health in a tick

    
    while on_gameplay_screen:
        clock.tick(framerate)

        curr_time+=1

        if curr_time == game_time: pygame.event.post(pygame.event.Event(NIGHTFALL))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False
                on_gameplay_screen = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    pygame.event.post(pygame.event.Event(CANNON_FIRED_EVENT))
            if event.type == NIGHTFALL:
                for ship in ships:
                    ship.vel = (-0.5,0,0)
                    ship.original_image = pygame.transform.flip(ship.original_image, True, False)
            if event.type == CANNON_FIRED_EVENT:
                pygame.mixer.Sound.play(sound_fire)
                new_cannonball = Cannonball(cannon)
                cannonballs.add(new_cannonball)
            if event.type == SHIP_HIT:
                pygame.mixer.Sound.play(sound_hit)
                event.cannonball.kill()
                event.ship.kill()

        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and cannon.ud_angle < math.pi / 4:
            cannon.ud_angle += math.pi / 180
            # print("cannon ud_angle adjusted to ", cannon.ud_angle)
        # if keys[pygame.K_DOWN] and cannon.ud_angle > 0.5:
        if keys[pygame.K_DOWN] and cannon.ud_angle > 0.35:
            cannon.ud_angle -= math.pi / 180
            # print("cannon ud_angle adjusted to ", cannon.ud_angle)
        if keys[pygame.K_LEFT] and cannon.lr_angle > -0.95:
            cannon.lr_angle -= math.pi / 180
            # print("cannon lr_angle adjusted to ", cannon.lr_angle)
        if keys[pygame.K_RIGHT] and cannon.lr_angle < 0.95:
            cannon.lr_angle += math.pi / 180
            # print("cannon lr_angle adjusted to ", cannon.lr_angle)
        
        if (next_ship_time == 0 and curr_time < game_time): # time to create another ship
            y_dist = random.randint(50,300)
            new_ship = Ship(y_dist)
            ships.add(new_ship, layer=-y_dist)
            next_ship_time = random.randint(60,120) # set countdown for next ship

        next_ship_time -= 1

        ships.update(curr_time, game_time)
        cannonballs.update()

        for ship in ships:
            # island damage if ship has zero velocity
            if ship.vel == pygame.math.Vector3(0,0,0) and curr_time % 60 == 0:
                is_red_island = True
                island_health -=1
            elif curr_time % 60 >= 5:
                is_red_island = False

            # ship hit
            for cannonball in cannonballs:
                diff_vec = cannonball.pos - ship.pos
                if (diff_vec.magnitude() < 20):
                    ship_hit_data = {"cannonball": cannonball, "ship": ship}
                    pygame.event.post(pygame.event.Event(SHIP_HIT, ship_hit_data))

        if previous_island_health != island_health:
            pygame.mixer.Sound.play(sound_island_hurt)
            previous_island_health = island_health

        if island_health <= 0 or curr_time >= game_time:
            on_gameplay_screen = False
            game_state = GAME_OVER_SCREEN

        # draw stuff

        curr_sky_color = night_sky_color
        curr_water_color = night_water_color
        if curr_time < game_time: 
            curr_sky_color = get_color_gradient(day_sky_color, night_sky_color, curr_time / game_time)
            curr_water_color = get_color_gradient(day_water_color, night_water_color, curr_time / game_time)
        pygame.draw.rect(screen, curr_sky_color, (0,0,WIDTH, HEIGHT/2))
        pygame.draw.rect(screen, curr_water_color, (0,HEIGHT/2,WIDTH, HEIGHT/2))

        pygame.draw.rect(screen, border_color, ((WIDTH-(WIDTH/3))-2,(HEIGHT/5)-2,(50*(WIDTH/200))+4, (HEIGHT/30)+4))

        if is_red_island: # draws island red or green
            pygame.draw.polygon(screen, damage_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2], [WIDTH, 4*HEIGHT/7], [WIDTH, 3*HEIGHT/7]])
            pygame.draw.rect(screen, damage_color, (WIDTH-(WIDTH/3),HEIGHT/5,island_health*(WIDTH/200), HEIGHT/30))
        else:
            pygame.draw.polygon(screen, island_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2], [WIDTH, 4*HEIGHT/7], [WIDTH, 3*HEIGHT/7]])
            pygame.draw.rect(screen, island_color, (WIDTH-(WIDTH/3),HEIGHT/5,island_health*(WIDTH/200), HEIGHT/30))

        ships.draw(screen)
        cannonballs.draw(screen)
        screen.blit(cannon.image, cannon.rect)

        pygame.display.flip() # update screen

def game_over_loop():
    global run, game_state

    PLAY_AGAIN = 0
    QUIT = 1
    current_button_selected = PLAY_AGAIN

    on_title_screen = True
    while on_title_screen:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_title_screen = False
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if current_button_selected == PLAY_AGAIN:
                        game_state = GAMEPLAY_SCREEN
                        on_title_screen = False
                    elif current_button_selected == QUIT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT)) 
                elif event.key == pygame.K_DOWN:
                    current_button_selected = QUIT
                elif event.key == pygame.K_UP:
                    current_button_selected = PLAY_AGAIN
    
        # draw stuff

        pygame.draw.rect(screen, day_water_color, (0,0,WIDTH, HEIGHT)) # background

        # -- draw buttons -- 
        
        # highlight currently selected button
        if current_button_selected == PLAY_AGAIN:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2-255, 810, 210)) # play again button highlight
        if current_button_selected == QUIT:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2+95, 810, 210)) # quit button highlight

        # button background
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2-250, 800, 200)) # play again button
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200)) # quit button

        # button text
        font = pygame.font.Font('PirateJack-lglRX.otf',175) # Pirate Jack by font by Tigade Std
        play_text = font.render('PLAY AGAIN', True, (255, 215, 0))
        quit_text = font.render('QUIT', True, (255, 215, 0))
        screen.blit(play_text,play_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
        screen.blit(quit_text,quit_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))

        pygame.display.flip() # update screen


while run:

    if (game_state == GAMEPLAY_SCREEN):
        gameplay_loop()
    elif (game_state == TITLE_SCREEN):
        title_loop()
    elif (game_state == GAME_OVER_SCREEN):
        game_over_loop()

pygame.quit()
