from portfolio import Portfolio
from util import *
from extractors import *
from reward import *

import sys

class ApproximateQAgent():
    def __init__(self, 
                 funds=10000, 
                 featExtractor=BasicFeatureExtractor(), 
                 alpha=0.10, 
                 epsilon=0.05, 
                 gamma=0.2, 
                 trainingDataBound=0.8,
                 stepsPerEpisode=1440,
                 rewardFunction=reward):
        self.featExtractor = featExtractor
        self.weights = Counter()
        self.portfolio = Portfolio(funds)

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
        value = 0
        for key in features:
            value += features[key] * self.weights[key]
        return value

    def update(self, state, action, nextState, reward):
        """
           Should update your weights based on transition
        """
        "*** YOUR CODE HERE ***"
        difference = reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)
        for key in features:
            self.weights[key] += self.alpha * difference * features[key] 

    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        "*** YOUR CODE HERE ***"
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

          HINT: You might want to use util.flipCoin(prob)
          HINT: To pick randomly from a list, use random.choice(list)
        """
        "*** YOUR CODE HERE ***"
        legalActions = self.getLegalActions(state)
        if not legalActions:
            return None
        if flipCoin(self.epsilon):
            return random.choice(legalActions)
        return self.computeActionFromQValues(state)

    def computeActionFromQValues(self, state):
        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        "*** YOUR CODE HERE ***"
        actions = self.getLegalActions(state)
        if not actions:
            return None
        qValueActionPairs = [(action, self.getQValue(state, action)) for action in actions]
        print qValueActionPairs
        maxActions = []
        maxQValue = -sys.maxint
        for action, qValue in qValueActionPairs:
            if qValue == maxQValue:
                maxActions.append(action)
            elif qValue > maxQValue:
                maxActions = [action]
                maxQValue = qValue
        print maxActions
        return random.choice(maxActions)

    def getValue(self, state):
        return self.computeValueFromQValues(state)

    def runEpisode(self):
        def getDelta(history):
            state = self.portfolio.getCurrentState()
            portfolioDelta = (history[-1][2] - history[0][2]) / history[0][2]
            bitcoinDelta = (state["market"].getCurrentMarketInfo()["weighted_price"] - state["initial_bitcoin_price"]) / state["initial_bitcoin_price"]
            return portfolioDelta - bitcoinDelta


        self.portfolio.reset(self.trainingDataBound)
        for i in range(self.stepsPerEpisode):
            state = self.portfolio.getCurrentState()
            action = self.getAction(state)
            self.portfolio.takeAction(action)
            nextState = self.portfolio.getCurrentState()
            reward = self.rewardFunction(state, action)
            self.update(state, action, nextState, reward)
        self.episodes.append(self.portfolio.getHistory())
        return getDelta(self.episodes[-1])





