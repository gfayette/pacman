# finalTeam.py
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


# finalTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
from __future__ import print_function
from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from game import Directions
import game
from util import nearestPoint


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first='OffensiveReflexAgent', second='DefensiveReflexAgent'):
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
        CaptureAgent.registerInitialState(self, gameState)

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """
        actions = gameState.getLegalActions(self.index)

        values = [self.evaluate(gameState, a) for a in actions]
        if self.index == 1:
            print(values, file=sys.stderr)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())

        if foodLeft <= 2 or gameState.getAgentState(self.index).numCarrying > 5:
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


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """

    def __init__(self, index, timeForComputing=.1):
        super().__init__(index, timeForComputing)
        self.edibleGhosts = False
        self.nearGhostsTimer = 0

    def isDeadEnd(self, successor, depth, previous):
        """
        Returns true if the given successor state leads to a dead end
        in 'depth' moves or less
        """
        if depth == 0:
            return False

        actions = successor.getLegalActions(self.index)
        state = successor.getAgentState(self.index)
        position = state.getPosition()

        if len(actions) <= 2:
            return True
        else:
            depth -= 1
            nextSuccessorDeadEnd = True
            for a in actions:
                if a != 'Stop':
                    nextSuccessor = self.getSuccessor(successor, a)
                    if not nextSuccessor.getAgentState(self.index).getPosition() == previous:
                        if not self.isDeadEnd(nextSuccessor, depth, position):
                            nextSuccessorDeadEnd = False
            return nextSuccessorDeadEnd

    def checkEdibleGhosts(self, gameState, scareTime):
        """
        Check to see if the opponent's ghosts are edible and
        their scareTimer is less than 'scareTime'
        """
        opp_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        for p in opp_state:
            if p.scaredTimer > scareTime:
                self.edibleGhosts = True
                return
        self.edibleGhosts = False

    def checkNearGhosts(self, gameState, dist):
        """
        Check if the agent is within 'dist' of opponent's ghosts
        and set a timer if so
        """
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        opp_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        chasers = [p for p in opp_state if p.getPosition() != None and not p.isPacman]

        close_dist = 9999.0
        if len(chasers) > 0:
            close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])

        if close_dist < dist:
            self.nearGhostsTimer = 5
        else:
            if self.nearGhostsTimer > 0:
                self.nearGhostsTimer -= 1

        if myPos == self.start:
            self.nearGhostsTimer = 0

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """

        self.checkEdibleGhosts(gameState, 4)
        self.checkNearGhosts(gameState, 8)

        actions = gameState.getLegalActions(self.index)

        if len(actions) > 1 and 'Stop' in actions:
            actions.remove('Stop')

        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        # State and position
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Assign successorScore
        foodList = self.getFood(successor).asList()
        capsules = self.getCapsules(successor)
        features['successorScore'] = -1 * (len(foodList) + len(capsules))

        # Compute distance to the nearest food or capsule and assign distanceToFood
        minFoodDist = 9999.0
        if len(foodList) > 0:
            minFoodDist = min([self.getMazeDistance(myPos, food) for food in foodList])
        minCapsuleDist = 9999.0
        if len(capsules) > 0:
            minCapsuleDist = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
        features['distanceToFood'] = min([minFoodDist, minCapsuleDist])

        # Assign goHome in proportion to how many pieces of food the agent is carrying
        numCarrying = gameState.getAgentState(self.index).numCarrying
        distance = self.getMazeDistance(myPos, self.start)
        features['goHome'] = distance * numCarrying

        # If the agent is near ghosts and they are not edible
        if self.nearGhostsTimer > 0 and not self.edibleGhosts:
            # Favor paths that take the agent home
            distance = self.getMazeDistance(myPos, self.start)
            features['goHome'] = distance
            # Assign fleeEnemy
            if action == 'Stop':
                features['fleeEnemy'] = 100.0  # dont stop
            elif self.isDeadEnd(successor, 6, gameState.getAgentState(self.index).getPosition()):
                features['fleeEnemy'] = 100.0  # don't go down a dead end
                print(str(myPos), " is a dead end")
            else:  # Use the fleeEnemy feature to discourage the agent from moving towards the closest ghost
                close_dist = 9999.0
                opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
                if len(chasers) > 0:
                    close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])
                features['fleeEnemy'] = -close_dist
        # If the ghosts are edible, use the fleeEnemy feature to encourage the agent to chase the closest ghost
        elif self.edibleGhosts:
            close_dist = 9999.0
            opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
            chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
            if len(chasers) > 0:
                close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])
            for c in chasers:
                # If the ghost is at its starting location, then it was just eaten by Pacman
                if c.getPosition() == (1, 1) or c.getPosition() == (30, 14):
                    close_dist = 0.0  # Eat the ghost
            features['fleeEnemy'] = close_dist

        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -2.0, 'fleeEnemy': -20.0, 'goHome': -1.5}


class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """
    def __init__(self, index, timeForComputing=.1):
        super().__init__(index, timeForComputing)
        self.selfEdibleGhost = False

    def checkEdibleGhosts(self, gameState, scareTime):
        """
        Check to see if your ghosts are edible and
        their scareTimer is less than 'scareTime'
        """
        self_state = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
        for p in self_state:
            if p.scaredTimer > scareTime:
                #print("Edible")
                self.selfEdibleGhost = True
                return
        self.edibleGhosts = False

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """

        self.checkEdibleGhosts(gameState, 3)

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        if self.index == 1:
            print(values, file=sys.stderr)
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes distance to invaders we can see
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            #run away from pacman if edible
            if self.selfEdibleGhost:
                features['invaderDistance'] = min(dists)
            #chase pacman if not edible
            else:
                features['invaderDistance'] = -min(dists)
        #check to not move to the wrong area
        elif myState.isPacman:
            features['wrongZone'] = 1
        else:
            features['wrongZone'] = 0

        #follow ghost if no pacmen to chase
        pacmen = [a for a in enemies if a.getPosition() != None and not a.isPacman]
        if len(pacmen) > 0:
            pacDists = [self.getMazeDistance(myPos, a.getPosition()) for a in pacmen]
            features['pacmanDist'] = -min(pacDists)

        #don't stop moving
        if action == 'Stop':
            features['moveIt'] = 1

        # Compute distance to the nearest food
        foodList = self.getFood(successor).asList()
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        return features

    def getWeights(self, gameState, action):
        return {'invaderDistance': 1000, 'wrongZone': -500, 'distanceToFood': -20, 'moveIt': -25, 'pacmanDist': 200}