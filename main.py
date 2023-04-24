import asyncio
from random import randint
import copy
import math
import numpy as np
import sys
import pygame
#from cfg import *
import string




# Global variables
###################################################################################

# field generator setup
minsamples = 5
iterations = 4

hres = 1280
vres = 720

tickrate = 120
gravity = -9.81
input_scale = 700 / hres
time_scale = hres / 200

screen_color = (0, 0, 0)
ground_color = (255, 0, 0)
projectile_color = (25, 25, 25)

# Setup fps counter
frame_count = 0
frame_time_count = 0
frame_time_avg = '0'
fps_avg = '0'
update_interval = tickrate // 2

# Player generator setup
default_color = ((0, 0, 255), (86, 130, 3),(255, 0, 0))
p1color = (0, 0, 255)
p2color = (86, 130, 0)
player_list = []

# Init Pygame
pygame.init()
screen = pygame.display.set_mode((hres, vres))
clock = pygame.time.Clock()

# Load Fonts
title_font = pygame.font.Font('freesansbold.ttf', 64)
font1 = pygame.font.Font('freesansbold.ttf', 24)
font2 = pygame.font.Font('freesansbold.ttf', 32)
font_fps = pygame.font.Font('freesansbold.ttf', 16)
font_small = pygame.font.Font('freesansbold.ttf', 16)










#pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])




    
    

###################################################################################


 
# Main function
async def main():
#def main():

    # Global variables (need to improve this)
    ###########################################################################################################
    
    # Initialise game objects
    world = World.get()
    projectile = Projectile(world.ground)
    p1 = Player()
    #p1.gen_pos(world.ground)
    p2 = Player()
    #p2.gen_pos(world.ground)
    print('Players:', Player.count, Player.list)
    player_list = [p1, p2]

    # Start game with score 0
    score = 0

    crater_color = (255, 240, 0)
    blastsize = 27
    


    init_new = True
    hit = p1_hit = p2_hit = False
    reset_score = False
    main_count = 0
    turn = 0

    kaboom = 0
    kaboomfactor = 7

    # Load cannon sprite
    cannon_sprite = pygame.image.load("assets/cannon.png").convert_alpha()


    #################################################################################################3
    
    # Game loop
    while True :
        clock.tick_busy_loop(tickrate)
        #clock.tick(tickrate)
        #time = pygame.time.get_ticks()
        #Player.active = turn % len(Player.list)
        Player.active = player_list[turn % len(Player.list)]

        # Get mouse position 
        mouse_pos = pygame.mouse.get_pos()
        

        # Game menu loop
        while State.state['menu'] == 1 :
            # Make cursor blink Main.cursor value (0 or 1)
            clock.tick_busy_loop(tickrate)
            main_count += 1
            if main_count >= 2 * tickrate :
                main_count = 0
            Menu.cursor = main_count // tickrate

            if State.state['title_menu'] == 1 :
                Menu.title(screen)
                # Go title menu
            if State.state['main_menu'] == 1 :
                Menu.main(screen, p1, p2)
                # go pause menu
            if State.state['end_menu'] == 1 :
                pass
                # go end menu

        # Event loop
        for event in pygame.event.get() :
            # Key event    

            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_n :
                    init_new = True
                    reset_score = True


            # Mousebutton event (launch projectile
            if projectile.inflight == False and hit == False :
                if event.type == pygame.MOUSEBUTTONDOWN :
                    mouse_presses = pygame.mouse.get_pressed()
                    if mouse_presses[0]:
                        print(mouse_pos)
                        kaboom = 0
                        kaboomfactor = 7    # Hit explosion speed factor 
                        velocity = [input_scale* (mouse_pos[0] - Player.active.pos[0]), 
                            input_scale * (mouse_pos[1] - Player.active.pos[1])]
                        projectile.launch(Player.active.pos, velocity)

            # Exit game on close windows button
            if event.type == pygame.QUIT:
                sys.exit()

        # Logic loop

        if init_new == True :    # Initiate new turn
            world = World.get()
            p1.gen_pos(world.ground)
            p2.gen_pos(world.ground)
            projectile = Projectile(world.ground)
            if reset_score == True :
                p1.score = p2.score = 0
                reset_score = False
            hit = p1_hit = p2_hit = False
            init_new = False

        # Calculate projectile flight and collision, hit detect.        
        if projectile.inflight == True :                     # Increment if in flight.
            projectile.increment()
            if projectile.inflight == False :               # if inflight==False after increment, shot has finished
                turn += 1
            if projectile.collision == True :               # Calculate crater position and hit detection
                if projectile.check_hit(p1.pos) :           # Increment player score on hit
                    p2.add_score()
                    hit = p1_hit = True
                if projectile.check_hit(p2.pos) :
                    p1.add_score()
                    hit = p2_hit = True
                #print('flight:', projectile.inflight, ' Hit1:', p1_hit, p2_hit)




        # Render loop

        pygame.Surface.fill(screen, (0, 0, 0))                          # Draw background color.
        pygame.draw.aalines(screen, world.color, False, world.ground)   # Draw world.ground.


        if projectile.inflight == True :                                        # Draw projectile if in flight.
            pygame.draw.aalines(screen, projectile.color, False, projectile.trajectory[-7:])
            pygame.draw.aalines(screen, (255, 255, 0), False, projectile.trajectory[-2:])
            #pygame.draw.circle(screen, (255, 255, 0), projectile.trajectory[-1], radius=1)
        
        
        # Update cannon angle for active player, according to mouse position
        Player.active.set_cannon_angle(mouse_pos)

        # Draw cannon sprites
        draw_cannon(cannon_sprite, p1)
        draw_cannon(cannon_sprite, p2)

        # Draw player sprites
        screen.blit(p1.sprite, (p1.pos[0] - 35, p1.pos[1] - 28))
        screen.blit(p2.sprite, (p2.pos[0] - 28, p2.pos[1] - 28))

        # Draw player dots (for testing purposes)
        #pygame.draw.circle(screen, p1.color, p1.pos, radius=8)
        #pygame.draw.circle(screen, p2.color, p2.pos, radius=8)    
        
        # Draw explosions in case of projectile collision with ground
        if projectile.collision == True :
            if kaboom < blastsize :
                kaboom += 2
                pygame.draw.circle(screen, crater_color, projectile.crater, radius=kaboom)
            else :
                pygame.draw.circle(screen, crater_color, projectile.crater, radius=blastsize)

        # Draw hit animation if player is hit
        if hit :
            kaboom += kaboomfactor
            kaboomfactor *= 0.997
            pygame.draw.circle(screen, crater_color, projectile.crater, radius=kaboom)
            if kaboom > hres :
                init_new = True

        # Draw score and framerate overlays
        draw_score(screen, p1, p2)
        draw_fps(screen, show_frame_time=False)

        # Flip framebuffer
        pygame.display.flip()
    await asyncio.sleep(0)




