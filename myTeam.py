# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import math

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'anton', second = 'harry'):
    #anton on top
    #harry on bottom
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class SecretAgent(CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """
    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on).

        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)

        IMPORTANT: This method may run for at most 15 seconds.
        """

        '''
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py.
        '''
        CaptureAgent.registerInitialState(self, gameState)

        '''
        Your initialization code goes here, if you need any.
        '''
        
        #     Is basic formula for colour debugging:
        #     CaptureAgent.debugDraw(self,cells, [1,0,0], clear=False)
        
        
        if self.red and not self.red == None:
            #if on red team
            print "I'm red! -- remove"
        elif not self.red == None:
            #if on blue team
            print "I'm blue! -- remove"
        else:
            print "Identity crisis --------------  WHAT !!!!????"
            #something went wrong
    
        noWalls = []
        walls = gameState.getWalls()
    
        #will create a list of all spaces with no walls
        for x in range(walls.width):
            for y in range(walls.height):
                if walls[x][y] is False:
                    noWalls.append((x,y))
        self.notWalls = noWalls
    
        self.hover(gameState)
        
    
    def centreToFood(self):
        """This section is to find the shortest path from base line
        to the closest food on enemy side, while splitting y in two"""
                
        food = CaptureAgent.getFood(self, gameState)
        foodListTop = []
        foodListBottom = []
        for x in range(food.width):
            for y in range(food.height):
                if (food[x][y]):
                    if y > food.height/2-1:
                        foodListTop.append((x,y))
                    else:
                        foodListBottom.append((x,y))    
        
        if self.red:
            centreSafeLine = food.width/2 - 1    
        else:
            centreSafeLine = food.width/2
        
        if foodListTop != None:
            foodTarget = foodListTop[0]
            bestDistance = None
            bestDistanceCoord = []
            for y in range(food.height/2, food.height):
                
                if not gameState.hasWall(centreSafeLine, y): 
                    temp = self.getMazeDistance((centreSafeLine, y), foodTarget)
                    if bestDistance == None or temp < bestDistance:
                        bestDistance = temp
                        bestDistanceCoord= (centreSafeLine, y)
                        
#         Debugging:
#         CaptureAgent.debugDraw(self,[foodTarget], [1,0,0], clear=False)
#         CaptureAgent.debugDraw(self,[bestDistanceCoord], [1,0,0], clear=False)
        
        
    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        '''
        You should change this in your own agent.
        '''

        return self.hover(gameState)
    
    
    #Get all legal positions (no walls)
    	#Split red and blue side
    	#Add food reward (value = 1)
    	#Initial power capsule reward (value = -99)
    	#When ghost within 5 block radius, change power capsule reward (value = 99)
    #Agent stuff
    	#If agent not enemy, agent.isPacman == true, agent is on enemy side
    #goHome -- shortest distance back to friendly side

    def goToCoord(self, (x,y), gameState):
        #Could edit this to take into account weights
        currentCoord = currentX, currentY = gameState.getAgentState(self.index).getPosition()
        print self.name, currentCoord
        targetPosition = (x,y)
        actions = gameState.getLegalActions(self.index)
        bestActions = []
        bestAction = None
        nextCoord = None
        for action in actions:
            print action
            if action == "North":
                nextCoord = (currentX,currentY+1)
            elif action == "East":
                nextCoord = (currentX+1,currentY)
            elif action == "South":
                nextCoord = (currentX,currentY-1)
            elif action == "West":
                nextCoord = (currentX-1,currentY)
            else:
                bestAction = action
                continue
            if self.getMazeDistance(nextCoord, targetPosition) < self.getMazeDistance(currentCoord, targetPosition):
                bestAction = action
                bestActions.append((action, self.getMazeDistance(nextCoord, targetPosition)))
        if bestActions:
            print "ACTION!!!"
            bestAction = max(bestActions, key= lambda x:x[1])[0]
        else:
            print "NO ACTION!!!----------"
        return bestAction
        
        
    
    def getClosestCoord(self, coordList, gameState):
        currentPosition = gameState.getAgentState(self.index).getPosition()
        minCoord = None
        minDist = float('inf')
        for coord in coordList:
            if self.getMazeDistance(currentPosition, coord) < minDist:
                minCoord = coord
                minDist = self.getMazeDistance(currentPosition, coord)
        CaptureAgent.debugDraw(self,[minCoord], [1,1,1], clear = False) #REMOVE
        return minCoord, minDist

class anton(SecretAgent):
    #Top agent
    def hover(self, gameState):
        self.top = True
        self.name = "anton"
        print "myTeam - anton"
        getOpenings(self, gameState)
        if self.red:
            CaptureAgent.debugDraw(self,self.hoverCoords, [1,0.5,0], clear = False) #REMOVE
        else:
            CaptureAgent.debugDraw(self,self.hoverCoords, [0,0.5,1], clear = False) #REMOVE
        closestCoord, distance = SecretAgent.getClosestCoord(self, self.hoverCoords, gameState)
        return SecretAgent.goToCoord(self, closestCoord, gameState)
        
class harry(SecretAgent):
    #Bot agent
    def hover(self, gameState):
        self.top = False
        self.name = "harry"
        print "myTeam - harry"
        getOpenings(self, gameState)
        if self.red:
            CaptureAgent.debugDraw(self,self.hoverCoords, [1,0.1,0], clear = False) #REMOVE
        else:
            CaptureAgent.debugDraw(self,self.hoverCoords, [0,0.9,1], clear = False) #REMOVE
        closestCoord, distance = SecretAgent.getClosestCoord(self, self.hoverCoords, gameState)
        return SecretAgent.goToCoord(self, closestCoord, gameState)

def getOpenings(self, gameState):
    #sets hover coordinates for each agent
    openingCoords = [] #list of coordinated within 
    notWalls = self.notWalls
    walls = gameState.getWalls()
    x = walls.width
    y = walls.height
    hoverWidth = 3
    midHeight =int(math.floor(y/2))
    midBoard = int(math.floor(x/2))
    if self.red:
        hoverLine = midBoard - hoverWidth
    else:
        hoverLine = midBoard + hoverWidth -1
    if self.top is True:
        # for top agent
        i = hoverLine
        for j in range(midHeight, y):
            if (i,j) in notWalls:
                openingCoords.append((i,j))
    else:
        #for bot agent
        i = hoverLine
        for j in range(0, midHeight):
            if (i,j) in notWalls:
                openingCoords.append((i,j))
    self.hoverCoords = openingCoords
