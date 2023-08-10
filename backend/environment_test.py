'''
Unit tests for each of the functions in environment.py
'''
from collections import defaultdict
import copy
from environment.environment import *
import math
import numpy as np
import random

'''
Make a dummy environment to test out each of the functions.
Based on constructor from old file.
'''
def dummy_environment():
    # Fire Environment API Class
    fire_env = FireEnvironment()

    # Array of all land cells in the grid
    dimension = 20
    state = np.array([[LandCell(0, False, False) for j in range(dimension)] for i in range(dimension)])

    # Place initial fire seeds
    burn_count = 2
    for i in range(burn_count):
        x, y = random.randint(0, dimension - 1), random.randint(0, dimension - 1)
        while (state[x][y].fire):
            x, y = random.randint(0, dimension - 1), random.randint(0, dimension - 1)
        state[x][y].fire = True

    # Set fuel levels
    mean, std = 8.5, 3
    def set_fuel(cell):
        cell.fuel = max(0, np.random.normal(mean, std))
    np.vectorize(set_fuel)(state)

    # Create evacuation paths
    evacuation_paths = []
    path = np.array([(17, j) for j in range(5)])
    evacuation_paths.append(EvacuationPath(path, 3, True))
    path = np.concatenate((np.array([(17, j) for j in range(6, 11)]), np.array([(i, 10) for i in range(18, 20)])))
    evacuation_paths.append(EvacuationPath(path, 4, True))
    path = np.concatenate((np.array([(i, 9) for i in range(9)]), np.array([(8, 10)])))
    evacuation_paths.append(EvacuationPath(path, 3, True))
    path = np.array([(9, j) for j in range(12)])
    evacuation_paths.append(EvacuationPath(path, 6, True))
    path = np.concatenate((np.array([(8, j) for j in range(12, 14)]), np.array([(i, 14) for i in range(8, 11)]), np.array([(11, j) for j in range(14, 20)])))
    evacuation_paths.append(EvacuationPath(path, 7, True))

    # Build the pathed areas
    pathed_areas = defaultdict(dict)
    for i in range(len(evacuation_paths)):
        for loc in evacuation_paths[i].path_locations:
            pathed_areas[loc[0]][loc[1]] = i
        if (state[loc[0]][loc[1]].fire):
            evacuation_paths[i].active = False

    # Create action space
    action_space = []
    action_space.append(PopulatedArea(8, 11, False, math.inf, np.array([evacuation_paths[2:5]]), None))
    action_space.append(PopulatedArea(17, 5, False, math.inf, np.array([evacuation_paths[0:2]]), None))

    # Indicate populated areas also on game state
    for area in action_space:
        state[area.i][area.j].populated = True

    # Return dummy state!
    return fire_env, state, evacuation_paths, pathed_areas, action_space

'''
Corresponding to deplete_fuel()
'''
def test_deplete_fuel():
    # Create dummy variables and run the deplete fuel function
    fire_env, state, _, _, _ = dummy_environment()
    old_state = copy.deepcopy(state)
    new_state = fire_env.deplete_fuel(state)

    # Verify values have been edited
    for i, j in np.ndindex(new_state.shape):
        if (old_state[i, j].fire):
            assert old_state[i, j].fuel - 2 <= new_state[i, j].fuel
        else:
            assert old_state[i, j].fuel == new_state[i, j].fuel

'''
Corresponding to get_state_utility()
'''
def test_get_state_utility():
    # Create dummy variables and run state utility function
    fire_env, state, _, _, action_space = dummy_environment()
    reward = fire_env.get_state_utility(state, action_space)
    assert reward == 2