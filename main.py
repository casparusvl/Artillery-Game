import asyncio
import copy
import math
from random import randint
import sys
#import string

import numpy as np
import pygame


# Global constants
###################################################################################

# World generator settings
MINSAMPLES = 5
ITERATIONS = 4

# Screen resolution
HRES = 1280
VRES = 720

# Game engine settings
TICKRATE = 60   # This is also the max framerate. Game speed will slow down if TICKRATE can't be maintained
GRAVITY = -10
INPUT_SCALE = 700 / HRES    #0.5
TIME_SCALE = HRES / 200     #7

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (166, 166, 166)
DARKGREY = (100, 100, 100)

# Setting for hit animation
if TICKRATE < 100:
    KABOOMCONSTANT = 12
else:
    KABOOMCONSTANT = 7    # Hit explosion speed factor

CRATER_COLOR = (255, 240, 0)
BLASTSIZE = 27

#screen_color = (0, 0, 0)
GROUND_COLOR = RED

# Player generator setup
DEFAULT_COLOR = ((0, 0, 255), (86, 130, 3),(255, 0, 0))
#P1COLOR = (0, 0, 255)
#P2COLOR = (86, 130, 0)



# Init Pygame
pygame.init()
screen = pygame.display.set_mode((HRES, VRES))
clock = pygame.time.Clock()

# Load Fonts
title_font = pygame.font.Font('freesansbold.ttf', 64)
font1 = pygame.font.Font('freesansbold.ttf', 24)
font2 = pygame.font.Font('freesansbold.ttf', 32)
font_fps = pygame.font.Font('freesansbold.ttf', 16)
font_small = pygame.font.Font('freesansbold.ttf', 16)


###################################################################################

