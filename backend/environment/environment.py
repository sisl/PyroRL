'''
Environment for Wildfire Spread
'''
import math
import numpy as np

class land_cell:
    '''
    Data structure to represent a cell of land
    '''
    fire: bool
    fuel: float
    populated: bool

    def __init__(self):
        self.fire = False
        self.populated = False

class evacuation_path:
    '''
    Data structure to account for a set of land cells for evacuation
    '''
    path_locations: np.array([])
    evacuation_time: int
    active: bool

    def __init__(self):
        self.active = True

class populated_area:
    '''
    Contains details about the set of populated areas
    '''
    i: int
    j: int
    evacuating: bool
    remaining_time: int
    available_paths: np.array([])
    current_path: evacuation_path

    def __init__(self):
        self.evacuating = False
        self.current_path = None

# [TO-DO]: currently making this return stuff, so can be useful in front-end work?
# [TO-DO]: abstract 'np.nditer' calls to one-liner helper function?
class fire_environment:
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
        with np.nditer(state, op_flags=['readwrite']) as it:
            for s in it:
                if (s.fire):
                    s.fuel = max(0, s.fuel - 1)
                    if (not s.fuel):
                        s.fire = False
        return state

    '''
    Updating the action space based on current state of the wildfire
    '''
    def update_action_space(self, state, action_space):
        with np.nditer(action_space, op_flags=['readwrite']) as it:
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

if __name__ == "__main__":
    # Initialize environment
    test = fire_environment()

    # Initialize a land cell
    #another_test = land_cell()
    #print(another_test.fuel)

    # Initialize states and deplete fuel
    #states = np.array([[1, 2, 3], [4, 5, 6]])
    #test.deplete_fuel(states)