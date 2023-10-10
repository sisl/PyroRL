'''
Environment for Wildfire Spread
'''
import copy
from importlib.resources import path
from pickle import POP
import random
from os import stat
import numpy as np
from scipy.stats import bernoulli
import itertools

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
    
    def sample_next_state(self):
        # First, get all of the indices
        new_state = copy.deepcopy(self.state_space)
        (rows, cols) = new_state[FIRE_INDEX].shape
        indices = list(itertools.product(range(rows), range(cols)))

        # Find all neighbors within observation distance
        observation_distance = 2
        distance_constant = 0.094
        for pair in indices:
            row_range = list(range(max(0, pair[0] - observation_distance), min(rows, pair[0] + observation_distance) + 1))
            col_range = list(range(max(0, pair[1] - observation_distance), min(cols, pair[1] + observation_distance) + 1))
            neighbors = self.state_space[FIRE_INDEX][row_range[0]:row_range[-1] + 1, col_range[0]:col_range[-1] + 1]

            # Get fuel levels for all on fire indices
            on_fire = np.where(neighbors > 0)
            if (on_fire[0].size):
                fuels = self.state_space[FUEL_INDEX][row_range[0]:row_range[-1] + 1, col_range[0]:col_range[-1] + 1]
                fuel_levels = fuels[on_fire]

                # Calculate distances and remove the original pair
                (n_rows, n_cols) = np.where(np.isin(self.state_space[FUEL_INDEX], fuel_levels)) # np.where(self.state_space[FUEL_INDEX] == fuel_levels)
                distances = np.sqrt(((n_rows - pair[0]) ** 2) + ((n_cols - pair[1]) ** 2) ** 2)
                final_distances = distances[np.nonzero(distances)[0]]
                
                # Update cell to be on fire or not
                if (final_distances.size):
                    probabilities = 1 - (distance_constant * ((1 / final_distances) ** 2))
                    probability = 1 - np.product(probabilities)
                    new_state[FIRE_INDEX][pair[0]][pair[1]] = bernoulli.rvs(probability, size=1)

                    # Remove a path as being usable
                    for i in range(len(self.paths)):
                        if (self.paths[i][0][pair[0]][pair[1]]):
                            self.paths[i][1] = False
        
        # Update state
        self.state_space = new_state

    def remove_paths(self):
        """
        Remove paths that been burned down by a fire.
        """
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