# async is required for pygbag
async def main():
    '''
    Main function
    '''

    # Initialise game objects
    global state
    state = GameState()
    fps = Frame_counter()
    world = World()
    projectile = Projectile()
    p1 = Player()
    p2 = Player()
    #print(Player.count, f"Players: {Player.list[0].name}, {Player.list[1].name};")

    
    # Game loop
    while True :
        clock.tick(TICKRATE)
        #clock.tick_busy_loop(TICKRATE)
        #time = pygame.time.get_ticks()
        Player.active = Player.list[state.turn % len(Player.list)]

        # Get mouse position 
        mouse_pos = pygame.mouse.get_pos()
        

        # Initiate new turn
        if state.init_new:
                if state.victory:
                    state.menu = True
                else:
                    world.generate()
                    p1.gen_pos(world)
                    p2.gen_pos(world)
                    projectile.reset()
                    state.init_new = False
                    if state.reset_score == True :
                        p1.score = p2.score = 0
                        state.reset_score = False


        # Menu loop
        while state.menu == True:
            clock.tick(TICKRATE)
            Menu.cursor_blink()

            # Select correct menu screen
            if state.title_menu == True :
                Menu.title(screen)
            elif state.setup_menu == True :
                Menu.setup(screen, p1, p2)
            elif state.pause == True:
                Menu.pause(screen)
            elif state.victory:
                Menu.victory(screen, state.victory)
            
            else:
                state.menu = False
                
            await asyncio.sleep(0)

        
        # Events
        for event in pygame.event.get() :
            
            # Key event
            if event.type == pygame.KEYDOWN:

                # Tests
                #######################################
                # Victory screen
                """
                if event.key == pygame.K_v:
                    state.init_new = True
                    state.victory = p1
                """

                # Generate new terrain
                if event.key == pygame.K_n:
                    state.init_new = True
                ########################################


                if event.key in [pygame.K_ESCAPE, pygame.K_p, pygame.K_PAUSE]:
                   state.menu = True
                   state.pause = True


            # Mousebutton event (launch projectile
            if projectile.inflight == False and projectile.hit == False :
                if event.type == pygame.MOUSEBUTTONDOWN :
                    mouse_presses = pygame.mouse.get_pressed()
                    if mouse_presses[0]:
                        print(f"FIRE AWAY!\nVelocity X/Y: {mouse_pos},   Angle: {Player.active.cannon_angle}")
                        Blast.reset()
                        projectile.launch(Player.active, mouse_pos)

            # Exit game on close windows button
            if event.type == pygame.QUIT:
                sys.exit()


        # Game logic

        # Calculate projectile flight and collision, hit detect.        
        if projectile.inflight == True :                # Increment if in flight.
            projectile.increment()
            projectile.check_collision(world)
            if projectile.inflight == False:
                # Projectile is not inflight anymore, so turn is over
                state.turn += 1
            if projectile.collision == True:    
                # In case projectile has had a collision.
                # Do hit detection on both players and increment score on player hit
                if projectile.check_hit(p1.pos):
                    print(f"{p1.name} was hit!")
                    p2.increase_score()
                    state.turn = 0                 
                    projectile.hit = True
                if projectile.check_hit(p2.pos):
                    print(f"{p2.name} was hit!")
                    p1.increase_score()
                    state.turn = 1
                    projectile.hit = True
                
                # Check victory condition
                if p1.score >= 3:
                    state.victory = p1
                if p2.score >= 3:
                    state.victory = p2




        # Render logic
        pygame.Surface.fill(screen, (0, 0, 0))                          # Draw background color.
        pygame.draw.aalines(screen, world.color, False, world.ground)   # Draw world.ground.

        if projectile.inflight == True :  
            # Draw faint projectile smoketrail
            pygame.draw.aalines(screen, (25, 25, 25), False, projectile.trajectory[-30:])
            # Draw bright yellow projectile
            pygame.draw.aalines(screen, (255, 255, 0), False, projectile.trajectory[-3:])
            # pygame.draw.aalines(screen, (255, 255, 0), False, projectile.interp_traj)
            # Alternate drawing of dot shaped projectile
            #pygame.draw.circle(screen, (255, 255, 0), projectile.trajectory[-1], radius=1)
        
        # Update cannon angle for active player, according to mouse position
        Player.active.set_cannon_angle(mouse_pos)

        # Draw cannon sprites
        draw_cannon(p1)
        draw_cannon(p2)

        # Draw player sprites
        screen.blit(p1.sprite, (p1.pos[0] - 35, p1.pos[1] - 28))
        screen.blit(p2.sprite, (p2.pos[0] - 28, p2.pos[1] - 28))

        # Draw player dots (for testing purposes)
        #pygame.draw.circle(screen, p1.color, p1.pos, radius=8)
        #pygame.draw.circle(screen, p2.color, p2.pos, radius=8)    
        
        # Draw explosions in case of projectile collision with ground
        if projectile.collision == True:
            Blast.small(projectile.crater, BLASTSIZE)

        
        # Draw hit animation if player is hit
        if projectile.hit == True:
            Blast.big(projectile.crater)


        # Draw score and framerate overlays
        draw_score(screen, p1, p2)
        fps.update()
        fps.draw_framerate(screen)
        #fps.draw_frametime(screen)


        # Flip framebuffer
        pygame.display.flip()
        await asyncio.sleep(0)

################################################################################################################################



# Game classes.
class GameState:
    '''
    Stores global game state
    '''
    #__slots__ = ("menu", "title_menu", "setup_menu", "pause", "end_menu", "init_new", "reset_score", "turn", "victory")

    def __init__(self):
        self.menu = True
        self.title_menu = True
        self.setup_menu = False
        self.pause = False
        self.end_menu = False

        self.init_new = True
        self.reset_score = False
        self.turn = 0
        self.victory = None




