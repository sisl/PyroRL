'''
Environment for Wildfire Spread
'''
import copy
import math
from os import stat
import numpy as np
from scipy.stats import bernoulli
from collections import defaultdict

class FireWorld:
    paths_list: list

    def sample_constructor(self, n, m, populated_areas, paths):
        """
        Updated constructor to make environment more generalizable
        """
        # Define the state space and set the populated areas
        self.state_space = np.zeros([5, n, m])
        pop_indices = np.ravel_multi_index(populated_areas.T, self.state_space[2].shape)
        self.state_space[2].ravel()[pop_indices] = 1

        # Update list of paths and maintain number of paths for each area
        self.paths_list = paths
        path_nums = defaultdict(int)
        def update_paths(path):
            for p in path:
                path_nums[tuple(p)] += 1
        np.vectorize(update_paths)(self.paths_list)

        # Update state space to reflect new paths
        path_nums = (np.array(list(path_nums.items()), dtype=object))
        rows, cols = zip(*path_nums[:, 0])
        self.state_space[4][rows, cols] = path_nums[:, 1]

    # order of state space is fire?, fuel, populated?, evacuating?, paths
    def __init__(self): # later we will have rows and cols that the user can enter when creating the world
        self.state_space = np.zeros([5, 10, 10]) # rows and cols would go where the 10, 10 values are
        populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
        self.state_space[2].ravel()[np.ravel_multi_index(populated_areas.T, self.state_space[2].shape)] = 1 # set the populated areas
        one_path_cells = np.array([[1,0],[1,1], [2,2], [3,2],[4,2],[4,1],[4,0],[2,9],[2,8],[3,8],[5,8],[6,9],[6,7],[7,7],[8,6],[7,5],[7,4]])
        two_path_cells = np.array([[8,5],[6,8],[9,5],[6,9]])

        # setting the paths
        self.state_space[4].ravel()[np.ravel_multi_index(one_path_cells.T, self.state_space[4].shape)] = 1 
        self.state_space[4].ravel()[np.ravel_multi_index(two_path_cells.T, self.state_space[4].shape)] = 2

        # hard code all the different paths
        self.paths_list = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]])

        # Note: We'll also need to be able to denote which path is associated with each pop center (probably a list of lists, but do this later)
    
    # gonna flush out the rest of this tomorrow
    def remove_paths(self):
        path_cells_on_fire = np.logical_and(self.state_space[0], self.state_space)
        on_fire_indices = np.transpose(np.nonzero(path_cells_on_fire))
        for path in on_fire_indices:
            location = np.where(self.paths_list==path)

if __name__ == "__main__":
    test = FireWorld()
    # Constructor
    print(test.state_space)
    print("------")

    # Potential other constructor? To make code more generalizable
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    test.sample_constructor(10, 10, populated_areas, paths)