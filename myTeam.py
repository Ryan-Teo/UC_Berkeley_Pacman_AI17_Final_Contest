# baselineTeam.py
# ---------------
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


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys, math
from game import Directions
import game
from util import nearestPoint

STARTING_FOOD = float("-inf")

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
							 first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
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
		self.food = STARTING_FOOD
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

		self.myFood = None
		if self.red:
			self.myFood = gameState.getRedFood().asList()
		else:
			self.myFood = gameState.getBlueFood().asList()

		self.missingFood = None
		self.onDefence = False

		self.onStart = True

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

		isPacman = gameState.getAgentState(self.index).isPacman

		# increment when food is eaten
		if(len(foodList) < foodLeft):
			if self.food == STARTING_FOOD:
				self.food = 0
			self.food += 1

		# when food is deposited as well as 1st started
		if not isPacman and self.food < float("inf"):
			self.food = STARTING_FOOD

		# check if there is any enemy is our base
		enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
		invaders = [a for a in enemies if a.isPacman]
		if not invaders:
			self.onDefence = False
			self.missingFood = None
		else:
			self.onDefence = True

		# make it false once it passes the border
		if self.onStart:
			if isPacman:
				self.onStart = False

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

		print "GO ", random.choice(bestActions)
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
		return features

	def getWeights(self, gameState, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0}

	def highlightEnemy(self, gameState):
		myPos = gameState.getAgentState(self.index).getPosition()
		enemies = []
		for enemy in self.getOpponents(gameState):
			coord = gameState.getAgentState(enemy).getPosition()
			if coord != None:
				enemies.append(coord)
		# CaptureAgent.debugDraw(self,enemies,[1,0,0], clear = True)
		return enemies

	def getClosestCoord(self, coordList, gameState):
		currentPosition = gameState.getAgentState(self.index).getPosition()
		minCoord = None
		minDist = float('inf')
		for coord in coordList:
			if self.getMazeDistance(currentPosition, coord) < minDist:
				minCoord = coord
				minDist = self.getMazeDistance(currentPosition, coord)
		# CaptureAgent.debugDraw(self,[minCoord], [1,1,1], clear = False) #REMOVE
		return minCoord, minDist

	def enemyCoord(self, gameState):
		enemies = []
		for enemy in self.getOpponents(gameState):
			coord = gameState.getAgentPosition(enemy)
			if coord != None:
				enemies.append(coord)
		return enemies

	def enemyClosestDist(self, gameState):
		enemies = self.enemyCoord(gameState)
		myPos = gameState.getAgentPosition(self.index)
		closest = None
		if len(enemies) != 0:
			for enemy in enemies:
				distance = self.getMazeDistance(myPos, enemy)
				if distance < closest or closest == None:
					closest = distance
		return closest

	def capsuleDist(self, gameState):
		capsules = CaptureAgent.getCapsules(self, gameState)
		capsuleCoord, capsuleDist = self.getClosestCoord(capsules, gameState)
		return capsuleCoord, capsuleDist

	def enemyOnOurSide(self, gameState):
		missingFood = None
		if self.red:
			redFood = gameState.getRedFood().asList()
			if len(redFood) < len(self.myFood):
				for food in self.myFood:
					if food not in redFood:
						missingFood = food
						self.myFood = redFood
		else:
			blueFood = gameState.getBlueFood().asList()
			if len(blueFood) < len(self.myFood):
				for food in self.myFood:
					if food not in blueFood:
						missingFood = food
						self.myFood = blueFood
		return missingFood
		
	def closestAgent(self, gameState, targetPos):
		#for missingFood, check if return value == self.index
		if targetPos is None:
			return False
		else:
			myTeam = self.getTeam(gameState)
			teamDist = []
			for teamMate in myTeam:
				distToEnemy = self.getMazeDistance(gameState.getAgentPosition(teamMate),targetPos)
				teamDist.append((teamMate, distToEnemy))
			closestAgent = min(teamDist, key= lambda x:x[1])[0]
			return closestAgent

	def getGeneralFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		features = util.Counter()
		successor = self.getSuccessor(gameState, action)
		foodList = self.getFood(successor).asList() 
		currentFoodList = self.getFood(gameState).asList() 
		myPos = successor.getAgentState(self.index).getPosition()

		features['successorScore'] = self.getScore(successor)
		features['distanceToFood'] = 0
		features['distanceToHome'] = 0
		features['stop'] = 0

		# if food is there
		if not len(foodList) == len(currentFoodList):
			features['food'] = 1
		elif self.food == STARTING_FOOD:
			features['food'] = 0 

		# always prevent stopping
		if action == 'Stop':
			features['stop'] = 1

		# convert my position from float to int to check if it has food
		floatX, floatY = myPos
		myIntPos = (int(floatX), int(floatY))
		if myIntPos in currentFoodList:
			features['eatTheFood'] = 1
			print "eat the food"

		# only check when agent is pacman or about to become pacman
		isPacman = gameState.getAgentState(self.index).isPacman
		isGoingToBePacman = successor.getAgentState(self.index).isPacman
		if isPacman or isGoingToBePacman:
			enemies = self.highlightEnemy(gameState)
			print "enemies around", enemies
			if enemies:
				features['eatTheFood'] = 0
				print "running for life"

			enemyDanger = self.enemyClosestDist(successor)	
			if(enemyDanger != None):
				if(enemyDanger <= 4):
					features['escape'] = 8/enemyDanger
				elif(enemyDanger <= 8):
					features['escape'] = 1
				else:
					features['escape'] = 0  
			
			if features['escape'] != 0:
				features['eatTheFood'] = 0
		
			capsuleCoord, capsuleDist = self.capsuleDist(gameState)
			
			if capsuleDist < enemyDanger:
				features['getCapsule'] = 1

		return features

	def getDefenceFeatures(self, gameState, action):
		# if our food is being eaten
		print "GO DEFENSE"
		features = util.Counter()	
		successor = self.getSuccessor(gameState, action)

		myState = successor.getAgentState(self.index)
		myPos = myState.getPosition() 

		# Computes whether we're on defense (1) or offense (0)
		features['onDefense'] = 1
		if myState.isPacman: features['onDefense'] = 0

		# Computes distance to invaders we can see
		enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
		invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
		features['numInvaders'] = len(invaders)
		if len(invaders) > 0:
			dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
			features['invaderDistance'] = min(dists)

		if action == Directions.STOP: features['stop'] = 1
		rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
		if action == rev: features['reverse'] = 1

		if self.missingFood:
			features["distanceToMissingFood"] = self.getMazeDistance(self.missingFood, myPos)

		return features

