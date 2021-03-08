# justEnoughTeam.py
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


# justEnoughTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util, sys
from util import nearestPoint
from pacman import Directions
from game import Agent
from game import Actions
from game import Configuration
import random
import game
import util


#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'JustEnoughAgent', second = 'DefensiveReflexAgent'):
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

class JustEnoughAgent(CaptureAgent):
    "pacman that gets just enough pellets to be ahead, then returns home"
    def getAction(self, state):

        #If the score is in the green, then the agent heads home and doesn't risk getting caught, otherwise it collects pellets until it is ahead
        if state.getScore() > 0:
            #retreat
            #remove stop
            #weight current direction high
            #weight path back higher

            #holds a weighted distribution of options
            choiceDist = Counter(actions = state.getLegalPacmanActions())

            going = state.getDirection()

            #these if statements weight higher the direction the agent is travelling and the direction to the nearest pellet
            if choiceDist[going] > 0:
                choiceDist[going] += 4

            if choiceDist[Directions.WEST] > 0:
                choiceDist[Directions.WEST] += 4


            #if the player is near a ghost, this removes options that would endanger the agent
            if self.checkNearGhosts(state, 2)[0]:
                #these next 2 lines of code are modified from George Fayette's Checknearghosts method
                opp_state = [state.getAgentState(i) for i in self.getOpponents(state)]
                chasers = [p for p in opp_state if p.getPosition() != None and not p.isPacman]

                #store location of nearest ghost
                ghostLocation = chasers[self.checkNearGhosts(state, 2)[1]]


                remove1 = vectorToDirection((ghostLocation[0] - thisPosition[0], 0))
                remove2 = vectorToDirection((0, ghostLocation[1] - thisPosition[1]))

                del choiceDist[remove1]
                del choiceDist[remove2]

            if len(choiceDist) > 0:
                #I found this choosefromdistribution line in ghost agents, it looks like it picks an option using the counter as a weighted distribution, so hopefully it works
                return util.chooseFromDistribution( choiceDist )
            else:
                return Directions.Stop




        else:
            foodList = self.getFood(state).asList()
            thisState = state.getAgentState(self.index)
            thisPosition = thisState.getPosition()
            nearestFood = self.nearestPellet(foodList, thisPosition)

            weight1 = Actions.vectorToDirection((nearestFood[0] - thisPosition[0], 0))
            weight2 = Actions.vectorToDirection((0, nearestFood[1] - thisPosition[1]))


            #holds a weighted distribution of options
            choiceDist = Counter(actions = state.getLegalPacmanActions())

            going = state.getDirection()

            #these if statements weight higher the direction the agent is travelling and the direction to the nearest pellet
            if choiceDist[going] > 0:
                choiceDist[going] += 4

            if choiceDist[weight1] > 0:
                choiceDist[weight1] += 2

            if choiceDist[weight2] > 0:
                choiceDist[weight2] += 2

            #can't stop, won't stop
            del choiceDist[Directions.STOP]


            #if the player is near a ghost, this removes options that would endanger the agent
            if self.checkNearGhosts(state, 2)[0]:
                #these next 2 lines of code are modified from George Fayette's Checknearghosts method
                opp_state = [state.getAgentState(i) for i in self.getOpponents(state)]
                chasers = [p for p in opp_state if p.getPosition() != None and not p.isPacman]

                #store location of nearest ghost
                ghostLocation = chasers[self.checkNearGhosts(state, 2)[1]]


                remove1 = vectorToDirection((ghostLocation[0] - thisPosition[0], 0))
                remove2 = vectorToDirection((0, ghostLocation[1] - thisPosition[1]))

                del choiceDist[remove1]
                del choiceDist[remove2]


            if len(choiceDist) > 0:
                #I found this choosefromdistribution line in ghost agents, it looks like it picks an option using the counter as a weighted distribution, so hopefully it works
                return util.chooseFromDistribution( choiceDist )
            else:
                return Directions.Stop


    def nearestPellet(self, foodList, position):
        minDist = 9999
        index = -1

        for food in foodList:
            if (abs(food[0] - position[0]) + abs(food[1] - position[1])) < minDist:
                minDist = abs(food[0] - position[0]) + abs(food[1] - position[1])
                index = foodList.index(food)

        return foodList[index]

    def checkNearGhosts(self, gameState, dist):
        """
        Check if the agent is within 'dist' of opponent's ghosts, method modified from George Fayette's improved OffensiveReflexAgent
        """
        #get 'this' state, and record the position
        myState = gameState.getAgentState(self.index)
        myPos = myState.getPosition()

        #get list of ghosts, then list of their position
        opp_state = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
        chasers = [p for p in opp_state if p.getPosition() != None and not p.isPacman]

        #set a max distance
        close_dist = 9999.0

        ghostIndex = -1

        #if there are any ghosts
        if len(chasers) > 0:
            #closest distance is the minimum of ghost distance and current closest
            for c in chasers:
                if close_dist > self.getMazeDistance(myPos, c.getPosition()):
                    close_dist = self.getMazeDistance(myPos, c.getPosition())
                    ghostIndex = chaser.index(c)

        #returns a tuple with a boolean stating whether the ghost is near, and an index of the nearest ghost
        if close_dist < dist:
            return (True, ghostIndex)
        else:
            return (False, -1)

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

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        if self.index == 1:
            print(values, file=sys.stderr)
            # print(self.getPreviousObservation(), file=sys.stderr)

        # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        # if self.index == 1:
        #   print(bestActions, file=sys.stderr)

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
