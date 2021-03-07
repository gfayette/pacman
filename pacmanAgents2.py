# pacmanAgents.py
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


from pacman import Directions
from game import Agent
import random
import game
import util

class LeftTurnAgent(game.Agent):
    "An agent that turns left at every opportunity"

    def getAction(self, state):
        legal = state.getLegalPacmanActions()
        current = state.getPacmanState().configuration.direction
        if current == Directions.STOP: current = Directions.NORTH
        left = Directions.LEFT[current]
        if left in legal: return left
        if current in legal: return current
        if Directions.RIGHT[current] in legal: return Directions.RIGHT[current]
        if Directions.LEFT[left] in legal: return Directions.LEFT[left]
        return Directions.STOP

class JustEnoughAgent(Agent):
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
            foodList = self.getFood(gameState).asList()
            thisState = state.getAgentState(self.index)
            thisPosition = ThisState.getPosition()
            nearestFood = self.nearestPellet(foodList, thisPosition)

            weight1 = vectorToDirection((nearestFood[0] - thisPosition[0], 0))
            weight2 = vectorToDirection((0, nearestFood[1] - thisPosition[1]))


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
        mindDist = 9999
        index = -1

        for food in foodList:
            if (abs(food[0] - position[0]) + abs(food[1] - position[1])) < minDist:
                mindDist = abs(food[0] - position[0]) + abs(food[1] - position[1])
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

class GreedyAgent(Agent):
    def __init__(self, evalFn="scoreEvaluation"):
        self.evaluationFunction = util.lookup(evalFn, globals())
        assert self.evaluationFunction != None

    def getAction(self, state):
        # Generate candidate actions
        legal = state.getLegalPacmanActions()
        if Directions.STOP in legal: legal.remove(Directions.STOP)

        successors = [(state.generateSuccessor(0, action), action) for action in legal]
        scored = [(self.evaluationFunction(state), action) for state, action in successors]
        bestScore = max(scored)[0]
        bestActions = [pair[1] for pair in scored if pair[0] == bestScore]
        return random.choice(bestActions)

def scoreEvaluation(state):
    return state.getScore()
