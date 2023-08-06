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

    def __init__(self, fuel):
        self.fuel = fuel
        self.fire = False
        self.populated = False

class EvacuationPath:
    '''
    Data structure to account for a set of land cells for evacuation
    '''
    path_locations: np.array([])
    evacuation_time: int
    active: bool

    def __init__(self):
        self.active = True

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

    def __init__(self):
        self.evacuating = False
        self.current_path = None

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
        def edit_cell(cell: LandCell):
            if (cell.fire):
                cell.fuel = max(0, cell.fuel - 1)
                if (not cell.fuel):
                    cell.fire = False
            return cell
        
        # Vectorize operation
        return np.vectorize(edit_cell)(state)

    '''
    Updating the action space based on current state of the wildfire
    '''
    def update_action_space(self, state, action_space):
        with np.nditer(action_space, flags=["refs_OK"], op_flags=['readwrite']) as it:
            for a in it:
                if (a.evacuating and a.remaining_time):
                    if (not a.current_path.active):
                        a.remaining_time = math.inf
                        a.evacuating = False
                        a.current_path = None
                        # [TO-DO]: Line here about returning the numpy representation, unsure what needs to happen
                    else:
                        a.remaining_time -= 1
                        if (not a.remaining_time):
                            state[a.i][a.j].populated = False
        return state, action_space

    '''
    Calculate the utility of all of the states
    '''
    def get_state_utility(self, state, action_space):
        reward = 0
        with np.nditer(action_space, flags=["refs_ok"], op_flags=['readwrite']) as it:
            for a in it:
                # If populated area is on fire and not evacuated, incur -100 reward
                if (a.remaining_time and state[a.i][a.j].fire):
                    reward -= 100
                    a.remaining_time = 0
                    state[a.i][a.j].populated = False
                
                # Else, if current populated area is not evacuating, add 1 reward
                elif ((not a.evacuating) and a.remaining_time):
                    reward += 1
        return reward

# [TO-DO]: placeholder to initialize the environment
if __name__ == "__main__":
    test = FireEnvironment()