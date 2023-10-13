"""
Environment for Wildfire Spread
"""
from collections import namedtuple
import copy
from importlib.resources import path
import itertools
import numpy as np
from os import stat
from pickle import POP
import random
from scipy.stats import bernoulli
import torch

from environment.environment_constant import fire_mask

"""
Indices corresponding to each layer of state
"""
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

    # Reminder: we want to remove custom_fire_placement eventually (because we can just use the None from custom_fire_locations)
    def __init__(self, num_rows, num_cols, populated_areas, paths, paths_to_pops, actions,action_to_pop_and_path, custom_fire_placement = False, num_fire_cells = 2, custom_fire_locations = None):
        # Define the state space
        self.reward = 0
        self.state_space = np.zeros([5, num_rows, num_cols])

        #remember which paths are associated with each population center
        self.paths_to_pops = paths_to_pops #path index: list of pop x,y indices [[x,y],[x,y],...]

        # remember which path an evacuating area chose to take
        self.evacuating_paths = {} # path_index : list of pop x,y indices that are evacuating [[x,y],[x,y],...]

        # state to know how much timestamps are left for the evacuating areas
        self.evacuating_timestamps = np.full((num_rows, num_cols), np.inf)

        #initialize self.actions
        self.actions = actions

        # we want to remember which action index corresponds to which population center
        # and which path (because we just provide an array like [1,2,3,4,5,6,7]) which
        # would each be mapped to a given population area taking a given path
        self.action_to_pop_and_path = action_to_pop_and_path # action index: list of pop x,y index and path index [[x,y],path_index]

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
        pop_rows = populated_areas[:,0]
        pop_cols = populated_areas[:,1]
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

    
    def sample_fire_propogation(self):
        # Drops fuel level of enflamed cells
        self.state_space[FUEL_INDEX,self.state_space[FIRE_INDEX] == 1] -= 1
        self.state_space[FUEL_INDEX,self.state_space[FUEL_INDEX] < 0] = 0
        # self.state_space[FUEL_INDEX] = np.max(self.state_space[FUEL_INDEX], np.zeros(self.state_space[FUEL_INDEX].shape))


        #Extinguishes cells that have run out of fuel
        self.state_space[FIRE_INDEX,self.state_space[FUEL_INDEX,:] <= 0] = 0

        # Runs kernel of neighborhing cells where each row corresponds to the neighborhood of a cell
        torch_rep = torch.tensor(self.state_space[FIRE_INDEX]).unsqueeze(0)
        y = torch.nn.Unfold((5,5), dilation = 1, padding = 2)
        z = y(torch_rep)

        # the relative importance of each neighboring cell is weighted
        z = z * fire_mask

        # Unenflamed cells are set to 1 to eliminate their role to the fire spread equation
        z[z == 0] = 1
        z = z.prod(dim = 0)
        z = 1 - z.reshape(self.state_space[FIRE_INDEX].shape)

        # from the probability of an ignition in z, new fire locations are randomly generated
        prob_mask = torch.rand_like(z)
        new_fire = (z > prob_mask).float()


        # These new fire locations are added to the state
        self.state_space[FIRE_INDEX] = np.maximum(np.array(new_fire), self.state_space[FIRE_INDEX])

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
                (n_rows, n_cols) = np.where(np.isin(self.state_space[FUEL_INDEX], fuel_levels))
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

    # Note to self: make sure to update evacuation timestep state
    def update_paths_and_evactuations(self):
        """
        Remove paths that been burned down by a fire. 
        Also stops evacuating any areas that were taking a burned down path. 
        Also decrements the evacuation timestamps
        """
        self.state_space[FIRE_INDEX][1,1] = 1
        for i in range(len(self.paths)):
            # check if we need to remove a path
            if self.paths[i][1] and np.sum(np.logical_and(self.state_space[FIRE_INDEX], self.paths[i][0])) > 0:
                # decrement the count for the paths in the state space
                self.state_space[PATHS_INDEX] -= self.paths[i][0]
                # remove the path
                self.paths[i][1] = False

                # stop evacuating an area if it was taking the removed path
                if i in self.evacuating_paths:
                    pop_centers = np.array(self.evacuating_paths[i])
                    pop_rows = pop_centers[:,0]
                    pop_cols = pop_centers[:,1]
                    self.evacuating_timestamps[pop_rows,pop_cols] = np.inf
                    self.state_space[EVACUATING_INDEX, pop_rows, pop_cols] = 0
                    del self.evacuating_paths[i]
            elif i in self.evacuating_paths: # we need to decrement the evacuating paths timestep

                # for the below, this code works for if multiple population centers are taking the same path and 
                # finish at the same time, but if we have it so that two population centers can't take the same 
                # path it could probably be simplified
                pop_centers = np.array(self.evacuating_paths[i])
                pop_rows = pop_centers[:,0]
                pop_cols = pop_centers[:,1]
                self.evacuating_timestamps[pop_rows,pop_cols] -= 1
                done_evacuating = np.where(self.evacuating_timestamps == 0)
                self.state_space[EVACUATING_INDEX, done_evacuating] = 0
                self.state_space[POPULATED_INDEX, done_evacuating] = 0

                # the forbidden for loop (maybe think of a way to do differently later)
                # note that right now it is going to be vastly often the case that two 
                # population cases don't finish evacuating along the same path at the same 
                # time right now, so this is an extremely rare edge case, meaning that most often
                # this for loop will run for a single iteration
                done_evacuating = np.array([done_evacuating[0],done_evacuating[1]])
                done_evacuating = np.transpose(done_evacuating)
                for j in range(done_evacuating.shape[0]):
                    update_row = done_evacuating[j,0]
                    update_col = done_evacuating[j,1]
                    self.evacuating_paths[i].remove(list(done_evacuating[j]))

                    # this population center is done evacuating, so we can set its timestamp back to infinity
                    # (this is important so that we don't try to remove this from self.evacuating paths twice - 
                    # was causing a bug)
                    self.evacuating_timestamps[update_row, update_col] = np.inf

                # no more population centers are using this path, so we delete it
                if len(self.evacuating_paths[i]) == 0:
                    del self.evacuating_paths[i]

    def advance_to_next_timestep(self):

        # Advance fire forward one timestep
        self.sample_fire_propogation()

        # Update paths
        self.remove_paths()

        # Accumulate reward and document enflamed areas
        self.accumulate_reward()



    # Finish accumulate_reward such that populated_index and evacuating_index are set to zero in as efficient a manner as possible
    # Here's my partial work
    def accumulate_reward(self):

        # Get which populated_areas areas are on fire and evacuating
        populated_areas = np.where(self.state_space[POPULATED_INDEX] == 1)
        fire = self.state_space[FIRE_INDEX][populated_areas]
        evacuating = self.state_space[EVACUATING_INDEX][populated_areas]

        # Mark enflamed areas as no longer populated or evacuating
        enflamed_populated_areas = np.where(self.state_space[FIRE_INDEX][populated_areas] == 1)[0]
        enflamed_rows = populated_areas[0][enflamed_populated_areas]
        enflamed_cols = populated_areas[1][enflamed_populated_areas]        

        # Depopulate enflamed areas and remove evacuations
        self.state_space[POPULATED_INDEX, enflamed_rows, enflamed_cols]= 0
        self.state_space[EVACUATING_INDEX, enflamed_rows, enflamed_cols] = 0

        # Update reward
        self.reward -= 100 * len(enflamed_populated_areas)
        self.reward += len((np.where(fire + evacuating == 0))[0])

    def get_state_utility(self):
        """
        Get the total amount of utility given a current state.
        """
        present_reward = self.reward
        self.reward = 0
        return present_reward
    
    def get_actions(self):
        return self.actions

    def set_action(self, action):
        if self.action_to_pop_and_path[action]: # could be the case that we do nothing and it's none
            pop_cell, path_index = self.action_to_pop_and_path[action]
            pop_cell_row = pop_cell[0]
            pop_cell_col = pop_cell[1]
            #make sure that the path chosen and the populated cell haven't burned down and it's not already evacuating
            if (self.paths[path_index][1] and self.state_space[POPULATED_INDEX,pop_cell_row, pop_cell_col] == 1 
                and self.evacuating_timestamps[pop_cell_row, pop_cell_col] == np.inf):
                if path_index in self.evacuating_paths: # note: we need to add a test for this case at some point (two pop centers choosing to take the same path)
                    self.evacuating_paths[path_index].append(pop_cell)
                else:
                    self.evacuating_paths[path_index] = [pop_cell]
                self.state_space[EVACUATING_INDEX,pop_cell_row, pop_cell_col] = 1
                self.evacuating_timestamps[pop_cell_row, pop_cell_col] = 10