class World:
    '''
    Generates terrain: .ground(list) on initiation
    '''
    def __init__(self):
        '''
        Create empty world object
        '''
        ground = []
        self.color = GROUND_COLOR


    def _iteration(self, samples, hres, vres) :
        '''
        Sampling for use in World.generate()
        '''
        #nr of pixels per sample
        segment = hres / (samples - 1)
        
        # Create terrain samples and average slope between samples
        samplelist = []
        slopelist = []
        for i in range(samples):
            # Get random y Coordinates within some bounds, y coordinates are flipped because of Pygame coordinate system
            samplelist.append(vres - (randint((0), (16 * vres // 20))))   
        for i in range(samples - 1):
            # Fill array with the desired slope at each list segment, to be able to perform a linear interpolation.
            slopelist.append((samplelist[i + 1] - samplelist[i]) / segment)

        # Perform linear interpolation. For each point add the slope value of the containing segment to the value of the previous point in the array.
        terrain = [samplelist[0]]
        for i in range(hres - 1):
            n = int (i / segment)
            terrain.append(float(terrain[i]) + slopelist[n])
        return terrain
    

    def generate(self, minsamples=MINSAMPLES, iterations=ITERATIONS, hres=HRES, vres=VRES) :
        '''
        #### Generate ground.
        Creates weighted average of an "iterations" nr of runs of iterate().
        '''
        unweightedground = np.zeros(hres)
        weightsum = 0
        for i in range(iterations):
            samples = minsamples * (2 ** i)
            weight = 1 / (2 ** i)
            weightsum += weight
            iter = np.array(self._iteration(samples, hres, vres))
            unweightedground += (iter * weight)
        groundlist = unweightedground / weightsum
        #groundxvalues = np.array(range(hres)) 
        #ground = np.column_stack((groundxvalues, groundlist))
        self.ground = [ i for i in enumerate(groundlist)]
        


class Player:
    '''
    Player class
    instance variables: .nr, .name, .pos, .color, .score, .sprite, .cannon_angle
    Class variables: .count, .list, .active
    '''
    count = 0
    list = []
    active = None

    def __init__(self, color=False):
        Player.count += 1
        self.nr = Player.count
        self.pos = [0, 0]
        self.set_color(color)
        self.set_name()
        self.score = 0
        self.set_sprites()
        Player.list.append(self)


    def __str__(self):
        return 'Player nr: {}\nName: {}\nPosition: {}\nColor: {}'.format(self.nr, self.name, self.pos, self.color)
    
    
    def set_name(self, name=''):
        '''
        Default to name "Player {nr}" if no input given
        '''
        self.name = str(name) if name else f"Player {self.nr}"

    
    def gen_pos(self, world, hres=HRES):
        '''
        Put Player on the ground.
        randomly calculates x coordinate within bounds and calculates correct y coordinate
        '''
        if self.nr == 1:
            xpos = randint(hres // 20, 3 * hres // 20)
            pos = [xpos, world.ground[xpos][1]]   # y Coordinates flipped 
        elif self.nr == 2:
            xpos = randint(17 * hres // 20, 19 * hres // 20)
            pos = [xpos, world.ground[xpos][1]]   # y Coordinates flipped 
        else:
            raise Exception("Invalid player nr")
        self.pos = pos

    
    def set_color(self, color):
        '''
        Allows to select player color , or pick next color from default color list
        '''
        if type(color) == tuple:
            if len(color) >= 3 and max(color) < 256 and min(color) >= 0:
                self.color = color[:3]
        else:
            self.color = DEFAULT_COLOR[(self.nr-1) % len(DEFAULT_COLOR)]


    def increase_score(self, amount=1) :
        '''
        Increments player score by given amount
        '''
        self.score = self.score + amount


    def set_sprites(self):
        '''
        Sets player sprite, currently on of 3 built in tanks sprites
        '''
        if self.nr == 1:
            self.sprite = pygame.image.load("img/tank_blue.png").convert_alpha()
            self.cannon_sprite = pygame.image.load("img/cannon.png").convert_alpha()
            self.cannon_angle = 5
        elif self.nr == 2:
            self.sprite = pygame.transform.flip(pygame.image.load("img/tank_green.png").convert_alpha(), True, False)
            self.cannon_sprite = pygame.image.load("img/cannon.png").convert_alpha()
            self.cannon_angle = 175
        else:
            self.sprite = pygame.image.load("img/tank_pink.png").convert_alpha()
            self.cannon_sprite = pygame.image.load("img/cannon.png").convert_alpha()
            self.cannon_angle = 5


    def set_cannon_angle(self, mouse_pos):
        '''
        Calculates the angle of the cannon sprite according to relative mouse position
        '''
        x_offset = mouse_pos[0] - self.pos[0]
        if x_offset > 0:
            self.cannon_angle = math.degrees(math.atan((self.pos[1] - mouse_pos[1]) / x_offset ))
        elif x_offset < 0:
            self.cannon_angle = 180 + math.degrees(math.atan((self.pos[1] - mouse_pos[1]) / x_offset))

        

class Projectile:
    '''
    Initiate projectile launch
    .trajectory .pos .velocity .inflight .collision
    '''
    def __init__(self):
        self.reset()


    def reset(self):
        '''
        Reset projectile parameters
        '''
        self.inflight = False
        self.collision = False
        self.hit = False
        self.pos = []
        self.velocity = []
        self.trajectory = []
        self.interp_traj = []
        self.col_checked = 0
        self.crater = []


    def launch(self, player, mouse_pos):#, start_velocity):
        '''
        Calculates velocity from relative mouse position and fires projectile
        '''
        self.reset()
        self.inflight = True
        
        self.pos = copy.copy(player.pos)
        self.pos[1] = self.pos[1] - 13 # Correction to center on tank sprite
        self.trajectory = [self.pos] # Start position in trajectory list
        self.interp_traj = [self.pos]
        
        self.velocity = [INPUT_SCALE * (mouse_pos[0] - player.pos[0]),
                         INPUT_SCALE * (mouse_pos[1] - player.pos[1])]


    def increment(self):
        '''
        Increment projectile position by one timestep.
        '''
        dt = TIME_SCALE / TICKRATE
        position = copy.copy(self.trajectory[-1])
        velocity = self.velocity
        position[0] = position[0] + velocity[0] * dt
        position[1] = position[1] + velocity[1] * dt
        velocity[1] = velocity[1] - GRAVITY * dt
        self.velocity = velocity
        self.trajectory.append(position)
        self.interp_traj.extend(self.interpolate(self.trajectory[-2:]))
        
    
    def interpolate(self, points):
        '''
        Get value of trajectory for every x coordinate, to be able to do accurate collision detection
        '''
        # Determine interpolated function
        slope = (points[1][1] - points[0][1]) / (points[1][0] - points[0][0])
        const = points[0][1] - slope * points[0][0]
        # function: round(const + slope * i, 2)

        # Calculate graph of interpolated function in between points
        graph = []
        if self.velocity[0] >= 0:
            for i in range(int(points[0][0]) + 1, int(points[1][0]) + 1):
                graph.append([i, const + slope * i])
        else:
            for i in range(int(points[0][0]), int(points[1][0]), -1):
                graph.append([i, const + slope * i])
        #print(points)
        #print(slope)
        #print("Raak: ", graph)
        return graph

    
    def check_collision(self, world):
        '''
        Check for collision with world.
        in case of projectile out of bounds, left or right edge of the screen, set .inflight:False.
        In case of collision set .inflight:False and .collision:True and calculate coordinates of crater.
        '''
        for i in self.interp_traj[self.col_checked:]:
            self.col_checked = len(self.interp_traj)
            
            # When out of bounds
            if i[0] < 0 or i[0] >= HRES:
                self.inflight = False
                return
            
            # When collision with ground
            elif i[1] >= world.ground[i[0]][1]:
                self.crater = world.ground[i[0]]
                self.collision = True
                self.inflight = False
                print("Crater:", self.crater)
                return
            

    def check_hit(self, target, blast_size=25):
        '''
        Call in case of collision. Check if target coordinates have been hit
        '''
        if sum((np.array(target, dtype=float) - np.array(self.crater)) ** 2) < (blast_size ** 2) :
            self.hit = True
            return True
        else :
            return False

    
    # Partial implementation of rolling bomb weapon
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
            while (posx_int + (i + 5)) < HRES :
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
                while (posx_int + (i + 5)) < HRES :
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


class Blast:
    kaboom = 0
    kaboomfactor = KABOOMCONSTANT

    @classmethod
    def reset(cls):
        cls.kaboom = 0
        cls.kaboomfactor = KABOOMCONSTANT

    @classmethod
    def small(cls, crater, blastsize):
        if cls.kaboom < blastsize :
            cls.kaboom += 2
            pygame.draw.circle(screen, CRATER_COLOR, crater, radius=cls.kaboom)
        else :
            pygame.draw.circle(screen, CRATER_COLOR, crater, radius=blastsize)
    
    @classmethod
    def big(cls, crater):
        global state
        cls.kaboom += cls.kaboomfactor
        cls.kaboomfactor *= 0.997
        pygame.draw.circle(screen, CRATER_COLOR, crater, radius=cls.kaboom)
        if cls.kaboom > HRES :
            cls.kaboom = 0
            cls.kaboomfactor = KABOOMCONSTANT
            state.init_new = True

    

class Menu:
    '''
    Contains a method for each gamemenu
    '''
    playerselect = 1
    count = 0
    p1name = ''
    p2name = ''
    cursor = 1
    cursor_count = 0

    @classmethod
    def cursor_blink(cls):
        '''
        Makes the cursor blink
        '''
        cls.cursor_count += 2
        if cls.cursor_count >= 2 * TICKRATE:
            cls.cursor_count = 0
        cls.cursor = cls.cursor_count // TICKRATE

    # This is not used
    '''
    @classmethod
    def typing(cls, char) :
        alfabet = string.ascii_letters
        cap = pygame.key.get_pressed()[pygame.K_LSHIFT] | pygame.key.get_pressed()[pygame.K_RSHIFT]
        if 96 < char & char < 96 + len(alfabet) :
            char = char - 97
            char = alfabet[char + cap * 26]
        #elif char == 32 :
        #    char = ' '
        else :
            char = ''
        return char
    '''

    @classmethod 
    def title(cls, surface):
        '''
        Draw Title screen
        '''
        state.pause = False
        for event in pygame.event.get() :
            # Key event    
            if event.type == pygame.KEYDOWN :
                
                if event.key == pygame.K_RETURN :
                    state.setup_menu = True
                    state.title_menu = False
                
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            
            if event.type == pygame.QUIT:
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN :
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0]:
                    state.setup_menu = True
                    state.title_menu = False

        pygame.Surface.fill(surface, (0, 0, 0))
        textrect = draw_text(surface, 'Tank Duel', title_font, RED, (HRES // 2), (VRES // 4), x_side="center")
        textrect = draw_text(surface, '(Click to start)', font_small, RED, (HRES // 2), (textrect.bottom + 5), x_side="center", y_side="top")
        textrect = draw_text(surface, 'Kasper Vloon, 2023', font_small, DARKGREY, (HRES - 10), (VRES -10), x_side="right")
        pygame.display.flip()

    @classmethod
    def victory(cls, surface, winner):
        '''
        Draw Victory screen
        '''
        for event in pygame.event.get() :
            # Key event    
            if event.type == pygame.KEYDOWN :
                
                if event.key == pygame.K_r:
                    state.victory = False
                    state.pause = False
                    state.reset_score = True
                    
                if event.key == pygame.K_n:
                    state.victory = False
                    state.pause = False
                    state.setup_menu = True

                if event.key == pygame.K_ESCAPE:
                    state.victory = False
                    state.pause = False
                    state.title_menu = True

                if event.key == pygame.K_ESCAPE:
                    pass
            
            if event.type == pygame.QUIT:
                sys.exit()


        pygame.Surface.fill(surface, (0, 0, 0))
        
        # Victory message
        textrect = draw_text(surface, f"{winner.name} WINS!", title_font, winner.color, (HRES // 2), (VRES // 4), x_side="center")

        # Line 1
        textrect = draw_text(surface, "[r]", font1, GREY, textrect.centerx - 140, textrect.bottom + 120, x_side="left")
        textrect = draw_text(surface, "Rematch", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        # Line 2
        textrect = draw_text(surface, "[n]", font1, GREY, textrect.left - 160, textrect.bottom + 40, x_side="left")
        textrect = draw_text(surface, "New Game", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        # Line 3
        textrect = draw_text(surface, "[Esc]", font1, GREY, textrect.left - 160, textrect.bottom + 40, x_side="left")
        textrect = draw_text(surface, "Exit to Title", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        pygame.display.flip()      


    @classmethod
    def pause(cls, surface):
        '''
        Pause screen
        '''

        for event in pygame.event.get() :
            # Key event    
            if event.type == pygame.KEYDOWN :
                
                if event.key in [pygame.K_PAUSE, pygame.K_p]:
                    state.pause = False

                if event.key == pygame.K_n:
                    state.pause = False
                    state.setup_menu = True

                if event.key == pygame.K_ESCAPE:
                    state.pause = False
                    state.title_menu = True
            
            if event.type == pygame.QUIT:
                sys.exit()


        pygame.Surface.fill(surface, (0, 0, 0))
        
        # Pause message
        textrect = draw_text(surface, "Game paused", font2, RED, (HRES // 2), (VRES // 4), x_side="center")

        # Line 1
        textrect = draw_text(surface, "[p]", font1, GREY, textrect.centerx - 140, textrect.bottom + 120, x_side="left")
        textrect = draw_text(surface, "Continue", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        # Line 2
        textrect = draw_text(surface, "[n]", font1, GREY, textrect.left - 160, textrect.bottom + 40, x_side="left")
        textrect = draw_text(surface, "New Game", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        # Line 3
        textrect = draw_text(surface, "[Esc]", font1, GREY, textrect.left - 160, textrect.bottom + 40, x_side="left")
        textrect = draw_text(surface, "Exit to Title", font1, GREY, textrect.left + 160, textrect.bottom, x_side="left")

        pygame.display.flip() 


    @classmethod
    def setup(cls, surface, p1, p2) :   # Draw setup screen
        
        
        if cls.playerselect == 1:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    sys.exit()

                    # Key event
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state.title_menu = True
                        state.setup_menu = False
                        cls.playerselect = 1
                        return

                    if event.key == pygame.K_PAUSE:
                        if state.pause == True:
                            # If state is pause game
                            state.menu = False
                            state.setup_menu = False
                            return
                        
                    # If down key go to p2 select
                    if event.key == pygame.K_DOWN:
                        if cls.p1name:
                            p1.name = cls.p1name
                        cls.playerselect = 2
                    # If backspace
                    if event.key == 8 :
                        cls.p1name = cls.p1name[:-1]
                    # If space
                    elif event.key == 32:
                        cls.p1name = cls.p1name + ' '
                        cls.p1name = cls.p1name[:10]
                    # If unicode
                    else :
                        char = event.unicode
                        char = char.strip()
                        cls.p1name = cls.p1name + char
                        cls.p1name = cls.p1name[:10]
                    # When press ENTER: Set P1 name if typed name != empty
                    # and change selector to p2
                    if event.key == pygame.K_RETURN:
                        #if cls.p1name:
                            #p1.name = cls.p1name
                        cls.playerselect = 2
                    
                       
        elif cls.playerselect == 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                # Key event    
                if event.type == pygame.KEYDOWN :
                    if event.key == pygame.K_ESCAPE:
                        state.title_menu = True
                        state.setup_menu = False
                        cls.playerselect = 1
                        return
                        
                    if event.key == pygame.K_PAUSE:
                        if state.pause == True:
                            # If state is pause game
                            state.menu = False
                            state.setup_menu = False
                            return
                        
                    # If up key go to p1 select
                    if event.key == pygame.K_UP:
                        if cls.p2name:
                            p2.name = cls.p2name
                        cls.playerselect = 1
                        
                    if event.key == 8 :
                        cls.p2name = cls.p2name[:-1]
                        # If space
                    elif event.key == 32:
                        cls.p1name = cls.p1name + ' '
                        cls.p1name = cls.p1name[:10]
                    else :
                        char = event.unicode
                        char = char.strip()
                        cls.p2name = cls.p2name + char
                        cls.p2name = cls.p2name[:10]
                    # When press ENTER: Set P1 name if typed name != empty
                    # exit menu and change selector back to p1
                    if event.key == pygame.K_RETURN:
                        p1.set_name(cls.p1name)
                        p2.set_name(cls.p2name)
                        cls.playerselect = 1
                        state.menu = False
                        state.setup_menu = False
                        state.init_new = True
                        state.reset_score = True
        
        pygame.Surface.fill(surface, (0, 0, 0)) 
        
        # Title line
        string = 'Name'
        text = font2.render(string, True, RED, (0,0,0))
        textrect = text.get_rect()
        textrect.left = HRES * 3 // 8
        textrect.bottom = VRES // 6
        surface.blit(text, textrect)

        string = '' #'Color'
        text = font2.render(string, True, RED, (0,0,0))
        textrect = text.get_rect()
        textrect.left = HRES * 5 // 8
        textrect.bottom = VRES // 6
        surface.blit(text, textrect)
        
        # Player 1 line
        string = 'Player {}'.format(p1.nr)
        text = font2.render(string, True, p1.color, (0,0,0))
        text2rect = text.get_rect()
        text2rect.left = HRES // 8
        text2rect.top = textrect.bottom + 20
        surface.blit(text, text2rect)
        
        string = cls.p1name[:10] + '_' * cls.cursor if cls.playerselect == 1 else cls.p1name[:10]
        text = font2.render(string, True, p1.color, (0,0,0))
        text2rect = text.get_rect()
        text2rect.left = HRES * 3 // 8
        text2rect.top = textrect.bottom + 20
        surface.blit(text, text2rect)

        # Player 2 line
        string = 'Player {}'.format(p2.nr)
        text = font2.render(string, True, p2.color, (0,0,0))
        text3rect = text.get_rect()
        text3rect.left = HRES // 8
        text3rect.top = text2rect.top + 60
        surface.blit(text, text3rect)
        
        string = cls.p2name[:10] + '_' * cls.cursor if cls.playerselect == 2 else cls.p2name[:10]
        text = font2.render(string, True, p2.color, (0,0,0))
        text3rect = text.get_rect()
        text3rect.left = HRES * 3 // 8
        text3rect.top = text2rect.top + 60
        surface.blit(text, text3rect)

        pygame.display.flip() 



class Frame_counter:
    # Setup fps counter

    def __init__(self):
        '''
        Initiate at 0
        '''
        self.frame_count = 0
        self.frame_time_sum = 0
        self.frame_time_avg = 0
        self.fps_avg = 0
        self.update_interval = TICKRATE // 2

    def update(self):
        '''
        Update average framerate over 'update_interval' nr of frames
        '''
        frame_time = int(clock.get_time())
        if self.frame_count < self.update_interval:
            self.frame_count += 1
            self.frame_time_sum += frame_time
        else:
            ft = self.frame_time_sum / self.update_interval
            self.frame_time_avg = round(ft, 1)
            self.fps_avg = round(1000 / ft)
            self.frame_count = 0
            self.frame_time_sum = 0

    def draw_framerate(self, surface):  
        text = font_fps.render(f"{self.fps_avg} fps", True, GREEN, (0,0,0))
        textRect = text.get_rect()
        textRect.topleft = (10, 10)
        surface.blit(text, textRect)

    def draw_frametime(self, surface):
        text = font_fps.render(f"{self.frame_time_avg} ms", True, GREEN, (0,0,0))
        textRect = text.get_rect()
        textRect.topleft = (10, 10)
        surface.blit(text, textRect)



# Game methods

#simplify text drawing, not yet implemented everywhere
def draw_text(surface, string, font, color, x_pos, y_pos, *, x_side='left', y_side='bottom'):
    '''
    #### KeyArgs:
    [x_side]: 'left', 'right', 'center'
    [y_side]: 'bottom', 'top', 'center'
    '''
    text = font.render(string, True, color, (0,0,0))
    textrect = text.get_rect()

    match x_side:
        case 'left':
            textrect.left = x_pos
        case 'right':
            textrect.right = x_pos
        case 'center':
            textrect.centerx = x_pos
        case _:
            raise ValueError("Invalid value for keyword argument: [x_side]")

    match y_side:
        case 'bottom':
            textrect.bottom = y_pos
        case 'top':
            textrect.top = y_pos
        case 'center':
            textrect.centery = y_pos
        case _:
            raise ValueError("Invalid value for keyword argument: [y_side]")

    surface.blit(text, textrect)
    return textrect

        
def draw_score(surface, p1, p2):
    '''
    Draw scoreboard, showing player names and scores.
    '''

    # player 1
    string = p1.name + '  |'
    text = font1.render(string, True, p1.color)
    textrect = text.get_rect()
    textrect.topright = (HRES // 2, 10)
    surface.blit(text, textrect)

    string = str(p1.score)
    text = font2.render(string, True, p1.color)
    text2rect = text.get_rect()
    text2rect.top = textrect.bottom + 10
    text2rect.centerx = textrect.right - 60
    surface.blit(text, text2rect)
       
    # Player 2
    string = '|  ' + p2.name
    text = font1.render(string, True, p2.color)
    textrect = text.get_rect()
    textrect.topleft = (HRES // 2, 10)
    surface.blit(text, textrect)

    string = str(p2.score)
    text = font2.render(string, True, p2.color)
    text2rect = text.get_rect()
    text2rect.top = textrect.bottom + 10
    text2rect.centerx = textrect.left + 60
    surface.blit(text, text2rect)


def draw_cannon(player):
    '''
    Draw cannon part of player sprite in correct location and with correct angle
    '''
    cannon = pygame.transform.rotate(player.cannon_sprite, player.cannon_angle)
    w = cannon.get_width() // 2
    h = cannon.get_height() // 2
    if player.nr == 1:
        screen.blit(cannon, (player.pos[0] - w, player.pos[1] - h - 13))
        screen.blit(player.sprite, (player.pos[0] - 35, player.pos[1] - 28))
    elif player.nr == 2:
        screen.blit(cannon, (player.pos[0] - w, player.pos[1] - h - 13))
        screen.blit(player.sprite, (player.pos[0] - 28, player.pos[1] - 28))



if __name__ == "__main__":
    asyncio.run(main())
#   main()
