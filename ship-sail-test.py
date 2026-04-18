import pygame
import random
import math

display_dist = 20

WIDTH = 1920
WIDTH_ANGLE = 2*math.pi/3 # 120 degrees
HEIGHT = 1080 
HEIGHT_ANGLE = math.pi/2 # 90 degrees

pygame.init()
ships = pygame.sprite.Group()
active_sprites = pygame.sprite.LayeredUpdates() # contains ships and cannonballs

def update_rect(sprite): 
    # image scaling
    scale_factor = display_dist / sprite.pos.magnitude()
    display_size = sprite.size * scale_factor
    sprite.image = pygame.transform.scale(sprite.original_image, (display_size, display_size / sprite.aspect_ratio))

    # location on screen
    lr_display_pos = math.atan(sprite.pos.x / sprite.pos.y) * (WIDTH / WIDTH_ANGLE) + (WIDTH / 2)
    ud_display_pos = math.atan(sprite.pos.z / math.sqrt(sprite.pos.x ** 2 + sprite.pos.y ** 2)) * (HEIGHT / HEIGHT_ANGLE) * (-1) + (HEIGHT / 2)
    ship_rocking_adjust = 20*math.sin(curr_time / rocking_rate)
    sprite.rect = sprite.image.get_rect(center=(lr_display_pos, ud_display_pos + ship_rocking_adjust))