# Game classes.
# Game State counters 
class State:
    state = {'menu' : 1, 'title_menu' : 1, 'main_menu' : 0, 'pause_menu': 0, 'end_menu' : 0, 'gameplay' : 0}


# world class generates .ground(np.array) on initiation
# .ground
class World:
    
    def __init__(self, ground):
        self.ground = ground
        self.color = ground_color

    @classmethod
    # sampling for use in generate()
    def _iteration(cls, samples, hres, vres) :
        #nr of pixels per sample
        segment = hres / (samples - 1)
        
        # Create terrain samples and average slope between samples
        samplelist = []
        slopelist = []
        for i in range(samples) :
            samplelist.append(vres - (randint((0), (16 * vres // 20))))   # y Coordinates flipped 
        for i in range(samples - 1) :
            slopelist.append((samplelist[i + 1] - samplelist[i]) / segment)

        # Create full length list of interpolated terrain, first value is samplelist[0]
        terrain = [samplelist[0]]
        for i in range(hres - 1) :
            n = int (i / segment)
            terrain.append(float(terrain[i]) + slopelist[n])
        return terrain

    @classmethod
    # Use to create new instance (ground will be generated)
    def get(cls, minsamples=minsamples, iterations=iterations, hres=hres, vres=vres) :
        unweightedground = np.zeros(hres)
        weightsum = 0
        for i in range(iterations) :
            samples = minsamples * (2 ** i)
            weight = 1 / (2 ** i)
            weightsum += weight
            iter = np.array(cls._iteration(samples, hres, vres))
            unweightedground += (iter * weight)
        groundlist = unweightedground / weightsum
        #groundxvalues = np.array(range(hres)) 
        #ground = np.column_stack((groundxvalues, groundlist))
        ground = [ i for i in enumerate(groundlist)]
        return cls(ground)
        

# Player class
# .nr .name .pos .color
class Player:
    # Class variables
    count = 0
    list = []
    active = 1

    
    def __init__(self, name=None, color=False):
        Player.count += 1
        self.nr = Player.count
        self.pos = [0, 0]
        self.set_color(color)
        self.name = str(name) if name else 'Player {}'.format(self.nr)
        self.score = 0
        if self.nr == 1:
            self.sprite = pygame.image.load("assets/tank_blue.png").convert_alpha()
            self.cannon_angle = 5
        elif self.nr == 2:
            self.sprite = pygame.transform.flip(pygame.image.load("assets/tank_green.png").convert_alpha(), True, False)
            self.cannon_angle = 175
        else:
            self.sprite = pygame.image.load("assets/tank_pink.png").convert_alpha()
            self.cannon_angle = 5
        Player.list.append((self.name))
        
        
    
    def __str__(self):
        return 'Player nr: {}\nName: {}\nPosition: {}\nColor: {}'.format(self.nr, self.name, self.pos, self.color)
    
    
    def set_name(self, name):
        self.name = str(name)

    
    # Generate player position
    def gen_pos(self, ground, hres=hres):
        if self.nr == 1:
            xpos = randint(hres // 20, 3 * hres // 20)
            pos = [xpos, ground[xpos][1]]   # y Coordinates flipped 
        elif self.nr == 2:
            xpos = randint(17 * hres // 20, 19 * hres // 20)
            pos = [xpos, ground[xpos][1]]   # y Coordinates flipped 
        else:
            raise Exception("Invalid player nr")
        self.pos = pos

    
    # Arg RGB tuple
    def set_color(self, color):
        if type(color) == tuple:
            if len(color) >= 3 and max(color) < 256 and min(color) >= 0:
                self.color = color[:3]
        else:
            self.color = default_color[(self.nr-1) % len(default_color)]

    
    def set_cannon_angle(self, mouse_pos):
        #mouse_pos
        if mouse_pos[0] - self.pos[0] >= 0:
            self.cannon_angle = math.degrees(math.atan((Player.active.pos[1] - mouse_pos[1]) / (mouse_pos[0] - Player.active.pos[0])))
        else:
            self.cannon_angle = 180 + math.degrees(math.atan((Player.active.pos[1] - mouse_pos[1]) / (mouse_pos[0] - Player.active.pos[0])))
        

    def add_score(self, amount=1) :
        self.score = self.score + amount


# Initiate projectile launch
# .trajectory .pos .velocity .inflight .collision
class Projectile:

    def __init__(self, ground, weapon_id=0):
        self.weapon_id = weapon_id
        self.inflight = False
        self.collision = False
        self.hit = False
        self.color = projectile_color
        self.ground = ground
        ## self.pos = 0
        self.velocity = []
        self.trajectory = []
        self.crater = []

    
    def launch(self, start_pos, start_velocity):
        self.inflight = False
        self.collision = False
        self.hit = False
        self.color = projectile_color
        self.pos = copy.deepcopy(start_pos)
        self.pos[1] = self.pos[1] - 13 # Correction for tank sprite cannon position
        self.velocity = copy.deepcopy(start_velocity)
        self.trajectory = copy.deepcopy([self.pos])
        self.inflight = True

    
    # Increment projectile position by one timestep, check collision with world.
    def increment(self, target_pos=None) :
        if not self.collision:
            dt = time_scale / tickrate
            position = copy.deepcopy(self.pos)
            velocity = copy.deepcopy(self.velocity)
            position[0] = position[0] + velocity[0] * dt
            position[1] = position[1] + velocity[1] * dt
            velocity[1] = velocity[1] - gravity * dt
            self.pos = position
            self.velocity = velocity
            self.trajectory.append(position)
            self.check_collision()

    
    # Check collision with world check and return .end .collision value.
    def check_collision(self):
        l = [0,0]
        col_pos = [0,0]
        if self.pos[0] < 0 or self.pos[0] > hres - 1 :
            self.inflight = False
        elif self.pos[1] >= self.ground[int(self.pos[0])][1]: # y Coordinates flipped 
            self.inflight = False
            self.collision = True
            col_list = self.pos # Calculate exact collision coordinate
            pos1 = self.trajectory[-2]
            pos2 = self.pos
            #print('A', pos2, pos1)
            slope_pos = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
            const = pos1[1] - (pos1[0] * slope_pos)
            l = []
            i = 0
            if pos2[0] > pos1[0] :
                while i < abs(pos2[0] - pos1[0]) :
                    i += 1
                    x = int(pos1[0]) + i
                    y = slope_pos * x + const
                    l.append([x, y])
            else :
                while i < abs(pos2[0] - pos1[0]) :
                    i += 1
                    x = int(pos1[0]) - i
                    y = slope_pos * x + const
                    l.append([x, y])

            if len(l) < 2 :
                self.crater = self.pos
            else :
                #print('L: ', l)
                for i in l :
                    #print('i: ', i, 'ground: ', self.ground[i[0]])
                    if i[1] > self.ground[i[0]][1] :                        
                        #col_pos = copy.deepcopy(self.ground[i[0]])
                        self.crater = i
                        break
                        
    
    def check_hit(self, target, blast_size=25) :    # Calculate if player hit.
        if sum((np.array(target, dtype=float) - np.array(self.crater)) ** 2) < (blast_size ** 2) :
            self.hit = True
            return True
        else :
            return False

    '''
    def roll(self):
        posx_int = int(posx_int)
        if self.ground[posx_int - 1][1] > self.ground[posx_int + 1][1] :
            while posx_int - (i + 5) > 0 :
                if self.ground[posx_int - (i + 4)] > self.ground[posx_int - i] :
                    i += 1
                    for q in range(10) :
                        output.append((posx_int - i, self.ground[posx_int - i]))
                    if hitcheck(output[-1], postarget, 10) :
                        break
                else :
                    break
        else :
            while (posx_int + (i + 5)) < hres :
                if self.ground[posx_int + (i + 4)] > self.ground[posx_int + i] :
                    i += 1
                    for q in range(10) :
                        output.append((posx_int + i, self.ground[posx_int + i]))
                    if hitcheck(output[-1], postarget, 10) :
                        break
                else :
                    break 

                    

        elif roll :
            i = 0
            posx_int = int(position[0])
            if world[posx_int - 1] > world[posx_int + 1] :
                while posx_int - (i + 5) > 0 :
                    if world[posx_int - (i + 4)] > world[posx_int - i] :
                        i += 1
                        for q in range(10) :
                            output.append((posx_int - i, world[posx_int - i]))
                        if hitcheck(output[-1], postarget, 10) :
                            break
                    else :
                        break
            else :
                while (posx_int + (i + 5)) < hres :
                    if world[posx_int + (i + 4)] > world[posx_int + i] :
                        i += 1
                        for q in range(10) :
                            output.append((posx_int + i, world[posx_int + i]))
                        if hitcheck(output[-1], postarget, 10) :
                            break
                    else :
                        break
            crater = output[-1]
            output.append(crater)
            break
        '''


class Menu :
    cursor = 0
    name = ''

    @classmethod
    def typing(cls, char) :
        alfabet = string.ascii_letters
        cap = pygame.key.get_pressed()[pygame.K_LSHIFT] | pygame.key.get_pressed()[pygame.K_RSHIFT]
        if 96 < char & char < 96 + len(alfabet) :
            char = char - 97
            char = alfabet[char + cap * 26]
        #elif char == 32 :
            #char = ' '
        else :
            char = ''
        return char

    @classmethod 
    def title(cls, surface) :   # Draw Title screen 
        global init_new
        pygame.Surface.fill(screen, (0, 0, 0)) 

        for event in pygame.event.get() :
            # Key event    
            if event.type == pygame.KEYDOWN :
                if event.key == pygame.K_SPACE :
                    State.state['main_menu'] = 1
                    State.state['title_menu'] = 0
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN :
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    State.state['main_menu'] = 1
                    State.state['title_menu'] = 0

        string = 'Tank duel'
        text = title_font.render(string, True, (255,0 ,0), (0,0,0))
        textrect = text.get_rect()
        textrect.centerx = hres // 2
        textrect.bottom = vres // 4
        surface.blit(text, textrect)
        
        string = '(Click to start)'
        text = font_small.render(string, True, (255, 0, 0), (0,0,0))
        text2rect = text.get_rect()
        text2rect.centerx = hres // 2
        text2rect.top = textrect.bottom + 5
        surface.blit(text, text2rect)
        
        string = '2023, by Kasper Vloon'
        text = font_small.render(string, True, (100, 100, 100), (0,0,0))
        textrect = text.get_rect()
        textrect.bottomright = (hres - 10, vres -10)
        surface.blit(text, textrect)

        
        pygame.display.flip() 
 
    @classmethod
    def main(cls, surface, p1, p2) :   # Draw Main screen
        #init_new

        i = 0
        pygame.Surface.fill(screen, (0, 0, 0)) 
        
        for event in pygame.event.get() :
            # Key event    
            if event.type == pygame.KEYDOWN :
                if event.key == 8 :
                    cls.name = cls.name[:-1]
                else :
                    char = event.unicode
                    char = char.strip()
                    cls.name = cls.name + char
                    cls.name = cls.name[:10]
            
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN :
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    State.state['menu'] = 0
                    State.state['main_menu'] = 0
                    init_new = True
        
        # Title line
        string = 'Name'
        text = font2.render(string, True, (255,0 ,0), (0,0,0))
        textrect = text.get_rect()
        textrect.left = hres * 3 // 8
        textrect.bottom = vres // 6
        surface.blit(text, textrect)

        string = 'Color'
        text = font2.render(string, True, (255,0 ,0), (0,0,0))
        textrect = text.get_rect()
        textrect.left = hres * 5 // 8
        textrect.bottom = vres // 6
        surface.blit(text, textrect)
        
        # Player 1 line
        string = 'Player {}'.format(p1.nr)
        text = font2.render(string, True, p1.color, (0,0,0))
        text2rect = text.get_rect()
        text2rect.left = hres // 8
        text2rect.top = textrect.bottom + 10
        surface.blit(text, text2rect)
        
        string = cls.name[:10] + '_' * cls.cursor
        text = font2.render(string, True, p1.color, (0,0,0))
        text2rect = text.get_rect()
        text2rect.left = hres * 3 // 8
        text2rect.top = textrect.bottom + 10
        surface.blit(text, text2rect)

        # Player 2 line
        string = 'Player {}'.format(p2.nr)
        text = font2.render(string, True, p2.color, (0,0,0))
        text3rect = text.get_rect()
        text3rect.left = hres // 8
        text3rect.top = text2rect.bottom + 10
        surface.blit(text, text3rect)
        
        string = cls.name[:10] + '_' * cls.cursor
        text = font2.render(string, True, p2.color, (0,0,0))
        text3rect = text.get_rect()
        text3rect.left = hres * 3 // 8
        text3rect.top = text2rect.bottom + 10
        surface.blit(text, text3rect)

        pygame.display.flip() 


# Game methods
def draw_fps(surface, interval=update_interval, show_frame_time=False) :   # Calculate fps over 'interval' frame average
    global frame_count
    global frame_time_count
    global fps_avg
    global frame_time_avg
    global font16

    frame_time = int(clock.get_time())
    if frame_count < interval :   # Update_interval is nr of frames over which to average
        frame_count += 1
        frame_time_count += frame_time
    else :
        ft = frame_time_count / interval
        frame_time_avg = str(round(ft))
        fps_avg = str(round(1000 / ft, 1))
        frame_count = 0
        frame_time_count = 0
    
    
    if show_frame_time == False :
        text = font_fps.render(fps_avg, True, (0, 255, 0), (0,0,0))
    else :
        text = font_fps.render(frame_time_avg, True, (0, 255, 0), (0,0,0))
    textRect = text.get_rect()
    textRect.topleft = (10, 10)
    surface.blit(text, textRect)


def draw_score(surface, p1, p2) :   # Draw Score board

    string = p1.name + '  |'
    text = font1.render(string, True, p1.color)
    textrect = text.get_rect()
    textrect.topright = (hres // 2, 10)
    surface.blit(text, textrect)

    string = str(p1.score)
    text = font2.render(string, True, p1.color)
    text2rect = text.get_rect()
    text2rect.top = textrect.bottom + 10
    text2rect.centerx = textrect.right - 60
    surface.blit(text, text2rect)
       

    string = '|  ' + p2.name
    text = font1.render(string, True, p2.color)
    textrect = text.get_rect()
    textrect.topleft = (hres // 2, 10)
    surface.blit(text, textrect)

    string = str(p2.score)
    text = font2.render(string, True, p2.color)
    text2rect = text.get_rect()
    text2rect.top = textrect.bottom + 10
    text2rect.centerx = textrect.left + 60
    surface.blit(text, text2rect)


def draw_cannon(sprite, player):
    cannon = pygame.transform.rotate(sprite, player.cannon_angle)
    w = cannon.get_width() // 2
    h = cannon.get_height() // 2
    if player.nr == 1:
        screen.blit(cannon, (player.pos[0] - w, player.pos[1] - h - 13))
        screen.blit(player.sprite, (player.pos[0] - 35, player.pos[1] - 28))
    elif player.nr == 2:
        screen.blit(cannon, (player.pos[0] - w, player.pos[1] - h - 13))
        screen.blit(player.sprite, (player.pos[0] - 28, player.pos[1] - 28))


def _check_hit(crater, target_pos, blast_size=25) :    # Calculate if player hit.
    if sum((np.array(target_pos, dtype=float) - np.array(crater)) ** 2) < (blast_size ** 2) :
        return True
    else :
        return False





asyncio.run(main())

#if __name__ == "__main__":
 #   main()
