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

from .environment_constant import fire_mask

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

    def __init__(self, num_rows, num_cols, populated_areas, paths, paths_to_pops, num_fire_cells = 2, custom_fire_locations = None):
        """
        The constructor defines the state and action space, initializes the fires,
        and sets the paths and populated areas.
        """
        # Define the state and action space
        self.reward = 0
        self.state_space = np.zeros([5, num_rows, num_cols])
        self.actions = list(np.arange(len(paths) + 1)) # extra action for doing nothing

        # Associate paths with populated areas and actions
        # Note: there seems to be an error that keeps popping up where this dictionary is not
        # getting properly created. Would investigate...
        self.paths_to_pops = paths_to_pops # path index: list of pop x,y indices [[x,y],[x,y],...]

        # We want to remember which action index corresponds to which population center
        # and which path (because we just provide an array like [1,2,3,4,5,6,7]) which
        # would each be mapped to a given population area taking a given path
        self.action_to_pop_and_path = { self.actions[-1] : None}
        for key in self.paths_to_pops:
            self.action_to_pop_and_path[key] = (paths_to_pops[key], key) # action index: list of pop x,y index and path index [[x,y],path_index]

        # State for the evacuation of populated areas
        self.evacuating_paths = {} # path_index : list of pop x,y indices that are evacuating [[x,y],[x,y],...]
        self.evacuating_timestamps = np.full((num_rows, num_cols), np.inf)

        # Initialize placement of fire cells
        if custom_fire_locations:
            fire_rows = custom_fire_locations[:,0]
            fire_cols = custom_fire_locations[:,1]
            self.state_space[FIRE_INDEX, fire_rows, fire_cols] = 1
        else:
            for _ in range(num_fire_cells):
                self.state_space[FIRE_INDEX, random.randint(0, num_rows - 1), random.randint(0, num_cols - 1)] = 1

        # Initialize fuel levels
        # Note: make the fire spread parameters to constants?
        num_values = num_rows * num_cols
        self.state_space[FUEL_INDEX] = np.random.normal(8.5,3,num_values).reshape((num_rows,num_cols))

        # Initialize populated areas
        pop_rows, pop_cols = populated_areas[:,0], populated_areas[:,1]
        self.state_space[POPULATED_INDEX, pop_rows, pop_cols] = 1

        # Initialize paths
        # Note: right now paths is different from self.paths but we can change this later if needed
        self.paths = []
        for path in paths:
            path_array = np.array(path)
            path_rows, path_cols = path_array[:,0], path_array[:,1]
            self.state_space[PATHS_INDEX,path_rows,path_cols] += 1

            # each path in self.paths is a list that records what the path is and whether or not the path still exists (i.e. has
            # not been destroyed by a fire)
            self.paths.append([np.zeros((num_rows, num_cols)), True])
            self.paths[-1][0][path_rows, path_cols] += 1

        # Set the timestep
        self.time_step = 0

    def sample_fire_propogation(self):
        """
        Sample the next state of the wildfire model.
        """
        # Drops fuel level of enflamed cells
        self.state_space[FUEL_INDEX,self.state_space[FIRE_INDEX] == 1] -= 1
        self.state_space[FUEL_INDEX,self.state_space[FUEL_INDEX] < 0] = 0

        # Extinguishes cells that have run out of fuel
        self.state_space[FIRE_INDEX,self.state_space[FUEL_INDEX,:] <= 0] = 0

        # Runs kernel of neighborhing cells where each row corresponds to the neighborhood of a cell
        torch_rep = torch.tensor(self.state_space[FIRE_INDEX]).unsqueeze(0)
        y = torch.nn.Unfold((5,5), dilation = 1, padding = 2)
        z = y(torch_rep)

        # The relative importance of each neighboring cell is weighted
        z = z * fire_mask

        # Unenflamed cells are set to 1 to eliminate their role to the fire spread equation
        z[z == 0] = 1
        z = z.prod(dim = 0)
        z = 1 - z.reshape(self.state_space[FIRE_INDEX].shape)

        # From the probability of an ignition in z, new fire locations are randomly generated
        prob_mask = torch.rand_like(z)
        new_fire = (z > prob_mask).float()

        # These new fire locations are added to the state
        self.state_space[FIRE_INDEX] = np.maximum(np.array(new_fire), self.state_space[FIRE_INDEX])

    # Note to self: make sure to update evacuation timestep state
    def update_paths_and_evactuations(self):
        """
        Performs three functions:
        1. Remove paths that been burned down by a fire
        2. Also stops evacuating any areas that were taking a burned down path
        3. Also decrements the evacuation timestamps
        """
        self.state_space[FIRE_INDEX][1,1] = 1
        for i in range(len(self.paths)):
            # Decrement path counts and remove path
            if self.paths[i][1] and np.sum(np.logical_and(self.state_space[FIRE_INDEX], self.paths[i][0])) > 0:
                self.state_space[PATHS_INDEX] -= self.paths[i][0]
                self.paths[i][1] = False

                # Stop evacuating an area if it was taking the removed path
                if i in self.evacuating_paths:
                    pop_centers = np.array(self.evacuating_paths[i])[0]
                    pop_rows, pop_cols = pop_centers[:,0], pop_centers[:,1]

                    # Reset timestamp and evacuation index
                    self.evacuating_timestamps[pop_rows,pop_cols] = np.inf
                    self.state_space[EVACUATING_INDEX, pop_rows, pop_cols] = 0
                    del self.evacuating_paths[i]

            elif i in self.evacuating_paths: # we need to decrement the evacuating paths timestep

                # for the below, this code works for if multiple population centers are taking the same path and
                # finish at the same time, but if we have it so that two population centers can't take the same
                # path it could probably be simplified
                pop_centers = np.array(self.evacuating_paths[i])[0]
                pop_rows, pop_cols = pop_centers[:,0], pop_centers[:,1]
                self.evacuating_timestamps[pop_rows,pop_cols] -= 1
                done_evacuating = np.where(self.evacuating_timestamps == 0)
                self.state_space[EVACUATING_INDEX, done_evacuating] = 0
                self.state_space[POPULATED_INDEX, done_evacuating] = 0

                # the forbidden for loop (maybe think of a way to do differently later)
                # note that right now it is going to be vastly often the case that two
                # population cases don't finish evacuating along the same path at the same
                # time right now, so this is an extremely rare edge case, meaning that most often
                # this for loop will run for a single iteration
                done_evacuating = np.array([done_evacuating[0], done_evacuating[1]])
                done_evacuating = np.transpose(done_evacuating)
                for j in range(done_evacuating.shape[0]):
                    self.evacuating_paths[i][0].remove(list(done_evacuating[j]))

                    # this population center is done evacuating, so we can set its timestamp back to infinity
                    # (this is important so that we don't try to remove this from self.evacuating paths twice -
                    # was causing a bug)
                    update_row, update_col = done_evacuating[j,0], done_evacuating[j,1]
                    self.evacuating_timestamps[update_row, update_col] = np.inf

                # no more population centers are using this path, so we delete it
                if len(self.evacuating_paths[i][0]) == 0:
                    del self.evacuating_paths[i]

    def advance_to_next_timestep(self):
        """
        Take three steps:
        1. Advance fire forward one timestep
        2. Update paths and evacuation
        3. Accumulate reward and document enflamed areas
        """
        self.sample_fire_propogation()
        self.update_paths_and_evactuations()
        self.accumulate_reward()
        self.time_step += 1

    def accumulate_reward(self):
        """
        Mark enflamed areas as no longer populated or evacuating and calculate reward.
        """
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

    def set_action(self, action):
        """
        Allow the agent to take an action within the action space.
        """
        # Check that there is an action to take
        if self.action_to_pop_and_path[action] and len(self.action_to_pop_and_path[action][0]) > 0:
            pop_cell, path_index = self.action_to_pop_and_path[action]
            pop_cell_row, pop_cell_col = pop_cell[0][0], pop_cell[0][1]

            # Ensure that the path chosen and populated cell haven't burned down and it's not already evacuating
            if (self.paths[path_index][1] and self.state_space[POPULATED_INDEX,pop_cell_row, pop_cell_col] == 1
                and self.evacuating_timestamps[pop_cell_row, pop_cell_col] == np.inf):

                # Add to evacuating paths and update state + timestamp
                # Note: we need to add a test for this case (two pop centers choosing to take the same path)
                if path_index in self.evacuating_paths:
                    self.evacuating_paths[path_index].append(pop_cell)
                else:
                    self.evacuating_paths[path_index] = [pop_cell]
                self.state_space[EVACUATING_INDEX,pop_cell_row, pop_cell_col] = 1
                self.evacuating_timestamps[pop_cell_row, pop_cell_col] = 10

    def get_state_utility(self):
        """
        Get the total amount of utility given a current state.
        """
        present_reward = self.reward
        self.reward = 0
        return present_reward

    def get_actions(self):
        """
        Get the set of actions available to the agent.
        """
        return self.actions

    def get_timestep(self):
        """
        Get current timestep of simulation
        """
        return self.time_step

    def get_state(self):
        """
        Get the state space of the current configuration of the gridworld.
        """
        return self.state_space

    def get_terminated(self):
        """
        Get the status of the simulation.
        """
        return ( self.time_step >= 100 )
