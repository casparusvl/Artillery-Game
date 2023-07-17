# Tank Dual CS50 final project
#### Video Demo:  <URL HERE>
#### Description:

## Tanks dual

This is a game in the style of the classic Scorched Earth. Both players control an artillery cannon on a randomly generates 2D landscape and can fire grenades at eachother.

### How to play:

#### Game menus:
At startup a title screen will be displayed. Click mouse button or press 'Enter' to continue.
Next is the setup screen. Both players will be able to select a Player name. If no name selected, default name (Player 1 and Player 2) will be used. Press enter to confirm name and start game. A randomly generated 2D world will be created and let the game begin!
During gameplay players can always pause the game and return to the setup screen by pressing 'Escape'. Pressing 'Escape' again will continue the game, while 'Enter' will start a new game with new Player names.

#### Gameplay:
Player 1 will start the game. Use the mouse to aim and determine the velocity of the shot. the further from the cannon, the further the shot will reach. Try to hit the other player to score a point! Be carefull though: If you hit yourself, your opponent's score will increase.
After your shot, it will be the other players turn and so on, until a hit is scored. At this point scored will be increased and a new world will be generated, so that the game can continue.
At any moment, a new game can be started by pressing 'N'.


### Technical documentation:


#### State class
Contains all Global gamestate variables. I choose to use a class instead of a dict, mainly because i found the dot syntax more convenient than dict lookup.

#### World class
Generate will randamly generate a terrain, which works as follows:
First create a numpy array with the horizontal resulution as size.
take a nr (n = MINSAMPLES) of random samples evenly spaced out over the array (with some upper and lower bounds for the y values), and perform a linear interpolation to fill the whole array.
double the nr of samples for a set number of iterations (n = ITERATIONS) and calculate a a weighted average of the resulting arrays.
De values of MINSAMPLES and ITERATIONS can be played experimented with.
MINSAMPLES = 3, ITERATIONS = 5 or MINSAMPLES = 5, ITERATIONS = 4 give results i like.

#### Player class
This contains the player objects. Currently 2 players are supported, but this could be extended without much difficulty.
Player name, Player color and Player sprite can be set.
Player posityion is automatically set with some random variation is x-position and the correct y-position according to the terrain.
It keeps track of player score and if the Player has been hit in the current round.
Contains a Player list and Player count as class variables.

#### Projectile class
Will launch a Projectile and contains it's trajectory.
Increment should be called every frame to increment projectile position with 1 timestep.
Contains the logic for collision and hit detection. Implementation of alternative projectile should be possible without much trouble.

#### Blast class
This class draws the explosion animations. Small explosion for impact, big explosion when player has been hit.

#### Menu class
Contains the game menu and title screen. One seperate function for each menu.

#### Frame counter class
A counter to show fps or frametime. Updates the average fps and frametime twice a second

#### draw_score function
Draws the scoreboard, showing Player names and scores.

#### draw_cannon
Draws the cannons on both player models, with the correct angle according to relative mouse position



#### Main function
Uses asyncio, as this is a requirement for Webassembly support, using Pygbag.




