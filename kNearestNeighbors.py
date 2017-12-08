import math

import pandas as pd
import numpy as np

from sklearn.neighbors import KNeighborsClassifier
from extractors import *

# Algorithm Parameters
# Number of neighbors to use in the classifier.
k = 3
# Bounds on the data for each part of the algorithm
training_bound = 0.6
fit_bound = 0.85

# select which feature extractor to use
extractor = KNearestNeighborsExtractor()

# select which data to train and test on
file_name = "15min_manyFeatures.csv"

# Read in our data
print "Opening file..."
df = pd.read_csv(file_name, parse_dates=True) 
# remove datapoints without all features defined
df = df.dropna()
# reset our index after dropping invalid datapoints
df = df.reset_index(drop=True)


# create list of labels - 'increase' or 'decrease' for each datapoint
print "Creating label list.."
all_labels = []
for i in range(len(df["weighted_price"]) - 1):
    if df["weighted_price"][i] < df["weighted_price"][i+1]:
        all_labels.append("decrease")
    else:
        all_labels.append("increase")

# create feature vectors using the given extractor
print "Creating feature list..."
feature_vectors = []
for index, row in df.iterrows():
	feature_vectors.append(extractor.getFeatures(row))

assert len(feature_vectors) == len(all_labels) + 1

training_datapoints = int(math.floor(len(all_labels) * training_bound))

train_labels = all_labels[:training_datapoints]
train_features = feature_vectors[:training_datapoints]


# set up the classifier
neigh = KNeighborsClassifier(n_neighbors=k)
# fit the classifier to the data
neigh.fit(feature_vectors, labels)