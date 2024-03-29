import numpy as np
from portfolio import Portfolio
from util import *
from extractors import *
from reward import *
import json
import sys
import pickle
import os
import copy

# seed the random number generator so that we can duplicate the results
np.random.seed(1337)

class ApproximateQAgent():
    def __init__(self, 
                 weightPath=None, # file path to previous weights (stored in results directory)
                 funds=10000, # start with 10000 dollars
                 featExtractor=Try1(), # define which feature extractor to use
                 alpha=0.5, 
                 epsilon=0.05, # initial epsilon value
                 gamma=0.90, # discount rate
                 trainingDataBound=0.90, # define percentage of data to use for training
                 stepsPerEpisode=288, # 3-day period
                 rewardFunction=reward): # define the reward function for the agent
        self.featExtractor = featExtractor()
        self.portfolio = Portfolio(funds)
        if not weightPath:
            self.weightPath = "results/" + str(featExtractor)[11:]
            if os.path.isfile(self.weightPath):
                # set weights to the values in the given file if available
                with open(self.weightPath) as f:
                    self.weights = pickle.load(f)
            else:
                # randomly initialize weights if they are not given by a file
                numFeatures = len(self.featExtractor.getFeatures(self.portfolio.getCurrentState(), "hold"))
                self.weights = np.random.randn(numFeatures)
        else:
            # randomly initialize weights if they are not given by a file
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
        """
            Returns the current weight values.
        """
        return self.weights

    def getQValue(self, state, action):
        """
            Returns Q(state,action) = w * featureVector, where * is the dotProduct operator.
        """
        # get the features from the feature extractor
        features = self.featExtractor.getFeatures(state, action)
        # return the dot product with the weights
        return features.dot(self.weights)

    def update(self, state, action, nextState, reward):
        """
           Update the weights based on the transition
        """
        # calculate the difference between the updated Q-Value and previous Q-Value for the given state, action pair
        difference = reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)
        features = self.featExtractor.getFeatures(state, action)
        # update the weights
        self.weights += self.alpha * difference * features
        # normalize the weights so that they don't blow up
        if np.mean(self.weights) > 0:
            self.weights /= np.mean(self.weights)

    def computeValueFromQValues(self, state):
        """
            Returns max_action Q(state,action) where the max is over legal actions.  
            Note that if there are no legal actions, which is the case at the terminal 
            state, this returns a value of 0.0.
        """
        actions = self.getLegalActions(state)
        if not actions:
            return 0.0
        return max([self.getQValue(state, action) for action in actions])

    def getLegalActions(self, state):
        """
            Returns a list of legal actions in the given state.  Depending on the 
            amount of Bitcoin and Cash the agent's portfolio has, these can include
            'buy', 'hold', and 'sell'.
        """
        return self.portfolio.getLegalActions(state)

    def getAction(self, state):
        """
            Compute the action to take in the current state.  With probability self.epsilon, 
            we take a random action and take the best policy action otherwise.  Note that if 
            there are no legal actions, which is the case at the terminal state, we return
            None as the action.
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
            this returns None.
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
        """
            Shorter function ame for computeValueFromQValues
        """
        return self.computeValueFromQValues(state)

    def runEpisode(self):
        """
            This runs a single training episode on the training data.  The length of the episode is dependent upon
            the value of self.stepsPerEpisode
        """
        def getDelta(history):
            """
                Returns the percent return information for the current episode
            """
            state = self.portfolio.getCurrentState()
            # get the price change in the portfolio total assets
            pChange = history[-1][2] - history[0][2]
            # calculate the percent difference
            portfolioDelta = (pChange) / history[0][2]
            # get the price change in bitcoin price
            bChange = state["market"].getCurrentMarketInfo()["weighted_price"]-state["initial_bitcoin_price"]
            # calculate the percent difference
            bitcoinDelta = (bChange) / state["initial_bitcoin_price"]
            return bitcoinDelta, portfolioDelta, portfolioDelta - bitcoinDelta, pChange, bChange, state["initial_bitcoin_price"],

        # randomly select a starting point in the training data for the episode to begin at
        self.portfolio.reset(0.0, self.trainingDataBound)

        for i in range(self.stepsPerEpisode):
            state = self.portfolio.getCurrentState()
            action = self.getAction(state)
            # take the action and increment the market one timestamp
            self.portfolio.takeAction(action)
            # observe the next state
            nextState = self.portfolio.getCurrentState()
            # get the reward based upon
            reward = self.rewardFunction(state, nextState)
            # update the weights for the Q-Value function
            self.update(state, action, nextState, reward)
        # store episode information in history
        self.episodes.append(self.portfolio.getHistory())


        # log data

        # append episode statistics to results/train.log
        with open('results/train.log', 'a+') as f:
            delta = getDelta(self.episodes[-1])
            f.write("{},{},{},{},{},{},{}\n".format(delta[0], delta[1], delta[2], delta[3], delta[4], delta[5], self.portfolio.getCurrentState()["total_in_usd"]))

        # store weights as a pickle dump to reuse later
        with open(self.weightPath, 'w') as f:
            pickle.dump(self.weights, f)

        # store weights in a easily readable formate
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

    def testAndTrain(self, n_train=100, n_test=100):
        """
            Runs both the training and testing portions of the algorithm
        """
        print "TRAINING"
        training = self.trainAgent(n_iter=n_train)
        training.to_csv("results/" + "train_" + self.featExtractor.__class__.__name__ + '.csv')
        print "TESTING"
        test = []
        for i in range(n_test):
            test.append(self.runTest())
        test = pd.DataFrame(test, columns=['returns', 'asset_value'])
        test.to_csv("results/" + "test_" + self.featExtractor.__class__.__name__ + '.csv')
        return training, test