class OffensiveReflexAgent(ReflexCaptureAgent):
	"""
	A reflex agent that seeks food. This is an agent
	we give you to get an idea of what an offensive agent might look like,
	but it is by no means the best or only way to build an offensive agent.
	"""
	def getFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		successor = self.getSuccessor(gameState, action)
		features = self.getGeneralFeatures(gameState, action)
		foodList = self.getFood(successor).asList() 

		missingFood = self.enemyOnOurSide(gameState)
		myState = successor.getAgentState(self.index)
		myPos = myState.getPosition()

		if missingFood and not self.missingFood == missingFood:
			self.missingFood = missingFood
			# check if this agent is closer
			closestAgent = self.closestAgent(gameState, self.missingFood)
			if self.index == closestAgent:
				self.onDefence = True
				features = self.getDefenceFeatures(gameState, action)
				return features

		# Compute distance to the nearest food

		if len(foodList) > 0: # This should always be True,  but better safe than sorry
			myPos = successor.getAgentState(self.index).getPosition()
			if self.onStart:
				minDistance = self.second_smallest([self.getMazeDistance(myPos, food) for food in foodList])
			else:
				minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
			distanceToHome = self.getMazeDistance(self.start, myPos)
			if self.food == STARTING_FOOD or self.food < 1:
				features['distanceToFood'] = minDistance
			else:
				features['distanceToHome'] = distanceToHome

		return features

	def getWeights(self, gameState, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0, 'distanceToHome': -10, 'distanceToFood': -10, 'distanceToMissingFood': -10,
				'food': 50, 'stop': -100, 'eatTheFood': 100, 'escape': -500, 'getCapsule':1000,
				'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'reverse': -2}

	def second_smallest(self, numbers):
		m1, m2 = float('inf'), float('inf')
		for x in numbers:
			if x <= m1:
				m1, m2 = x, m1
			elif x < m2:
				m2 = x
		return m2

class DefensiveReflexAgent(ReflexCaptureAgent):
	"""
	A reflex agent that keeps its side Pacman-free. Again,
	this is to give you an idea of what a defensive agent
	could be like.  It is not the best or only way to make
	such an agent.
	"""
	def getFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		successor = self.getSuccessor(gameState, action)
		features = self.getGeneralFeatures(gameState, action)
		foodList = self.getFood(successor).asList() 

		missingFood = self.enemyOnOurSide(gameState)
		myState = successor.getAgentState(self.index)
		myPos = myState.getPosition()

		if missingFood and not self.missingFood == missingFood:
			self.missingFood = missingFood
			# check if this agent is closer
			closestAgent = self.closestAgent(gameState, self.missingFood)
			if self.index == closestAgent:
				self.onDefence = True
				features = self.getDefenceFeatures(gameState, action)
				return features

		if self.onDefence:
			return self.getDefenceFeatures(gameState, action)

		# Compute distance to the nearest food

		if len(foodList) > 0: # This should always be True,  but better safe than sorry
			myPos = successor.getAgentState(self.index).getPosition()
			minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
			distanceToHome = self.getMazeDistance(self.start, myPos)
			if self.food == STARTING_FOOD or self.food < 1:
				features['distanceToFood'] = minDistance
			else:
				features['distanceToHome'] = distanceToHome

		return features

	def getWeights(self, gameState, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0, 'distanceToHome': -10, 'distanceToFood': -10, 'distanceToMissingFood': -10,
				'food': 50, 'stop': -100, 'eatTheFood': 100, 'escape': -500, 'getCapsule':1000}
