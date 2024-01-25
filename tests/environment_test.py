"""
Unit tests for each of the functions in environment.py
"""
import sys
from wildfire_evac.envs.environment.environment import *
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
    paths = [[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]]
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Initialize fire world
    test_world = FireWorld(10, 10, populated_areas, paths, paths_to_pops)
    return test_world

def test_initialization():
    populated_areas = np.array([[2,2],[4,1]])
    paths = [[[2,0],[2,1]], [[1,0],[1,1],[2,1],[3,1]]]
    paths_to_pops = {0:[2,2], 1:[4,1]}

    test_world = FireWorld(5, 5, populated_areas, paths, paths_to_pops)
    expected_population_array = np.array([
        [0,0,0,0,0],
        [0,0,0,0,0],
        [0,0,1,0,0],
        [0,0,0,0,0],
        [0,1,0,0,0]
    ])
    expected_path_array = np.array([
        [0,0,0,0,0],
        [1,1,0,0,0],
        [1,2,0,0,0],
        [0,1,0,0,0],
        [0,0,0,0,0]
    ])
    expected_returned_path_array = np.array([
        [0,0,0,0,0],
        [1,1,0,0,0],
        [1,1,0,0,0],
        [0,1,0,0,0],
        [0,0,0,0,0]
    ])
    assert np.array_equal(test_world.state_space[POPULATED_INDEX], expected_population_array)
    assert np.array_equal(test_world.state_space[PATHS_INDEX], expected_path_array)
    returned_state = test_world.get_state()
    assert np.array_equal(returned_state[PATHS_INDEX], expected_returned_path_array)

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


