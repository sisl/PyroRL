"""
Unit tests for each of the functions in environment.py
"""
from wildfire_evac.wildfire_evac.envs.environment.environment import *
import numpy as np
import random

def dummy_environment():
    """
    Set up environment for the grid world.
    """
    # Define hardcoded paramaters of the gridworld -- populated areas, paths,
    # and which areas can use whicn paths.
    # Note: discuss if these should be dynamically generated or others.
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Initialize fire world
    test_world = FireWorld(10, 10, populated_areas, paths, paths_to_pops)
    return test_world

def test_setup():
    """
    Set up grid world and initiate loop of action-taking + updating.
    """
    test_world = dummy_environment()
    for i in range(25):
        # Take a random action
        all_actions = test_world.get_actions()
        action = random.randint(0, len(all_actions) - 1)
        test_world.set_action(all_actions[action])
        print("Action: " + str(action))

        # Advance the gridworld and get the reward
        test_world.advance_to_next_timestep()
        reward = test_world.get_state_utility()
        print("Reward: " + str(reward) + "\n")