class Cannon(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load('sprites/cannon.png'), (400,400))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect(center=(WIDTH/2+15, HEIGHT - 200))
        self.ud_angle = math.pi / 4
        self.lr_angle = 0
        self.rect.top -= 50
    
    def update(self):
        row = int(16 * (self.ud_angle - 0.35) // (math.pi / 4 - 0.35))
        col = int(47 * (self.lr_angle + 0.95) // (0.95 + 0.95))
        if row < 0: row = 0
        if row > 16: row = 16
        if col < 0: col = 0
        if col > 47: col = 47
        # print(row, ", ", col)
        self.image = cannon_anim[row][col]
        self.image = pygame.transform.scale(self.image, (400,400))

class Cannonball(pygame.sprite.Sprite):

    def __init__(self, cannon):
        super().__init__()
        self.original_image = pygame.image.load('sprites/cannonball.jpg')
        rect = self.original_image.get_rect()
        self.aspect_ratio = rect.width / rect.height
        self.size = 100
        self.pos = pygame.math.Vector3(0,30,-10) # changed from (0,20,-20)
        init_velocity = 13
        ship_rocking_adjust_angle = 0.05*math.sin(curr_time / rocking_rate)
        self.vel = pygame.math.Vector3(
            init_velocity*math.cos(cannon.ud_angle+ship_rocking_adjust_angle)*math.sin(cannon.lr_angle),
            init_velocity*math.cos(cannon.ud_angle+ship_rocking_adjust_angle)*math.cos(cannon.lr_angle), 
            init_velocity*math.sin(cannon.ud_angle+ship_rocking_adjust_angle)
        )
        self.acc = pygame.math.Vector3(0,0,-0.5)
        self.fired = False
        update_rect(self)

    
    def update(self):
        self.pos += self.vel
        self.vel += self.acc
        active_sprites.change_layer(self, self.pos.y)
        # print("cannonball pos: ", self.pos)
        if self.pos.z >= 0: 
            self.fired = True
        update_rect(self)
        # if self.pos.y <= 40:
        #     self.image.set_alpha(0)
        # else:
        #     self.image.set_alpha(255)
        if self.pos.z < 0 and self.fired: # cannonball hits the water
            pygame.mixer.Sound.play(sound_miss)
            self.kill()

class Ship(pygame.sprite.Sprite): # (x,y,z) = (left/right, near/far, up/down)

    def __init__(self, y_val):
        super().__init__() 
        self.original_image = ship_sink_anim[0]
        self.size = 750
        rect = self.original_image.get_rect()
        self.aspect_ratio = rect.width / rect.height
        self.pos = pygame.math.Vector3(-2*y_val, y_val, 0) 
        self.vel = pygame.math.Vector3(1,0,0)
        self.sinking = False
        self.sinking_frame = -1
        update_rect(self)
    
    def update(self, curr_time, game_time):
        self.pos += self.vel
        if self.pos.x > 70 and (curr_time < game_time or game_state == GAME_OVER_SCREEN): # pause island ships
            self.vel = pygame.math.Vector3(0,0,0)
        if self.pos.x < -2*self.pos.y: 
            self.kill()
        if self.sinking:
            self.sinking_frame += 1
            if self.sinking_frame == ship_sink_anim_length: 
                self.kill()
                return
            self.original_image = ship_sink_anim[self.sinking_frame]
            rect = self.original_image.get_rect()
            self.aspect_ratio = rect.width / rect.height
        update_rect(self)

# sound effect audio files

sound_hit = pygame.mixer.Sound("sound_files/hit.wav")
sound_fire = pygame.mixer.Sound("sound_files/cannon_fire.wav")
sound_miss = pygame.mixer.Sound("sound_files/splash.wav")
sound_island_hurt = pygame.mixer.Sound("sound_files/smash.wav")
sound_select = 0 # sounds to still be added
sound_begin = 0
sound_lose_game = 0
sound_win_level = 0

sound_fire.set_volume(.6)
sound_miss.set_volume(.6)

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
NEXT_LEVEL_SCREEN = 3

load_open = 0 # variable for loading images on startup
cannon_anim = []
ship_sink_anim = []
ship_sink_anim_length = 60

rocking_rate = 50

current_level = 0
kill_count = 0

run = True
game_state = TITLE_SCREEN
curr_time = -1 # measured in num frames

def title_loop(button_delay):
    # this is probably too many global variables but if it works it works i guess
    global run, game_state, load_open, cannon_anim, ship_sink_anim, ship_sink_anim_length 

    PLAY = 0
    QUIT = 1
    current_button_selected = PLAY

    on_title_screen = True
    while on_title_screen:
        button_delay -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_title_screen = False
                run = False
            if event.type == pygame.KEYDOWN and button_delay <= 0:
                if event.key == pygame.K_SPACE:
                    if current_button_selected == PLAY:
                        game_state = GAMEPLAY_SCREEN
                        on_title_screen = False
                    elif current_button_selected == QUIT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT)) 
                elif event.key == pygame.K_DOWN:
                    current_button_selected = QUIT
                elif event.key == pygame.K_UP:
                    current_button_selected = PLAY
    
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
        
        if load_open == 0: # loading screen for loading the cannon images
            load_percent = 0
            loading_text = font.render('Loading', True, (255, 215, 0))
            screen.blit(loading_text,loading_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
            percent_text = font.render(str(int(load_percent*10000)/100)+'%', True, (255, 215, 0))
            screen.blit(percent_text,percent_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))
            pygame.display.flip()
            load_open += 1
            
            for i in range(ship_sink_anim_length):
                ship_sink_anim.append(pygame.image.load('ship_animation/ship' + str(i) + ".png"))
                
                load_percent += 1/(60+17)
                pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200))
                pygame.draw.rect(screen, island_color, (WIDTH/2-400, HEIGHT/2+100, 800*load_percent, 200))
                percent_text = font.render(str(int(load_percent*10000)/100)+'%', True, (255, 215, 0))
                screen.blit(percent_text,percent_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))
                pygame.display.flip()

            for i in range(17):
                cannon_anim.append([])
                dir_name = "cannon_anim/cannon_anim_" + str(i)
                ending = ".png"
                
                load_percent += 1/(60+17)
                pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200))
                pygame.draw.rect(screen, island_color, (WIDTH/2-400, HEIGHT/2+100, 800*load_percent, 200))
                percent_text = font.render(str(int(load_percent*10000)/100)+'%', True, (255, 215, 0))
                screen.blit(percent_text,percent_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))
                pygame.display.flip()
                
                for j in range(1, 49):
                    num = str(j).zfill(3)
                    cannon_anim[i].append(pygame.image.load(dir_name + "/img_" + num + ending))
                if i in [3, 7, 11, 14, 15, 16]:
                    cannon_anim[i].append(pygame.image.load(dir_name + "/img_049" + ending))
                if i == 7:
                    cannon_anim[i].append(pygame.image.load(dir_name + "/img_050" + ending))

        
        play_text = font.render('PLAY', True, (255, 215, 0))
        quit_text = font.render('QUIT', True, (255, 215, 0))
        screen.blit(play_text,play_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
        screen.blit(quit_text,quit_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))

        pygame.display.flip() # update screen

