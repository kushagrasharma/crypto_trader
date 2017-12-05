import numpy as np
from portfolio import Portfolio
from util import *
from extractors import *
from reward import *
import json
import sys
import pickle
import os

# seed the random number generator so that we can duplicate the results
np.random.seed(1337)

class ApproximateQAgent():
    def __init__(self, weightPath=None,
                 funds=10000, # start with 10000 dollars
                 featExtractor=Try2(), 
                 alpha=0.5, 
                 epsilon=0.05, # initial episolon value
                 gamma=0.90, # discount rate
                 trainingDataBound=0.90,
                 stepsPerEpisode=288, # 3-day period
                 rewardFunction=reward):
        self.featExtractor = featExtractor()
        self.portfolio = Portfolio(funds)
        if not weightPath:
            self.weightPath = "results/" + str(featExtractor)[11:]
            if os.path.isfile(self.weightPath):
                with open(self.weightPath) as f:
                    self.weights = pickle.load(f)
            else:
                numFeatures = len(self.featExtractor.getFeatures(self.portfolio.getCurrentState(), "hold"))
                self.weights = np.random.randn(numFeatures)
        else:
            self.weightPath = weightPath
            with open(weightPath) as f:
                self.weights = pickle.load(f)
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
        if np.mean(self.weights) > 0:
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
        if self.epsilon != 0 and flipCoin(self.epsilon):
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
            pChange = history[-1][2] - history[0][2]
            portfolioDelta = (pChange) / history[0][2]
            bChange = state["market"].getCurrentMarketInfo()["weighted_price"]-state["initial_bitcoin_price"]
            bitcoinDelta = (bChange) / state["initial_bitcoin_price"]
            return bitcoinDelta, portfolioDelta, portfolioDelta - bitcoinDelta, pChange, bChange, state["initial_bitcoin_price"],

        # randomly select a starting point in the training data
        self.portfolio.reset(0.5, self.trainingDataBound)

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
        # decrement epsilon as we progress in training
        # self.epsilon *= 0.9
        #print self.weights

        # log data
        with open('results/train.log', 'a+') as f:
            delta = getDelta(self.episodes[-1])
            f.write("{},{},{},{},{},{},{}\n".format(delta[0], delta[1], delta[2], delta[3], delta[4], delta[5], self.portfolio.getCurrentState()["total_in_usd"]))

        with open(self.weightPath, 'w') as f:
            pickle.dump(self.weights, f)
        self.weights.tofile('results/weight_history.csv',sep=',',format='%10.5f')
        return getDelta(self.episodes[-1])[2], self.portfolio.getCurrentState()["total_in_usd"]

    def runTest(self):
        def getDelta(history):
            state = self.portfolio.getCurrentState()
            pChange = history[-1][2] - history[0][2]
            portfolioDelta = (pChange) / history[0][2]
            bChange = state["market"].getCurrentMarketInfo()["weighted_price"]-state["initial_bitcoin_price"]
            bitcoinDelta = (bChange) / state["initial_bitcoin_price"]
            return bitcoinDelta, portfolioDelta, portfolioDelta - bitcoinDelta, pChange, bChange, state["initial_bitcoin_price"],


        self.portfolio.reset(self.trainingDataBound, self.trainingDataBound)
        self.epsilon = 0.001


        market = self.portfolio.getCurrentState()["market"]
        startTimestamp = market.getCurTimestamp()

        length = market.getNumTimestamps() - market.getCurTimestamp()
        for i in range(int(length) - 1):
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

        endTimestamp = market.getCurTimestamp()


        # log data
        with open('results/test.log', 'w') as f:
            delta = getDelta(self.episodes[-1])
            f.write("{},{},{},{},{},{},{},{},{}\n".format(delta[0], delta[1], delta[2], delta[3], delta[4], delta[5], self.portfolio.getCurrentState()["total_in_usd"], startTimestamp, endTimestamp))
        with open('test_history.log', 'w') as f:
            pickle.dump(self.portfolio.getHistory(), f)

        with open(self.weightPath, 'w') as f:
            pickle.dump(self.weights, f)
        return getDelta(self.episodes[-1])[2], self.portfolio.getCurrentState()["total_in_usd"]

    def trainAgent(self, n_iter = 100):
        training = []
        for i in range(n_iter):
            g = [i] + list(self.runEpisode())
            print(g)
            training.append(copy.deepcopy(g))
        return pd.DataFrame(training, columns=['iteration', 'returns', 'asset_value']).set_index('iteration', inplace=False)

    def testAndTrain(self, n_iter=100):
        print "TRAINING"
        training = agent.trainAgent(n_iter=n_iter)
        training.to_csv("results/" + "train_" + self.featExtractor.__class__.__name__ + '.csv')
        print "TESTING"
        return agent.runTest()


