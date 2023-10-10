'''
Environment for Wildfire Spread
'''
import copy
from importlib.resources import path
import math
from pickle import POP
import random
from os import stat
import numpy as np
from scipy.stats import bernoulli
from collections import defaultdict

from collections import namedtuple

FIRE_INDEX = 0
FUEL_INDEX = 1
POPULATED_INDEX = 2
EVACUATING_INDEX = 3
PATHS_INDEX = 4

class FireWorld:
    """
    We represent the world as a 5 by n by m tensor. n by m is the size of the grid world,
    while the 5 represents each of the following: [fire, fuel, populated_areas, evacuating, paths]
    """

    # order of state space is fire?, fuel, populated_areas?, evacuating?, paths
    def __init__(self, num_rows, num_cols, populated_areas_areas, paths, custom_fire_placement = False, num_fire_cells = 2, custom_fire_locations = None):
        # Define the state space
        self.state_space = np.zeros([5, num_rows, num_cols])

        # initialize the fire cells
        if custom_fire_placement:
            fire_rows = custom_fire_locations[:,0]
            fire_cols = custom_fire_locations[:,1]
            self.state_space[FIRE_INDEX, fire_rows, fire_cols] = 1
        else: 
            for _ in range(num_fire_cells):
                self.state_space[FIRE_INDEX, random.randint(0,9), random.randint(0,9)] = 1


        # initialize the fuel cells
        num_values = num_rows * num_cols
        self.state_space[FUEL_INDEX] = np.random.normal(8.5,3,num_values).reshape((num_rows,num_cols))

        # initialize the populated_areas areas 
        pop_rows = populated_areas_areas[:,0]
        pop_cols = populated_areas_areas[:,1]
        self.state_space[POPULATED_INDEX, pop_rows, pop_cols] = 1

        # initialize the paths
        self.paths = []
        for path in paths: #right now paths is different from self.paths but we can change this later if needed
            path_array = np.array(path)
            path_rows = path_array[:,0]
            path_cols = path_array[:,1]
            self.state_space[PATHS_INDEX,path_rows,path_cols] += 1

            # each path in self.paths is a list that records what the path is and whether or not the path still exists (i.e. has
            # not been destroyed by a fire)
            self.paths.append([np.zeros((num_rows, num_cols)), True])
            self.paths[-1][0][path_rows, path_cols] += 1
        """
        self.paths = np.zeros((paths.size, num_rows, num_cols))
        index = 0 
        for path in paths: #right now paths is different from self.paths but we can change this later if needed
            path_array = np.array(path)
            path_rows = path_array[:,0]
            path_cols = path_array[:,1]
            self.state_space[4,path_rows,path_cols] += 1

            self.paths[index, path_rows, path_cols] += 1
            index += 1
        """

        # Note: We'll also need to be able to denote which path is associated with each pop center (probably a list of lists, but do this later)
    

    def remove_paths(self):
        for i in range(len(self.paths)):
            if self.paths[i][1] and np.sum(np.logical_and(self.state_space[FIRE_INDEX], self.paths[i][0])) > 0:
                # decrement the count for the paths in the state space
                self.state_space[PATHS_INDEX] -= self.paths[i][0]
                # remove the path
                self.paths[i][1] = False

    def get_state_utility(self):
        """
        Get the total amount of utility given a current state.
        """
        # Get which populated_areas areas are on fire and evacuating
        reward = 0
        populated_areas = np.where(self.state_space[POPULATED_INDEX] == 1)
        fire = self.state_space[FIRE_INDEX][populated_areas]
        evacuating = self.state_space[EVACUATING_INDEX][populated_areas]

        # Update reward
        reward -= 100 * fire.sum()
        reward += len((np.where(fire + evacuating == 0))[0])
        return reward