def gameplay_loop(cannon_cooldown = framerate*(3/2), game_time = 90*framerate, island_health = 50, max_ship_distance = 300, next_ship_time_randomness = 1, enemy_fire_rate = framerate):
    """There are now 6 adjustable parameters for the gameplay_loop

cannon_cooldown - is how often the cannon reloads
game_time - is the length of each day
island_health - is how much heath the island starts with
max_ship_distance - is the furthest distance a new ship can spawn
next_ship_time_randomness - can be between 1 & 2, 1 is defaultly random, 2 is no randomness (aka at 2 new ships will arrive at a constant rate)
enemy_fire_rate - is the rate at which ships will damage the island once there

Theoretically we could allow the player to improve one of these after each successful level completion,
the speed at which new ships arrive would still always be increasing so they should't survive infinitely

currently none of them actually change when leveling up
"""
    global run, game_state, ships, current_level, kill_count, curr_time

    current_level += 1

    cannonballs = pygame.sprite.Group()
    cannon = Cannon()   
    ships.empty()
    active_sprites.empty()
    cannonballs.empty()

    ship_deck_img = pygame.transform.scale(pygame.image.load('sprites/ship_deck.png'), (WIDTH , WIDTH*(1355/3000)))
    ship_deck_rect = ship_deck_img.get_rect(midbottom=(WIDTH/2, HEIGHT))

    on_gameplay_screen = True

    curr_time = -1

    if current_level > framerate: # the level 60 clause
        next_ship_time = next_ship_time_randomness
    else:
        next_ship_time = random.randint(int((next_ship_time_randomness*framerate)/current_level), int((2*framerate)/current_level)) # [1 second, 2 seconds] decreases each level
    
    is_red_island = False # If the island is taking damage this tick
    previous_island_health = island_health # A variable for tracking if the island lost any health in a tick
    if curr_time == -1:
        initial_island_health = island_health
    
    if current_level == 1 and curr_time == -1: # sets the kill count to 0 on day 1
        kill_count = 0

    while on_gameplay_screen:
        clock.tick(framerate)

        curr_time+=1
        if curr_time % cannon_cooldown == 0: # resets cannon cooldown
            cannon_is_avail = True

        if curr_time == game_time: pygame.event.post(pygame.event.Event(NIGHTFALL))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                run = False
                on_gameplay_screen = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and cannon_is_avail:
                    pygame.event.post(pygame.event.Event(CANNON_FIRED_EVENT))
                    cannon_is_avail = False  # resets cannon cooldown
            if event.type == NIGHTFALL:
                for ship in ships:
                    if not ship.sinking: ship.vel = (-0.5,0,0)
                    ship.original_image = pygame.transform.flip(ship.original_image, True, False)
                for cannonball in cannonballs:
                    cannonball.kill()
                    cannonballs.update()
                on_gameplay_screen = False
                game_state = NEXT_LEVEL_SCREEN
            if event.type == CANNON_FIRED_EVENT:
                pygame.mixer.Sound.play(sound_fire)
                new_cannonball = Cannonball(cannon)
                cannonballs.add(new_cannonball)
                active_sprites.add(new_cannonball)
            if event.type == SHIP_HIT:
                kill_count += 1
                pygame.mixer.Sound.play(sound_hit)
                event.cannonball.kill()
                event.ship.sinking = True
                cannon_is_avail = True
        
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
            y_dist = random.randint(60,max_ship_distance)
            new_ship = Ship(y_dist)
            ships.add(new_ship)
            active_sprites.add(new_ship, layer=-y_dist)
            if current_level > framerate:
                next_ship_time = 1
            else:
                next_ship_time = random.randint(int((next_ship_time_randomness*framerate)/current_level), int((2*framerate)/current_level)) # set countdown for next ship

        next_ship_time -= 1

        ships.update(curr_time, game_time)
        cannonballs.update()
        cannon.update()

        for ship in ships:
            # island damage if ship has zero velocity
            if ship.vel == pygame.math.Vector3(0,0,0) and curr_time % enemy_fire_rate == 0 and not ship.sinking:
                is_red_island = True
                island_health -=1
            elif curr_time % enemy_fire_rate >= 5:
                is_red_island = False

            # ship hit
            if ship.sinking:
                continue
            for cannonball in cannonballs:
                diff_vec = cannonball.pos - ship.pos
                if (diff_vec.magnitude() < 20):
                    ship_hit_data = {"cannonball": cannonball, "ship": ship}
                    pygame.event.post(pygame.event.Event(SHIP_HIT, ship_hit_data))

        if previous_island_health != island_health:
            pygame.mixer.Sound.play(sound_island_hurt)
            previous_island_health = island_health

        if island_health <= 0:
            on_gameplay_screen = False
            game_state = GAME_OVER_SCREEN
            for cannonball in cannonballs:
                cannonball.kill()
                cannonballs.update()

        # draw stuff

        ship_rocking_adjust = 20*math.sin(curr_time / rocking_rate)

        curr_sky_color = night_sky_color
        curr_water_color = night_water_color
        if curr_time < game_time: 
            curr_sky_color = get_color_gradient(day_sky_color, night_sky_color, curr_time / game_time)
            curr_water_color = get_color_gradient(day_water_color, night_water_color, curr_time / game_time)
        pygame.draw.rect(screen, curr_sky_color, (0,0,WIDTH, HEIGHT/2+ship_rocking_adjust))
        pygame.draw.rect(screen, curr_water_color, (0,HEIGHT/2+ship_rocking_adjust,WIDTH, HEIGHT/2))

        # draws island & heath bar red or green
        pygame.draw.rect(screen, border_color, ((WIDTH-(WIDTH/3))-2,(HEIGHT/5)-2+ship_rocking_adjust,(initial_island_health*(WIDTH/200))+4, (HEIGHT/30)+4))
        if is_red_island:
            pygame.draw.polygon(screen, damage_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2+ship_rocking_adjust], [WIDTH, 4*HEIGHT/7+ship_rocking_adjust], [WIDTH, 3*HEIGHT/7+ship_rocking_adjust]])
            pygame.draw.rect(screen, damage_color, (WIDTH-(WIDTH/3),HEIGHT/5+ship_rocking_adjust,island_health*(WIDTH/200), HEIGHT/30))
        else:
            pygame.draw.polygon(screen, island_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2+ship_rocking_adjust], [WIDTH, 4*HEIGHT/7+ship_rocking_adjust], [WIDTH, 3*HEIGHT/7+ship_rocking_adjust]])
            pygame.draw.rect(screen, island_color, (WIDTH-(WIDTH/3),HEIGHT/5+ship_rocking_adjust,island_health*(WIDTH/200), HEIGHT/30))

        active_sprites.draw(screen)
        cannonballs.draw(screen)
        screen.blit(ship_deck_img, ship_deck_rect)
        screen.blit(cannon.image, cannon.rect)

        # draws the cannonball-ready indicator
        if cannon_is_avail:
            pygame.draw.circle(screen, border_color, (WIDTH-WIDTH/8,HEIGHT-HEIGHT/8), 50)

        pygame.display.flip() # update screen


