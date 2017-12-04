import numpy as np
from portfolio import Portfolio
from util import *
from extractors import *
from reward import *
import json
import sys
import pickle

np.random.seed(1337)

class ApproximateQAgent():
    def __init__(self, 
                 funds=10000, # start with 10000 dollars
                 featExtractor=Try2(), 
                 alpha=0.5, 
                 epsilon=0.05, # initial episolon value
                 gamma=0.95, # discount rate
                 trainingDataBound=0.8,
                 stepsPerEpisode=288, # 3-day period
                 rewardFunction=reward,
                 weights=None):
        self.featExtractor = featExtractor
        self.portfolio = Portfolio(funds)
        if weights == None:
            numFeatures = len(self.featExtractor.getFeatures(self.portfolio.getCurrentState(), "hold"))
            self.weights = np.zeros(numFeatures)
        else:
            self.weights = weights

        self.rewardFunction = rewardFunction
        self.trainingDataBound = trainingDataBound
        self.stepsPerEpisode = stepsPerEpisode
        self.discount = gamma
        self.epsilon = epsilon
        self.alpha = alpha
        self.episodes = []

    def getWeights(self):
        return self.weights

    def getQValue(self, state, action):
        """
          Should return Q(state,action) = w * featureVector
          where * is the dotProduct operator
        """
        features = self.featExtractor.getFeatures(state, action)
        return features.dot(self.weights)

    def update(self, state, action, nextState, reward):
        """
           Update the weights based on the transition
        """
        difference = reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)
        self.weights += self.alpha * difference * features
        self.weights /= np.mean(self.weights)

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, this returns a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if not actions:
            return 0.0
        return max([self.getQValue(state, action) for action in actions])

    def getLegalActions(self, state):
        return self.portfolio.getLegalActions(state)

    def getAction(self, state):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        legalActions = self.getLegalActions(state)
        if not legalActions:
            return None
        if flipCoin(self.epsilon):
            return np.random.choice(legalActions)
        return self.computeActionFromQValues(state)

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        actions = self.getLegalActions(state)
        if not actions:
            return None
        qValueActionPairs = [(action, self.getQValue(state, action)) for action in actions]
        maxActions = [qValueActionPairs[0][0]]
        maxQValue = qValueActionPairs[0][1]
        for action, qValue in qValueActionPairs:
            if qValue == maxQValue:
                maxActions.append(action)
            elif qValue > maxQValue:
                maxActions = [action]
                maxQValue = qValue
        return np.random.choice(maxActions)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

    def runEpisode(self):
        def getDelta(history):
            state = self.portfolio.getCurrentState()
            portfolioDelta = (history[-1][2] - history[0][2]) / history[0][2]
            bitcoinDelta = (state["market"].getCurrentMarketInfo()["weighted_price"] - state["initial_bitcoin_price"]) / state["initial_bitcoin_price"]
            return bitcoinDelta, portfolioDelta, portfolioDelta - bitcoinDelta

        # randomly select a starting point in the training data
        self.portfolio.reset(0, self.trainingDataBound)

        for i in range(self.stepsPerEpisode):
            state = self.portfolio.getCurrentState()
            action = self.getAction(state)
            # take the action and increment the market one timestamp
            self.portfolio.takeAction(action)
            # observe the next state
            nextState = self.portfolio.getCurrentState()
            # get the reward based upon
            reward = self.rewardFunction(state, nextState)
            self.update(state, action, nextState, reward)
        self.episodes.append(self.portfolio.getHistory())
        with open('history.log', 'a+') as f:
            delta = getDelta(self.episodes[-1])
            f.write("{},{},{},{}\n".format(delta[0], delta[1], delta[2], self.portfolio.getCurrentState()["total_in_usd"]))

        with open('weights.txt', 'w') as f:
            pickle.dump(self.weights, f)
        return getDelta(self.episodes[-1])[2], self.portfolio.getCurrentState()["total_in_usd"]

    def runTest(self):
        # move the market to the test data
        self.portfolio.reset(self.trainingDataBound, self.trainingDataBound)