"""
Test to make sure that if a path goes on fire, they are removed from the state space for paths. 
"""
def test_remove_path_on_fire():
    populated_areas = np.array([[1,2]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Manually set path on fire
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(test_world.state_space[PATHS_INDEX], np.zeros((num_rows, num_cols)))
    assert test_world.paths[0][1] == False


"""
Test to make sure that if multiple paths go on fire after a step, they are both removed from 
the paths state space.
"""
def test_remove_multiple_paths_on_fire():
    populated_areas = np.array([[1,2], [3,3]])
    paths = [[[1,0],[1,1]], [[3,4]]]
    paths_to_pops = {0:[[1,2]], 1:[[3,4]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Manually set paths on fire
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))
    first_path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, first_path_cell[0], first_path_cell[1]] = 1
    second_path_cell = paths[1][0]
    test_world.state_space[FIRE_INDEX, second_path_cell[0], second_path_cell[1]] = 1
    

    test_world.update_paths_and_evactuations()
    assert np.array_equal(test_world.state_space[PATHS_INDEX], np.zeros((num_rows, num_cols)))
    assert test_world.paths[0][1] == False
    assert test_world.paths[1][1] == False

"""
Test for if two paths intersect only the one on fire disappears
"""
def test_remove_path_on_fire_intersecting_paths():
    populated_areas = np.array([[1,2], [2,1]])
    paths = [[[1,0],[1,1]], [[0,1], [1,1]]]
    paths_to_pops = {0:[[1,2]], 1:[2,1]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Manually set path on fire
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    check_grid = np.zeros((num_rows,num_cols))
    check_grid[0,1] = 1
    check_grid[1,1] = 1
    assert np.array_equal(test_world.state_space[PATHS_INDEX], check_grid)

"""
Test to make sure that if a populated area was taking a path that caught on fire, it stops 
evacuating. 
"""
def test_stop_evacuating():
    populated_areas = np.array([[1,2]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Manually set popualted area to be evacuating
    populated_area = populated_areas[0]
    test_world.state_space[EVACUATING_INDEX, populated_area[0], populated_area[1]] = 1
    test_world.evacuating_paths[0] = [populated_area]

    # Set path populated area is using to evacuate on fire
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(test_world.state_space[EVACUATING_INDEX], np.zeros((num_rows, num_cols)))
    assert 0 not in test_world.evacuating_paths

"""
Test to make sure that if two areas are taking the same path, they both stop evacuating.
"""
def test_multiple_stop_evacuating():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2], [0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # turn off fires 
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Manually set popualted area to be evacuating
    first_populated_area = populated_areas[0]
    test_world.state_space[EVACUATING_INDEX, first_populated_area[0], first_populated_area[1]] = 1
    test_world.evacuating_paths[0] = [first_populated_area]
    second_populated_area = populated_areas[1]
    test_world.state_space[EVACUATING_INDEX, second_populated_area[0], second_populated_area[1]] = 1
    test_world.evacuating_paths[0].append(second_populated_area)

    # Set path populated areas are using to evacuate on fire
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(test_world.state_space[EVACUATING_INDEX], np.zeros((num_rows, num_cols)))
    assert 0 not in test_world.evacuating_paths



"""
Test to make sure that if a path is evacuating its evacuating timestamp is decremented when a step
is taken. 
"""
def test_evacuation_decrement():
    populated_areas = np.array([[1,2]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # turn off fires 
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # set populated area evacuation timstamp
    pop_area = populated_areas[0]
    test_world.evacuating_timestamps[pop_area[0], pop_area[1]] = 10
    test_world.evacuating_paths[0] = [pop_area]

    test_world.update_paths_and_evactuations()

    assert test_world.evacuating_timestamps[pop_area[0], pop_area[1]] == 9

"""
Test to make sure if two areas are evacuating on the same path, they both have their 
timestamps decremented when a step is taken.
"""
def test_multiple_evacuation_decrement():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2], [0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # turn off fires 
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # set populated areas evacuation timstamp
    first_pop_area = populated_areas[0]
    test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] = 10
    test_world.evacuating_paths[0] = [first_pop_area]
    second_pop_area = populated_areas[1]
    test_world.evacuating_timestamps[second_pop_area[0], second_pop_area[1]] = 10
    test_world.evacuating_paths[0].append(second_pop_area)

    test_world.update_paths_and_evactuations()

    assert test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] == 9
    assert test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] == 9

"""
Test to make sure that if a populated area finishes evacuating it is removed from the evacuating 
populated areas state. 
"""
def test_finished_evacuating():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]]]
    paths_to_pops = {0:[[1,2], [0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # turn off fires 
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # set populated areas evacuation timstamp
    pop_area = list(populated_areas[0])
    test_world.evacuating_timestamps[pop_area[0], pop_area[1]] = 1
    test_world.evacuating_paths[0] = [pop_area]

    # set populated area to be evacuating
    test_world.state_space[EVACUATING_INDEX, pop_area[0], pop_area[1]] = 1

    test_world.update_paths_and_evactuations()

    assert test_world.state_space[EVACUATING_INDEX, pop_area[0], pop_area[1]] == 0
    assert test_world.state_space[POPULATED_INDEX, pop_area[0], pop_area[1]] == 0
    assert 0 not in test_world.evacuating_paths
    assert test_world.evacuating_timestamps[pop_area[0], pop_area[1]] == np.inf

"""
Test to make sure self.actions is set up correctly.
"""
def test_set_actions():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)
    
    assert len(test_world.actions) == 4 #4 because action to do nothing adds 1

"""
Test to make sure that if an action that doesn't exist is given, nothing happens
"""
def test_bad_action():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    old_state_space = np.copy(test_world.state_space)
    test_world.set_action(4)
    assert(np.equal(test_world.state_space, old_state_space).all())

"""
Test to make sure that if the "do nothing" action is given, nothing happens
"""
def test_do_nothing_action():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    old_state_space = np.copy(test_world.state_space)
    test_world.set_action(3)
    assert(np.equal(test_world.state_space, old_state_space).all())

"""
Test to make sure that if the chosen path has burned down, nothing happens.
"""
def test_burned_down_path():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Set path on fire
    test_world.state_space[FIRE_INDEX, 1, 1] = 1
    test_world.advance_to_next_timestep()

    old_evacuating_paths = np.copy(test_world.evacuating_paths)
    old_state_space = np.copy(test_world.state_space)
    old_evacuating_timestamps = np.copy(test_world.evacuating_timestamps)

    # Set action to take path on fire
    test_world.set_action(0)

    assert(np.equal(old_evacuating_paths, test_world.evacuating_paths).all())
    assert(np.equal(old_state_space, test_world.state_space).all())
    assert(np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all())

"""
Test to make sure that if the chosen population center has burned down, nothing happens.
"""
def test_burned_down_pop():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Set populated area on fire
    test_world.state_space[FIRE_INDEX, 1, 2] = 1
    test_world.advance_to_next_timestep()

    old_evacuating_paths = np.copy(test_world.evacuating_paths)
    old_state_space = np.copy(test_world.state_space)
    old_evacuating_timestamps = np.copy(test_world.evacuating_timestamps)

    # Set action for populated cell on fire
    test_world.set_action(0)

    assert(np.equal(old_evacuating_paths, test_world.evacuating_paths).all())
    assert(np.equal(old_state_space, test_world.state_space).all())
    assert(np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all())


"""
Test to make sure that if populated cell is already evacuating, nothing happens when it is told to evacuate again
"""
def test_already_evacuating():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.evacuating_timestamps[1, 2] = 9 # intentially make this lower than default to see if it's reset
    test_world.state_space[EVACUATING_INDEX, 1, 2] = 1
    test_world.evacuating_paths[0] = [[1,2]]

    old_evacuating_paths = np.copy(test_world.evacuating_paths)
    old_state_space = np.copy(test_world.state_space)
    old_evacuating_timestamps = np.copy(test_world.evacuating_timestamps)

    test_world.set_action(0)

    assert(np.equal(old_evacuating_paths, test_world.evacuating_paths).all())
    assert(np.equal(old_state_space, test_world.state_space).all())
    assert(np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all())


"""
Test to make sure that taking an action for the first time for a populated cell works
"""
def test_pop_taking_first_action():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.set_action(1)

    assert(test_world.evacuating_paths[0] == [[0,1]])
    assert(test_world.state_space[EVACUATING_INDEX, 0, 1] == 1)
    assert(test_world.evacuating_timestamps[0,1] == 10)

"""
Test to make sure that taking an action for the first time for a populated cell works
"""
def test_pop_taking_first_action():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.set_action(1)

    assert(test_world.evacuating_paths[0] == [[0,1]])
    assert(test_world.state_space[EVACUATING_INDEX, 0, 1] == 1)
    assert(test_world.evacuating_timestamps[0,1] == 10)

"""
Test to make sure that taking an action works for one populated area if another populated area is already taking the same path.
"""
def test_multiple_pop_cells_same_path():
    populated_areas = np.array([[1,2], [0,1]])
    paths = [[[1,0],[1,1]],[[0,0]]]
    paths_to_pops = {0:[[1,2], [0,1]], 1:[[0,1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.set_action(0)
    test_world.set_action(1)

    assert(test_world.evacuating_paths[0] == [[1,2], [0,1]])
    assert(test_world.state_space[EVACUATING_INDEX, 0, 1] == 1)
    assert(test_world.evacuating_timestamps[0,1] == 10)
    assert(test_world.state_space[EVACUATING_INDEX, 1, 2] == 1)
    assert(test_world.evacuating_timestamps[1,2] == 10)