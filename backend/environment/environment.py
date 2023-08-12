'''
Environment for Wildfire Spread
'''
import math
import numpy as np

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
        if (i != 1 and action_space[i].remaining_time and not action_space[i].evacuating and action_space[i].available_paths[j].active):
            action_space[i].current_path = action_space[i].available_paths[j]
            action_space[i].evacuating = True
            action_space[i].remaining_time = action_space[i].current_path.evacuation_time
        return action_space
        

# [TO-DO]: placeholder to initialize the environment
if __name__ == "__main__":
    test = FireEnvironment()