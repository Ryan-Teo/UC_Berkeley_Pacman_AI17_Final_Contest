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

#USEFUL GLOBAL VARIABLES
STARTING_FOOD = float("-inf")
STARTING_GOAL = 1
LUXURY_GOAL = 3
STABLE_SCORE = 8
SAFE_DISTANCE = 4



#################
# Team creation #
#################
def createTeam(firstIndex, secondIndex, isRed, first = 'AccidentalIglooAgent', second = 'AccidentalIglooAgent'):
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



#########
# Agent #
#########

class AccidentalIglooAgent(CaptureAgent):
	"""
	A reflex agent that chooses score-maximizing actions
	"""
	def registerInitialState(self, gameState):
		self.start = gameState.getAgentPosition(self.index)
		CaptureAgent.registerInitialState(self, gameState)

		# Will create a list of all spaces with no walls based on gameState
		noWalls = []
		walls = gameState.getWalls()
		for x in range(walls.width):
			for y in range(walls.height):
				if walls[x][y] is False:
					noWalls.append((x,y))
		self.notWalls = noWalls
		self.walls = walls.asList()

		# Updates food and sets self.myFood
		self.food = STARTING_FOOD
		self.myFood = None
		self.updateMyFood(gameState)

		# Useful agent states	
		self.onStart = True
		self.onDefence = False
		self.onEscape = False
		self.isPowered = 0

		# Useful agent data
		self.target = None
		self.goal = STARTING_GOAL

	def chooseAction(self, gameState):
		"""
		Picks among the actions with the highest Q(s,a).
		"""
		actions = gameState.getLegalActions(self.index)
		foodLeft = len(self.getFood(gameState).asList())
		isPacman = gameState.getAgentState(self.index).isPacman

		# When food is deposited as well as 1st started
		if not isPacman and self.food < float("inf"):
			self.food = STARTING_FOOD

		self.setTarget(gameState)
		self.checkMode(gameState)

		# Increase goal when score is stable
		score = self.getScore(gameState)
		if score > STABLE_SCORE:
			self.goal = LUXURY_GOAL

		# You can profile your evaluation time by uncommenting these lines
		# start = time.time()
		values = [self.evaluate(gameState, a) for a in actions]
		# print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

		maxValue = max(values)
		bestActions = [a for a, v in zip(actions, values) if v == maxValue]
		successor = self.getSuccessor(gameState, random.choice(bestActions))
		foodList = self.getFood(successor).asList() 

		# increment when food is eaten
		if(len(foodList) < foodLeft):
			if self.food == STARTING_FOOD:
				self.food = 0
			self.food += 1

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



	##############
	# Evaluation #
	##############

	def evaluate(self, gameState, action):
		"""
		Computes a linear combination of features and feature weights
		"""
		features = self.getFeatures(gameState, action)
		weights = self.getWeights(gameState, action)

		return features * weights

	def getFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		# if we are on defence and target is set
		if self.onDefence and self.target:
			features = self.getDefenceFeatures(gameState, action)
			return features

		# only check when agent is pacman or about to become pacman
		successor = self.getSuccessor(gameState, action)
		isPacman = gameState.getAgentState(self.index).isPacman
		isGoingToBePacman = successor.getAgentState(self.index).isPacman
		if self.onEscape:
			if isPacman or isGoingToBePacman:
				features = self.getEscapeFeatures(gameState, action)
				return features

		# none of the special cases happen, just go generally
		features = self.getGeneralFeatures(gameState, action)
		return features

	def getWeights(self, gameState, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'successorScore': 1.0, 'food': 50, 'stop': -100, 'eatTheFood': 100, 'deadEnd': -200,
				'distanceToHome': -10, 'distanceToFood': -10, 'distanceToTarget': -10, 
				'distanceToPartner': 8, 'distanceToGhost': 50}



	##############
	#  Features  #
	##############

	def getGeneralFeatures(self, gameState, action):
		"""
		Returns a counter of features for the state
		"""
		features = util.Counter()
		successor = self.getSuccessor(gameState, action)
		foodList = self.getFood(successor).asList() 
		currentFoodList = self.getFood(gameState).asList() 
		myPos = successor.getAgentState(self.index).getPosition()
		distanceToHome = self.getMazeDistance(self.start, myPos)

		features['successorScore'] = self.getScore(successor)
		features['distanceToPartner'] = self.distanceBetweenPartner(successor)

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

		# Compute distance to the nearest food
		if len(foodList) > 0: # This should always be True,  but better safe than sorry
			myPos = successor.getAgentState(self.index).getPosition()
			myTeam = self.getTeam(gameState)
			# agents going for different food at the start
			if self.onStart and self.index == min(myTeam):
				minDistance = self.second_smallest([self.getMazeDistance(myPos, food) for food in foodList])
			else:
				minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
			# deposit food home when collected enough
			if self.food == STARTING_FOOD or self.food < self.goal:
				features['distanceToFood'] = minDistance
			else:
				features['distanceToHome'] = distanceToHome

		return features

	def getDefenceFeatures(self, gameState, action):
		# if there is enemy in our side
		features = util.Counter()	
		successor = self.getSuccessor(gameState, action)

		myState = successor.getAgentState(self.index)
		myPos = myState.getPosition() 

		# prevent it to stop
		if action == Directions.STOP: 
			features['stop'] = 1

		# go to the target
		if self.target:
			features["distanceToTarget"] = self.getMazeDistance(self.target, myPos)

		return features

	def getEscapeFeatures(self, gameState, action):
		features = util.Counter()
		successor = self.getSuccessor(gameState, action)

		myPos = successor.getAgentState(self.index).getPosition()
		distanceToHome = self.getMazeDistance(self.start, myPos)
		distanceToGhost = self.closestEnemy(successor, "distance")	

		# prevent it to stop
		if action == Directions.STOP: 
			features['stop'] = 1

		# head home but also stay away from ghost
		features['distanceToHome'] = distanceToHome
		if distanceToGhost > SAFE_DISTANCE:
			# when this step will result in us being eaten and return home
			features['distanceToGhost'] = float('-inf')
		else:
			features['distanceToGhost'] = distanceToGhost

		# don't run into dead end for next 3 steps
		for index in range(1, 3):
			wallNo = self.deadEndCheck(gameState, action)
			if wallNo >= 3:
				features['deadEnd'] = 3
				break

		return features



	###################
	# Enemy functions #
	###################

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

	def enemyEaten(self, gameState):
		eaten = False
		currEnemy = self.enemiesInRange(gameState)
		previousState = self.getPreviousObservation()
		pastEnemies = None
		if previousState:
			pastEnemies = self.enemiesInRange(previousState)
		if pastEnemies:
		#if enemies could be seen in the previous state
			pastEnemyDistance = self.closestEnemy(previousState, "distance")
			pastEnemyIndex = self.closestEnemy(previousState, "index")
			if pastEnemyDistance <= 1 and pastEnemyIndex not in currEnemy:
			#if enemy was next to me and is not in current range, he's eaten
				eaten = True
		self.updateMyFood(gameState)
		return eaten

	def enemiesInRange(self, gameState):
		myPos = gameState.getAgentState(self.index).getPosition()
		enemies = []
		for enemy in self.getOpponents(gameState):
			coord = gameState.getAgentState(enemy).getPosition()
			if coord != None and self.getMazeDistance(myPos, coord) < SAFE_DISTANCE:
				enemies.append(coord)
		return enemies

	def closestEnemy(self, gameState, option):
		#Option = ["distance", "index", "coord"]
		enemies = self.enemyCoord(gameState)
		myPos = gameState.getAgentState(self.index).getPosition()
		closestEnemyPos = None
		closestEnemyIndex = None
		closest = None
		if len(enemies) != 0:
			for enemyPos, enemy in enemies:
				distance = self.getMazeDistance(myPos, enemyPos)
				if distance < closest or closest == None:
					closest = distance
					closestEnemyPos = enemyPos
					closestEnemyIndex = enemy
		if option == "distance":
			return closest
		elif option == "index":
			return closestEnemyIndex
		elif option == "coord":
			return closestEnemyPos
		else:
			#Should only alert programmer of syntax error
			raise ValueError('Option value in closestEnemy is wrong : myTeam.py')

	def enemyCoord(self, gameState):
		enemies = []
		for enemy in self.getOpponents(gameState):
			coord = gameState.getAgentState(enemy).getPosition()
			if coord != None:
				enemies.append((coord,enemy))
		return enemies



	#######################
	# Our Agent Functions #
	#######################

	def checkMode(self, gameState):
		isPacman = gameState.getAgentState(self.index).isPacman
		# reset target and mode when enemy is eaten
		if self.enemyEaten(gameState):
			self.onDefence = False
			self.target = None

		# check if there is any enemy is our base
		enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
		invaders = [a for a in enemies if a.isPacman]
		if not invaders:
			self.onDefence = False
			self.target = None
		else:
			self.onDefence = True

		# make it false once it passes the border
		if self.onStart and isPacman:
			self.onStart = False

		# to prevent both agents going for the same food
		teammates = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
		ghosts = [a for a in teammates if not a.isPacman]
		if len(ghosts) >= 2:
			self.onStart = True

		# check if there is ghost around
		distanceToGhost = self.closestEnemy(gameState, "distance")	
		if distanceToGhost and distanceToGhost <= SAFE_DISTANCE:
			self.onEscape = True
		else:
			self.onEscape = False

	def setTarget(self, gameState):
		# if there is missing food and it is closer to this agent
		missingFood = self.enemyOnOurSide(gameState)
		if missingFood and self.closestAgent(gameState, missingFood):
			# set missing food position as the target
			self.target = missingFood

		# if we see an enemy on our side and this agent is closer
		enemyIndex = self.closestEnemy(gameState, 'index')
		enemyPos = self.closestEnemy(gameState, 'coord')
		if self.onDefence and self.closestAgent(gameState, enemyPos) and gameState.getAgentState(enemyIndex).isPacman:
			# set enemy's coordinate as target
			self.target = enemyPos

		# if already reach that position, reset
		myPos = gameState.getAgentState(self.index).getPosition()
		if self.target == myPos:
			self.target = None

	def closestAgent(self, gameState, targetPos):
		# check if return value == self.index
		if targetPos is None:
			return False
		else:
			myTeam = self.getTeam(gameState)
			teamDist = []
			for teamMate in myTeam:
				distToEnemy = self.getMazeDistance(gameState.getAgentState(teamMate).getPosition(),targetPos)
				teamDist.append((teamMate, distToEnemy))
			closestAgent = min(teamDist, key= lambda x:x[1])[0]
			return closestAgent == self.index

	def distanceBetweenPartner(self, gameState):
		# calculate distance between partner
		team = self.getTeam(gameState)
		for teammate in team:
			if not teammate == self.index:
				myPos = gameState.getAgentState(self.index).getPosition()
				matePos = gameState.getAgentState(teammate).getPosition()
				distance = self.getMazeDistance(myPos, matePos)
				return distance

	def updateMyFood(self, gameState):
		if self.red:
			self.myFood = gameState.getRedFood().asList()
		else:
			self.myFood = gameState.getBlueFood().asList()

	def capsuleDist(self, gameState):
		capsules = CaptureAgent.getCapsules(self, gameState)
		capsuleCoord, capsuleDist = self.getClosestCoord(capsules, gameState)
		return capsuleCoord, capsuleDist
	
	def deadEndCheck(self, gameState, action):
		successor = self.getSuccessor(gameState, action)
		myPos = successor.getAgentState(self.index).getPosition()
		x, y = myPos
		check = 0
		
		checkPositions = [(x+1, y),(x-1, y),(x, y+1),(x, y-1)]
		
		for position in checkPositions:
			if position in self.walls:
				check += 1
		return check



	#####################
	# General functions #
	#####################

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

	def getClosestCoord(self, coordList, gameState):
		currentPosition = gameState.getAgentState(self.index).getPosition()
		minCoord = None
		minDist = float('inf')
		for coord in coordList:
			if self.getMazeDistance(currentPosition, coord) < minDist:
				minCoord = coord
				minDist = self.getMazeDistance(currentPosition, coord)
		return minCoord, minDist

	# from stack overflow 
	# https://stackoverflow.com/questions/26779618/python-find-second-smallest-number
	def second_smallest(self, numbers):
		m1, m2 = float('inf'), float('inf')
		for x in numbers:
			if x <= m1:
				m1, m2 = x, m1
			elif x < m2:
				m2 = x
		return m2