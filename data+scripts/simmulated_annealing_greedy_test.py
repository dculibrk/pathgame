# coding: utf-8

# In[11]:


from __future__ import print_function

import math
# from anneal import *
import csv

from pprint import pprint

import pickle

import random

from anneal import Annealer


def distance(a, b):
    """Calculates Manhattan distance between two  coordinates."""

    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def init_NN(init_state, cities):
    """
    Initialize the initial soltution with a simple heuristic: always
    go to the nearest city.

    Even if this algoritmh is extremely simple, it works pretty well
    giving a solution only about 25% longer than the optimal one (cit. Wikipedia),
    and runs very fast in O(N^2) time complexity.

    """

    start = init_state[0] # we expect the depot to be at the start of the list
    must_visit = init_state
    path = [start]
    must_visit.remove(start)
    dbg_path = [cities[start]]
    while must_visit:
        nearest = min(must_visit, key=lambda x: distance(cities[path[-1]], cities[x]))
        path.append(nearest)
        dbg_path.append(cities[nearest])
        must_visit.remove(nearest)

    return path

class TravellingSalesmanProblem(Annealer):
    """Test annealer with a travelling salesman problem.

    """

    # pass extra data (the distance matrix) into the constructor

    def __init__(self, state, distance_matrix):
        self.distance_matrix = distance_matrix

        super(TravellingSalesmanProblem, self).__init__(state)  # important!

    def move(self):
        """Swaps two cities in the route."""
        """But we do not touch the start"""

        a = random.randint(1, len(self.state) - 1)

        b = random.randint(1, len(self.state) - 1)

        self.state[a], self.state[b] = self.state[b], self.state[a]

    def energy(self):
        """Calculates the length of the route."""

        e = 0

        for i in range(len(self.state)):
            e += self.distance_matrix[self.state[i - 1]][self.state[i]]

        #e += self.distance_matrix[self.state[i]][self.state[0]]

        return e




if __name__ == '__main__':

    # we'll store the results in the dictionary indexed by the order of the problems in the original 'game_16103.csv' file
    # so the format is { rowno : { 'energy' : ?, 'order' : final_state,  'greedye' : ? }}
    results = {}
    rowno = 0
    with open('game_16103.csv', mode='r') as csv_file:

        csv_reader = csv.DictReader(csv_file)


        for row in csv_reader:

            if rowno < 64:
                rowno = rowno + 1
                continue; #skip the first rows that were not taken into account, as these were debugging runs missing data

            dp = eval(row['destinationpoints'])
            # create a new dictionary for the destinations
            cities = {'0': (300, 260)}

            i = 1;
            for element in dp:
                cities[str(i)] = (element['x'], element['y'])
                i = i + 1

            #pprint(cities)

            # initial state, a randomly-ordered itinerary

            init_state = list(cities.keys())

            while init_state[0] != '0':
                init_state = init_state[1:] + init_state[:1]  # rotate depo to start

            #print(init_state)

            #random.shuffle(init_state[1:])
            init_state = init_NN(init_state, cities) #initialize with Nearest Neighbor

            #print(init_state)

            # create a distance matrix

            distance_matrix = {}

            for ka, va in cities.items():

                distance_matrix[ka] = {}

                for kb, vb in cities.items():

                    if kb == ka:

                        distance_matrix[ka][kb] = 0.0

                    else:

                        distance_matrix[ka][kb] = distance(va, vb)

            tsp = TravellingSalesmanProblem(init_state, distance_matrix)

            tsp.steps = 100000

            # since our state is just a list, slice is the fastest way to copy

            tsp.copy_strategy = "slice"

            #get the initial energy

            initial_energy = tsp.energy()

            state, e = tsp.anneal()

            #while state[0] != 'New York City':
            #    state = state[1:] + state[:1]  # rotate NYC to start

            print()

            #print("%i distanca:" % e)

            #for city in state:
            #   print("\t", city)

            results[rowno-64] = {'energy': e, 'order': state, 'greedye': initial_energy}

            rowno = rowno + 1

            if rowno > 75:
                break

    pickle_out = open("annealing_greedy_results.pickle", "wb")
    pickle.dump(results, pickle_out)
    pickle_out.close()

