'''
Unit tests for each of the functions in environment.py
'''
from environment.environment import *
import numpy as np

def dummy_environment():
    """
    Set up environment for the grid world
    """
    # Define hardcoded world variables
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)

    # Initialize fire world
    test_world = FireWorld()
    test_world.sample_constructor(10, 10, populated_areas, paths)
    return test_world

def test_world():
    test_world = dummy_environment()