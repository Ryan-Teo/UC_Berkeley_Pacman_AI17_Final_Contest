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
import distanceCalculator
import random, time, util, sys, math
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
							 first = 'ReflexCaptureAgent', second = 'ReflexCaptureAgent'):
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
	return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
	"""
	A base class for reflex agents that chooses score-maximizing actions
	"""
	def registerInitialState(self, gameState):
		self.start = gameState.getAgentPosition(self.index)
		self.food = float("inf")
		CaptureAgent.registerInitialState(self, gameState)

		#Find all coords with no walls
		noWalls = []
		walls = gameState.getWalls()
		#will create a list of all spaces with no walls
		for x in range(walls.width):
			for y in range(walls.height):
				if walls[x][y] is False:
					noWalls.append((x,y))
		self.notWalls = noWalls

	def chooseAction(self, gameState):
		"""
		Picks among the actions with the highest Q(s,a).
		"""
		actions = gameState.getLegalActions(self.index)

		# You can profile your evaluation time by uncommenting these lines
		# start = time.time()
		values = [self.evaluate(gameState, a) for a in actions]
		# print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

		maxValue = max(values)
		bestActions = [a for a, v in zip(actions, values) if v == maxValue]

		foodLeft = len(self.getFood(gameState).asList())

		successor = self.getSuccessor(gameState, random.choice(bestActions))
		foodList = self.getFood(successor).asList() 

		print "self.food, foodLeft, len(foodList)", self.food, foodLeft, len(foodList)

		if(len(foodList) < foodLeft):
			if self.food == float("inf"):
				self.food = 0
			self.food += 1
			print "ate a dot", len(foodList), foodLeft

		if not gameState.getAgentState(self.index).isPacman and self.food < 20:
			self.food = float("inf")
			print "deposited food"

		if foodLeft <= 2:
			bestDist = 9999
			for action in actions:
				successor = self.getSuccessor(gameState, action)
				pos2 = successor.getAgentPosition(self.index)
				dist = self.getMazeDistance(self.start, pos2)
				if dist < bestDist:
					bestAction = action
					bestDist = dist
			return bestAction

		return random.choice(bestActions)

	def getSuccessor(self, gameState, action):
		"""
		Finds the next successor which is a grid position (location tuple).
		"""
		successor = gameState.generateSuccessor(self.index, action)
		pos = successor.getAgentState(self.index).getPosition()
		if pos != nearestPoint(pos):
			# Only half a grid position was covered
			return successor.generateSuccessor(self.index, action)
		else:
			return successor

	def evaluate(self, gameState, action):
		"""
		Computes a linear combination of features and feature weights
		"""
		features = self.getFeatures(gameState, action)
		weights = self.getWeights(gameState, action)
		print "action, value", action, features*weights
		return features * weights

	def getFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		features = util.Counter()
		successor = self.getSuccessor(gameState, action)
		features['successorScore'] = self.getScore(successor)
		features['distanceToFood'] = 0
		features['distanceToHome'] = 0

		features = util.Counter()
		successor = self.getSuccessor(gameState, action)
		foodList = self.getFood(successor).asList() 
		currentFoodList = self.getFood(gameState).asList() 

		# Compute distance to the nearest food

		if len(foodList) > 0: # This should always be True,  but better safe than sorry
			myPos = successor.getAgentState(self.index).getPosition()
			minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
			distanceToHome = self.getMazeDistance(self.start, myPos)
			if self.food == float("inf") or self.food == 0:
				features['distanceToFood'] = minDistance
				print "going for food"
			else:
				features['distanceToHome'] = distanceToHome
				print "going home"

		if not len(foodList) == len(currentFoodList):
			features['food'] = 1
		elif self.food == float("inf"):
			features['food'] = 0 

		return features

	def getWeights(self, gameState, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0, 'distanceToHome': -10, 'distanceToFood': -10, 'food': 50}

	def balikKampung(self, gameState):
		safeCoords = []
		width, height = gameState.data.layout.width, gameState.data.layout.height
		homeLine = width/2
		if not self.red:
			homeLine -= 1
		for y in range(0, height):
			if (homeLine,y) in self.noWalls:
				safeCoords.append((homeLine,y))
		if safeCoords:
			return goToCoords(getClosestCoord(safeCoords, gameState), gameState)
		return None #check for none

	def highlightEnemy(self, gameState):
		enemies = []
		for enemy in self.getOpponents(gameState):
			coord = gameState.getAgentPosition(enemy)
			if coord != None:
				enemies.append(coord)
		CaptureAgent.debugDraw(self,enemies,[1,0,0], clear = True)
		return enemies

	def goToCoord(self, grace, gameState):
	#Could edit this to take into account weights
		x,y = grace
		currentCoord = currentX, currentY = gameState.getAgentState(self.index).getPosition()
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

	def enemyClosestDist(self, gameState):
		enemies = self.enemyCoord(self, gameState)
		myPos = gameState.getAgentPosition(self.index)
		closest = None
		if len(enemies) != 0:
			for enemy in enemies:
				distance = self.getMazeDistance(myPos, enemy)
				if distance < closest or closest == None:
					closest = distance
		return closest

	def jiakBaBui(self, gameState):
		#return boolean
		jiakLo = False
		oldGameState = self.getPreviousObservation()
		if CaptureAgent.getFood(self, oldGameState)<CaptureAgent.getFood(self, gameState):
			jiakLo = True
		return jiakLo