def next_level_loop(button_delay):
    global run, game_state, current_level


    NEXT_LEVEL = 0
    QUIT = 1
    current_button_selected = NEXT_LEVEL

    on_menu_screen = True
    while on_menu_screen:
        clock.tick(framerate)
        button_delay -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_menu_screen = False
                run = False
            if event.type == pygame.KEYDOWN and button_delay <= 0:
                if event.key == pygame.K_SPACE:
                    if current_button_selected == NEXT_LEVEL:
                        game_state = GAMEPLAY_SCREEN
                        on_menu_screen = False
                    elif current_button_selected == QUIT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT)) 
                elif event.key == pygame.K_DOWN:
                    current_button_selected = QUIT
                elif event.key == pygame.K_UP:
                    current_button_selected = NEXT_LEVEL
    
        # draw stuff

        ship_rocking_adjust = 20*math.sin(curr_time / rocking_rate)

        # -- draw background --

        # draw background
        pygame.draw.rect(screen, night_sky_color, (0,0,WIDTH, HEIGHT/2+ship_rocking_adjust))
        pygame.draw.rect(screen, night_water_color, (0,HEIGHT/2+ship_rocking_adjust,WIDTH, HEIGHT/2))

        # draw island
        pygame.draw.polygon(screen, island_color, [[WIDTH-(2*WIDTH/5), HEIGHT/+2+ship_rocking_adjust], [WIDTH, 4*HEIGHT/7+ship_rocking_adjust], [WIDTH, 3*HEIGHT/7+ship_rocking_adjust]])

        # draw ships
        ships.update(1,0)
        active_sprites.draw(screen)

        # -- draw buttons -- 
        
        # highlight currently selected button
        if current_button_selected == NEXT_LEVEL:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2-255, 810, 210)) # play again button highlight
        if current_button_selected == QUIT:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2+95, 810, 210)) # quit button highlight

        # button background
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2-250, 800, 200)) # play again button
        pygame.draw.rect(screen, night_sky_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200)) # quit button

        # button text
        font = pygame.font.Font('PirateJack-lglRX.otf',175) # Pirate Jack by font by Tigade Std
        play_text = font.render('NEXT LEVEL', True, (255, 215, 0))
        quit_text = font.render('QUIT', True, (255, 215, 0))
        screen.blit(play_text,play_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
        screen.blit(quit_text,quit_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))

        level_text = font.render('Level '+str(current_level)+' Complete', True, (255, 215, 0))
        screen.blit(level_text,level_text.get_rect(center=(WIDTH/2,120)))

        pygame.display.flip() # update screen

