'''
Environment for Wildfire Spread
'''
import copy
import math
import random
from os import stat
import numpy as np
from scipy.stats import bernoulli
from collections import defaultdict

class FireWorld:
    """
    We represent the world as a 5 by n by m tensor. n by m is the size of the grid world,
    while the 5 represents each of the following: [fire, fuel, populated, evacuating, paths]
    """
    paths_list: list

    # order of state space is fire?, fuel, populated?, evacuating?, paths
    def __init__(self, num_rows, num_cols, populated_areas, paths, custom_placement = False, num_fire_cells = 2, custom_locations = None):
        # Define the state space
        self.state_space = np.zeros([5, num_rows, num_cols])

        # initialize the fire cells
        if custom_placement:
            fire_rows = custom_locations[:,0]
            fire_cols = custom_locations[:,1]
            self.state_space[0, fire_rows, fire_cols] = 1
        else: 
            for _ in range(num_fire_cells):
                self.state_space[0, random.randint(0,9), random.randint(0,9)] = 1


        # initialize the fuel cells
        num_values = num_rows * num_cols
        self.state_space[1] = np.random.normal(8.5,3,num_values).reshape((num_rows,num_cols))

        # initialize the populated areas 
        pop_rows = populated_areas[:,0]
        pop_cols = populated_areas[:,1]
        self.state_space[2, pop_rows, pop_cols] = 1

        # initialize the paths
        self.paths_array = paths
        for path in self.paths_array:
            path_array = np.array(path)
            rows = path_array[:,0]
            cols = path_array[:,1]
            self.state_space[4,rows,cols] += 1

        # Note: We'll also need to be able to denote which path is associated with each pop center (probably a list of lists, but do this later)
    
    """
    def remove_paths(self):
        path_cells_on_fire = np.logical_and(self.state_space[0], self.state_space[4]) # whatever cells are one fire and are on a path will be one
        print(self.state_space[4])
        print("")
        print(self.state_space[0])
        print("")
        print(path_cells_on_fire)
        print("")
        on_fire_indices = np.transpose(np.nonzero(path_cells_on_fire)).tolist()
        # for path in self.paths_array:
        #     if set(path).isdisjoint(set())
    """

    def get_state_utility(self):
        """
        Get the total amount of utility given a current state.
        """
        # Get which populated areas are on fire and evacuating
        reward = 0
        populated = np.where(self.state_space[2] == 1)
        fire = self.state_space[0][populated]
        evacuating = self.state_space[3][populated]

        # Update reward
        reward -= 100 * fire.sum()
        reward += len((np.where(fire + evacuating == 0))[0])
        return reward
        

if __name__ == "__main__":
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths_array = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    test = FireWorld(10,10,populated_areas,paths_array)
    test.remove_paths()
