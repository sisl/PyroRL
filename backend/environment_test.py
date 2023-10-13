'''
Unit tests for each of the functions in environment.py
'''
from environment.environment import *
import numpy as np

def dummy_environment():
    """
    Set up environment for the grid world.
    """
    # Define hardcoded world variables (THESE SHOULD BE DYNAMICALLY GENERATED LATER)
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]} # path: populated areas
    action_to_pop_and_path = {0:([1,2],0), 1:([1,2],1), 2:([4,8],2), 3:([4,8],3), 4:([8, 7],4), 5:([8, 7],5), 6:([6,4],6), 7:None} # map action to actual population center and path to take
    actions = [0,1,2,3,4,5,6,7]


    # Initialize fire world
    test_world = FireWorld(10,10,populated_areas,paths,paths_to_pops,actions,action_to_pop_and_path)
    return test_world

def test_setup():
    """
    Test to set up the grid world, try running simple test.
    """
    test_world = dummy_environment()
    for i in range(200):
        test_world.advance_to_next_timestep()
        reward = test_world.get_state_utility()
        print(reward)
