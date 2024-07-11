# Tank Duel CS50 final project
#### Video Demo:  <URL HERE>
#### Description:

## Tank duel

This is a proof of concept for a game in the style of the classic Scorched Earth. Both players control a tank, placed on a randomly generated 2D landscape, and the goal is to destroy eachother's tank.
The game is written in Python using the Pygame framework and can run both locally or in a web browser through Webassembly.

### How to play:

#### Game menus:
At startup the title screen will be displayed. Click mouse button or press 'Enter' to continue.
Next is the setup screen. Both players will be able to input a Player name. If no name is selected, default names (Player 1 and Player 2) will be used. Press enter to confirm name and start game. A randomly generated 2D world will be created and let the game begin!
During gameplay players can always pause the game and return to the setup screen by pressing 'p' or 'Escape'. From the pause menu it's possible to start a new game

#### Gameplay:
Player 1 will start the game. Use the mouse to aim and determine the velocity of the shot. the further from the cannon you click, the further the shot will reach. Try to hit the other player to score a point! Be carefull though: Don't hit yourself!
After your shot, it will be the other players turn and so on, until a hit is scored. At this point the surviving Player will get a point and a new world will be generated, so that the game can continue.
First player to reach 3 kills wins the game!


### Technical documentation:

#### State class
Contains all Global gamestate variables as class variables. 

#### World class
Contains the playing field.
Generate will randomly generate a terrain, which works as follows:
First create a numpy array with the horizontal resulution as size.
take a nr (n = MINSAMPLES) of random samples evenly spaced out over the array (with some upper and lower bounds for the y values), and perform a linear interpolation to fill the array.
double the nr of samples for a set number of iterations (n = ITERATIONS) and calculate a weighted average of the resulting arrays.
The values of MINSAMPLES and ITERATIONS can be experimented with.
I've settled on MINSAMPLES = 5, ITERATIONS = 4.
MINSAMPLES = 3, ITERATIONS = 5 also givea a result i like.

#### Player class
This represents the player objects. Currently 2 players are supported, but this could be extended without much difficulty.
Player name, Player color and Player sprite can be set.
Player position is automatically set with some random variation in the x-position and the correct y-position according to the terrain.
Calculates the correct angle of the cannon for the active player, according to the relative mouse cursor position.
Keeps track of the player score.

#### Projectile class
Will launch a Projectile and calculate it's trajectory.
Increment should be called every frame when a projectile is in flight, to increment projectile position with 1 timestep.
Contains the logic for collision and hit detection. Implementation of alternative projectile should be possible without much trouble. I've started the implementation of a rolling bomb, but this hasn't been finished yet.

#### Blast class
This class draws the explosion animations. Small explosion for a normal impact, big explosion when a player has been hit.

#### Menu class
Used as a namespace for the game menus and title screen. One seperate function for each menu. This is not a very elegant design, but it's sufficient for now.
Has functions for typing input and to make the cursor blink.

#### Frame counter class
A counter to show framerate or frametime. Keeps track of a half-second average framerate and frametime in ms, and updates it twice a second.
Seperate draw functions for framerate and frametime.

#### draw_text function
A function to draw a line of text with speecified font, color and coordinates.

#### draw_score function
Draws the scoreboard, showing Player names and scores.

#### draw_cannon function
Draws the cannons on both player models, with the correct angle according to relative mouse position.
The actual angle of the cannon is stored in the player objects.

#### Main function
I've used the Pygbag module to compile the game to Webassembly so it can be run in a browser. To get this to work it was necessary to use asyncio.
Pygame.time.Clock.tick is use for the game clock.
screen resolution is configurable. The game will run well in a wide range of resolutions, but the sprites and and animations won't scale as they are based on fixed pixel sizes.
TICKRATE determines the target framerate the game will run on. Projectile physics will be consistent independent of tickrate, but speed of explosion animations might change.
If target framerate is not maintainable, game speed will slow down.


### New feauture ideas

#### Weapon types
Rolling bomb, homing missile etc.

#### Wind 
Wind that effects the weapon trajectory. The challenge here is to make a nice visual representation, e.g. a moving flag or clouds.

#### CPU controlled player AI
It might be  be interesting to create a AI so the game can be played against the computer.


