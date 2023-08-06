'''
Unit tests for each of the functions in environment.py
'''
from environment.environment import *
import numpy as np

'''
Make a dummy environment to test out each of the functions
'''
def dummy_environment():
    # Fire Environment API Class
    fire_env = FireEnvironment()

    # Array of all land cells in the grid
    state = np.array([
        [LandCell(8.5), LandCell(8.5), LandCell(8.5), LandCell(8.5)],
        [LandCell(8.5), LandCell(8.5), LandCell(8.5), LandCell(8.5)],
        [LandCell(8.5), LandCell(8.5), LandCell(8.5), LandCell(8.5)],
        [LandCell(8.5), LandCell(8.5), LandCell(8.5), LandCell(8.5)]
    ])
    return fire_env, state

'''
Corresponding to deplete_fuel()
'''
def test_deplete_fuel():
    # Run the deplete fuel function
    fire_env, state = dummy_environment()
    new_state = fire_env.deplete_fuel(state)

    # Verify values have been edited by none
    for i, j in np.ndindex(new_state.shape):
        assert state[i, j].fuel == new_state[i, j].fuel