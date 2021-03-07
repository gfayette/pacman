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

    def __init__(self, index, timeForComputing=.1):
        super().__init__(index, timeForComputing)
        self.nearGhosts = False
        self.edibleGhosts = False

    def registerInitialState(self, gameState):
        self.start = gameState.getAgentPosition(self.index)
        CaptureAgent.registerInitialState(self, gameState)

    def checkEdibleGhosts(self, gameState, scareTime):
        """
        Check to see if the opponent's ghosts are edible and
        their scareTimer is less than 'scareTime'
        """
        opp_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        for p in opp_state:
            if p.scaredTimer > scareTime:
                print("Edible")
                self.edibleGhosts = True
                return
        self.edibleGhosts = False

    def checkNearGhosts(self, gameState, dist):
        """
        Check if the agent is within 'dist' of opponent's ghosts
        """
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        opp_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        chasers = [p for p in opp_state if p.getPosition() != None and not p.isPacman]

        close_dist = 9999.0
        if len(chasers) > 0:
            close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])

        if close_dist < dist:
            self.nearGhosts = True
            print("near ghosts")
        else:
            self.nearGhosts = False

    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s,a).
        """

        self.checkEdibleGhosts(gameState, 4)
        self.checkNearGhosts(gameState, 6)

        actions = gameState.getLegalActions(self.index)
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        foodLeft = len(self.getFood(gameState).asList())
        if foodLeft == 0 or gameState.getAgentState(self.index).numCarrying > 2:
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

        # if self.index == 1:
        # print(str(features) + str(weights), file=sys.stderr)
        # print(gameState.getAgentState(self.index)) # Print out a text representation of the world.

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


    def getFeatures(self, gameState, action):
        # print(self.index)
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        foodList = self.getFood(successor).asList()
        features['successorScore'] = -len(foodList)  # self.getScore(successor)

        # Compute distance to the nearest food
        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # Compute distance to the nearest food
        capsules = self.getCapsules(successor)
        if len(capsules) > 0:
            distance = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
            features['distanceToCapsule'] = distance

        if self.nearGhosts and not self.edibleGhosts:
            if action == 'Stop':
                features['fleeEnemy'] = 20.0  # dont stop
            elif self.isDeadEnd(successor, 6, gameState.getAgentState(self.index).getPosition()):
                features['fleeEnemy'] = 20.0  # don't go down a dead end
                print(str(myPos), " is a dead end")
            else:
                close_dist = 9999.0
                opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
                if len(chasers) > 0:
                    close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])
                features['fleeEnemy'] = 1.0 / close_dist

        elif self.edibleGhosts:
            close_dist = 9999.0
            if gameState.getAgentState(self.index).isPacman:
                opp_fut_state = [successor.getAgentState(i) for i in self.getOpponents(successor)]
                chasers = [p for p in opp_fut_state if p.getPosition() != None and not p.isPacman]
                if len(chasers) > 0:
                    close_dist = min([float(self.getMazeDistance(myPos, c.getPosition())) for c in chasers])
                for c in chasers:
                    if c.getPosition() == (1,1):
                        close_dist = 0.1
            features['fleeEnemy'] = -10.0 / close_dist



        return features

    def getWeights(self, gameState, action):
        return {'successorScore': 100, 'distanceToFood': -1, 'fleeEnemy': -100.0, 'distanceToCapsule': -2}


class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free. Again,
    this is to give you an idea of what a defensive agent
    could be like.  It is not the best or only way to make
    such an agent.
    """

    def getFeatures(self, gameState, action):
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

        return features

    def getWeights(self, gameState, action):
        return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}
