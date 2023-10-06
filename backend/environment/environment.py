'''
Environment for Wildfire Spread
'''
import copy
import math
from os import stat
import numpy as np
from scipy.stats import bernoulli

class FireWorld:
    paths_list: list

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
    print(test.state_space)


# This is the old code that is being used as a base to start building off of
"""
class LandCell:
    '''
    Data structure to represent a cell of land
    '''
    fire: bool
    fuel: float
    populated: bool

    def __init__(self, fire, fuel, populated):
        self.fire = fire
        self.fuel = fuel
        self.populated = populated

class EvacuationPath:
    '''
    Data structure to account for a set of land cells for evacuation
    '''
    path_locations: np.array([])
    evacuation_time: int
    active: bool

    def __init__(self, path_locations, evacuation_time, active):
        self.path_locations = path_locations
        self.evacuation_time = evacuation_time
        self.active = active 

class PopulatedArea:
    '''
    Contains details about the set of populated areas
    '''
    i: int
    j: int
    evacuating: bool
    remaining_time: int
    available_paths: np.array([])
    current_path: EvacuationPath

    def __init__(self, i, j, evacuating, remaining_time, available_paths, current_path):
        self.i = i
        self.j = j
        self.evacuating = evacuating
        self.remaining_time = remaining_time
        self.available_paths = available_paths
        self.current_path = current_path

# [TO-DO]: currently making this return stuff, so can be useful in front-end work?
# [TO-DO]: abstract 'np.nditer' calls to one-liner helper function?
# [TO-DO]: put a type with each of the parameters
class FireEnvironment:
    '''
    Class to orchestrate the entire environment
    '''
    def __init__(self):
        # [TO-DO]: do some more fancy stuff here
        print("Initialized the environment")

    '''
    Helper function to calculate distance
    '''
    def calculate_distance(self, x_one, y_one, x_two, y_two):
        return math.sqrt(((x_one - x_two) ** 2) + ((y_one - y_two) ** 2) ** 2)

    '''
    Deplete the fuel and check across all states
    '''
    def deplete_fuel(self, state):
        # Helper function for each cell
        def edit_cell(c: LandCell):
            if (c.fire):
                c.fuel = max(0, c.fuel - 1)
                if (not c.fuel):
                    c.fire = False
            return c
        
        # Vectorize operation
        return np.vectorize(edit_cell)(state)

    '''
    At each point in the grid world, determine if there will be a fire by looking 
    at the amount of fuel and the surrounding states.
    '''
    def sample_next_state(self, state, distance_constant, pathed_areas, evacuation_paths):
        # Set constants
        new_state = copy.deepcopy(state)
        observation_distance = 2

        # Not vectorized -- figure out how to do it
        for i in range(state.shape[0]):
            for j in range(state.shape[1]):
                cell = state[i][j]

                # Use SISL paper to calculate probability of there being a fire
                probability = 1
                for n_i in range(max(0, i - observation_distance), min(state.shape[0], i + observation_distance)):
                    for n_j in range(max(0, j - observation_distance), min(state.shape[1], j + observation_distance)):
                        if (i != n_i and j != n_j and state[n_i][n_j].fire):
                            probability *= 1 - (distance_constant * ((1 / self.calculate_distance(i, j, n_i, n_j)) ** 2))

                # Calculate final probability using a Bernoulli distribution
                probability = 1 - probability
                new_state[i][j].fire = bernoulli.rvs(probability, size=1)

                # See if a newly fire area is part of a path
                if (new_state[i][j].fire and i in pathed_areas and j in pathed_areas[i]):
                    index = pathed_areas[i][j]
                    evacuation_paths[index].active = False
        
        return new_state

        
    '''
    Updating the action space based on current state of the wildfire
    [TO-DO]: Line in this function about returning the numpy representation, 
    unsure what needs to happen
    '''
    def update_action_space(self, state, action_space):
        # Helper function to individually update action
        def update_action(a: PopulatedArea):
            if (a.evacuating and a.remaining_time):
                if (not a.current_path.active):
                    a.remaining_time = math.inf
                    a.evacuating = False
                    a.current_path = None
                else:
                    a.remaining_time -= 1
                    if (not a.remaining_time):
                        state[a.i][a.j].populated = False
            return a
        
        # Vectorize and return state and action space
        action_space = np.vectorize(update_action)(action_space)
        return state, action_space

    '''
    Calculate the utility of all of the states
    '''
    def get_state_utility(self, state, action_space):
        # Helper function to calculate entire reward
        def calculate_reward(a: PopulatedArea):
            # If populated area is on fire and not evacuated, incur -100 reward
            reward = 0
            if (a.remaining_time and state[a.i][a.j].fire):
                reward -= 100
                a.remaining_time = 0
                state[a.i][a.j].populated = False
            
            # Else, if current populated area is not evacuating, add 1 reward
            elif ((not a.evacuating) and a.remaining_time):
                reward += 1
            return reward

        # Vectorize operation and return the reward
        return np.sum(np.vectorize(calculate_reward)(action_space))

    '''
    Function to take action after sampling a state
    Note: Only take an action if it does something (i.e., not evacuating an evacuated area or
    taking a path that isn't active)
    '''
    def take_action(self, action, action_space):
        # Only take action if we're doing something
        i, j = action[0], action[1]
        if (i != 1 and action_space[i].remaining_time 
            and not action_space[i].evacuating 
            and action_space[i].available_paths[j].active):

            # Update action space path and evacuation
            action_space[i].current_path = action_space[i].available_paths[j]
            action_space[i].evacuating = True
            action_space[i].remaining_time = action_space[i].current_path.evacuation_time
        return action_space
        

# [TO-DO]: placeholder to initialize the environment
if __name__ == "__main__":
    test = FireEnvironment()
"""