def game_over_loop(button_delay):
    global run, game_state, current_level, kill_count

    current_level = 0

    PLAY_AGAIN = 0
    QUIT = 1
    current_button_selected = PLAY_AGAIN

    on_game_over_screen = True
    while on_game_over_screen:
        clock.tick(framerate)
        button_delay -= 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                on_game_over_screen = False
                run = False
            if event.type == pygame.KEYDOWN and button_delay <= 0:
                if event.key == pygame.K_SPACE:
                    if current_button_selected == PLAY_AGAIN:
                        game_state = GAMEPLAY_SCREEN
                        on_game_over_screen = False
                    elif current_button_selected == QUIT:
                        pygame.event.post(pygame.event.Event(pygame.QUIT)) 
                elif event.key == pygame.K_DOWN:
                    current_button_selected = QUIT
                elif event.key == pygame.K_UP:
                    current_button_selected = PLAY_AGAIN
    
        # draw stuff

        # pygame.draw.rect(screen, day_water_color, (0,0,WIDTH, HEIGHT)) # background

        # -- draw background --

        ship_rocking_adjust = 20*math.sin(curr_time / rocking_rate)

        # draw background
        pygame.draw.rect(screen, night_sky_color, (0,0,WIDTH, HEIGHT/2+ship_rocking_adjust))
        pygame.draw.rect(screen, night_water_color, (0,HEIGHT/2+ship_rocking_adjust,WIDTH, HEIGHT/2))

        # draw island
        pygame.draw.polygon(screen, island_color, [[WIDTH-(2*WIDTH/5), HEIGHT/2+ship_rocking_adjust], [WIDTH, 4*HEIGHT/7+ship_rocking_adjust], [WIDTH, 3*HEIGHT/7+ship_rocking_adjust]])

        # draw ships
        ships.update(1,0)
        active_sprites.draw(screen)

        # -- draw buttons -- 
        
        # highlight currently selected button
        if current_button_selected == PLAY_AGAIN:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2-255, 810, 210)) # play again button highlight
        if current_button_selected == QUIT:
            pygame.draw.rect(screen, (255,255,255), (WIDTH/2-405, HEIGHT/2+95, 810, 210)) # quit button highlight

        # button background
        pygame.draw.rect(screen, night_water_color, (WIDTH/2-400, HEIGHT/2-250, 800, 200)) # play again button
        pygame.draw.rect(screen, night_sky_color, (WIDTH/2-400, HEIGHT/2+100, 800, 200)) # quit button

        # button text
        font = pygame.font.Font('PirateJack-lglRX.otf',175) # Pirate Jack by font by Tigade Std
        play_text = font.render('PLAY AGAIN', True, (255, 215, 0))
        quit_text = font.render('QUIT', True, (255, 215, 0))
        screen.blit(play_text,play_text.get_rect(center=(WIDTH/2,HEIGHT/2-145)))
        screen.blit(quit_text,quit_text.get_rect(center=(WIDTH/2,HEIGHT/2+195)))

        lose_text = font.render('GAME OVER', True, (255, 215, 0))
        kill_text = font.render(str(kill_count)+' Ships Sunk', True, (255, 215, 0))
        screen.blit(lose_text,lose_text.get_rect(center=(WIDTH/2,120)))
        screen.blit(kill_text,kill_text.get_rect(center=(WIDTH/2,(HEIGHT)-120)))

        pygame.display.flip() # update screen

while run: # the button_delay times prevent accidental button selecing

    if (game_state == GAMEPLAY_SCREEN):
        gameplay_loop()
    elif (game_state == TITLE_SCREEN):
        title_loop(10)
    elif (game_state == NEXT_LEVEL_SCREEN):
        next_level_loop(60)
    elif (game_state == GAME_OVER_SCREEN):
        game_over_loop(60)

pygame.quit()
