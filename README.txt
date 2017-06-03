Outline of approach:
	When game starts, agents will race towards the center
	Both agents are to begin collecting food
	If an enemy enters base, agents will chase enemy
	If agent is pacman and enemy is within sight range, agent will return to base

Techniques used:
	Food Collection:
		When possible, agents will stay an average set distance away from each other to prevent them getting the same food
		Both agents begin by only collecting one food at a time, but when a certain score is reached, one agent will increase food collection to three
		If agents are only supposed to collect one food, but there is a pellet directly next to the one just collected, pacman will collect that one as well

	Enemy within range in base (i.e. enemy is pacman): 
		When agents sense that their food is disappearing, they will come back to base and chase the enemy
		If agents see enemy within range on their side, they will abort food collection and priority is given to killing enemy

	Enemy within range in enemy territory (i.e. enemy is ghost):
		When collecting food, agents are to run back to centre line and ignore food if an enemy is sensed nearby
		If agent has eaten power capsule, the feature of ‘escape’ is ignored while the scared timer is above zero
		When running away, pacman will avoid any coordinates that are surrounded by 3 walls (i.e. a dead end)

Strengths:
	We have not delegated only one agent to attack and the other to defense. Both agents are capable of protecting and also eating food. This allows for a more dynamic AI approach
	Agents change amount of food to be eaten at one time according to the winning strategy
	We coded different strategies and chose the best one

Weaknesses:
	Many strategies we had originally planned for were unable to be implemented as our coding knowledge was not advanced enough to do so
	A Pacman can only see a dead end if the coordinate is adjacent to it 