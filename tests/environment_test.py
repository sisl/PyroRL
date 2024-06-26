"""
Unit tests for each of the functions in environment.py
"""

import numpy as np
from pyrorl.envs.environment.environment import (
    FireWorld,
    FIRE_INDEX,
    POPULATED_INDEX,
    EVACUATING_INDEX,
    PATHS_INDEX,
)
import pytest
import random


def dummy_environment():
    """
    Set up environment for the grid world.
    """
    # Define hardcoded paramaters of the gridworld -- populated areas, paths,
    # and which areas can use whicn paths.
    populated_areas = np.array([[1, 2], [4, 8], [6, 4], [8, 7]])
    paths = np.array(
        [
            [[1, 0], [1, 1]],
            [[2, 2], [3, 2], [4, 2], [4, 1], [4, 0]],
            [[2, 9], [2, 8], [3, 8]],
            [[5, 8], [6, 8], [6, 9]],
            [[7, 7], [6, 7], [6, 8], [6, 9]],
            [[8, 6], [8, 5], [9, 5]],
            [[8, 5], [9, 5], [7, 5], [7, 4]],
        ],
        dtype=object,
    )
    paths_to_pops = {
        0: [[1, 2]],
        1: [[1, 2]],
        2: [[4, 8]],
        3: [[4, 8]],
        4: [[8, 7]],
        5: [[8, 7]],
        6: [[6, 4]],
    }

    # Initialize fire world
    test_world = FireWorld(10, 10, populated_areas, paths, paths_to_pops)
    return test_world


def test_initialization():
    """
    Test to make sure that initializing the environment goes smoothly.
    """
    populated_areas = np.array([[2, 2], [4, 1]])
    paths = np.array([[[2, 0], [2, 1]], [[1, 0], [1, 1], [2, 1], [3, 1]]], dtype=object)
    paths_to_pops = {0: [2, 2], 1: [4, 1]}
    custom_fire_locations = np.array([[1, 2], [2, 3]])

    # Initialize environment and test each dimension of the tensor
    test_world = FireWorld(
        5,
        5,
        populated_areas,
        paths,
        paths_to_pops,
        custom_fire_locations=custom_fire_locations,
    )
    expected_population_array = np.array(
        [
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
        ]
    )
    assert np.array_equal(
        test_world.state_space[POPULATED_INDEX], expected_population_array
    )

    expected_path_array = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 2, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    assert np.array_equal(test_world.state_space[PATHS_INDEX], expected_path_array)

    expected_returned_path_array = np.array(
        [
            [0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 1, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0],
        ]
    )
    returned_state = test_world.get_state()
    assert np.array_equal(returned_state[PATHS_INDEX], expected_returned_path_array)

    fire_rows = custom_fire_locations[:, 0]
    fire_cols = custom_fire_locations[:, 1]
    comparison_array = returned_state[FIRE_INDEX, fire_rows, fire_cols] == 1
    assert comparison_array.all()


def test_setup():
    """
    Set up grid world and initiate loop of action-taking + updating.
    """
    test_world = dummy_environment()
    for _ in range(25):
        # Take a random action
        all_actions = test_world.get_actions()
        action = random.randint(0, len(all_actions) - 1)

        test_world.set_action(all_actions[action])

        # Advance the gridworld and get the reward
        test_world.advance_to_next_timestep()
        reward = test_world.get_state_utility()


def test_negative_parameters():
    """
    Test that negative parameters bring up ValueErrors
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [1, 1]]], dtype=object)
    paths_to_pops = {0: [[1, 2]]}
    num_rows = -5
    num_cols = 5

    # Initialize fire world and assert error
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with negative columns instead
    num_rows, num_cols = 5, -5
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with negative number of fire cells instead
    num_cols, num_fire_cells = 5, -5
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            num_fire_cells=num_fire_cells,
        )


def test_missing_wind_parameters():
    """
    Test the behavior when one of the wind parameters is defined and the other isn't
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = [[[1, 0], [1, 1]], [[0, 0]]]
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world with wind speed but no wind angle
    with pytest.raises(TypeError):
        test_wind_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            wind_angle=None,
            wind_speed=20,
        )

    # Initialize fire world with wind angle but no wind speed
    with pytest.raises(TypeError):
        test_wind_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            wind_angle=np.pi,
            wind_speed=None,
        )


def test_invalid_populated_areas():
    """
    Test that invalid populuated areas are not allowed
    """
    populated_areas = np.array([[-1, 2]])
    paths = np.array([[[1, 0], [1, 1]]], dtype=object)
    paths_to_pops = {0: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world and assert error
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with negative column instead
    populated_areas = np.array([[1, -2]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with out of bounds x coordinate
    populated_areas = np.array([[7, 2]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with out of bounds y coordinate
    populated_areas = np.array([[3, 8]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )


def test_invalid_paths():
    """
    Test that invalid paths throw an error
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [-1, 1]]], dtype=object)
    paths_to_pops = {0: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world and assert error
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with negative column instead
    paths = np.array([[[1, 1]], [[1, -2]]], dtype=object)
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with out of bounds x coordinate
    paths = np.array([[[1, 1]], [[20, 3], [1, 2]]], dtype=object)
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with out of bounds y coordinate
    paths = np.array([[[1, 1], [1, 0], [0, 0]], [[4, 4], [4, 5]]], dtype=object)
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )


def test_invalid_paths_to_pops():
    """
    Test invalid mappings from paths to populated areas
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [1, 1]]], dtype=object)
    paths_to_pops = {-1: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world and assert error
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with path index that is greater than total number allowed
    paths_to_pops = {2: [[1, 2]]}
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )

    # Try with populated area that doesn't exist
    paths_to_pops = {0: [[1, 2], [2, 3]]}
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )


def test_invalid_fire_locations():
    """
    Test that invalid fire locations are removed
    """
    populated_areas = np.array([[2, 2], [4, 1]])
    paths = np.array([[[2, 0], [2, 1]], [[1, 0], [1, 1], [2, 1], [3, 1]]], dtype=object)
    paths_to_pops = {0: [2, 2], 1: [4, 1]}
    custom_fire_locations = np.array([[1, 2], [2, -1]])
    num_rows = 5
    num_cols = 5

    # Initialize fire world and assert error
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            custom_fire_locations=custom_fire_locations,
        )

    # Try with negative column instead
    custom_fire_locations = np.array([[1, -2]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            custom_fire_locations=custom_fire_locations,
        )

    # Try with out of bounds x coordinate
    custom_fire_locations = np.array([[7, 2]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            custom_fire_locations=custom_fire_locations,
        )

    # Try with out of bounds y coordinate
    custom_fire_locations = np.array([[3, 8]])
    with pytest.raises(ValueError):
        test_world = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            custom_fire_locations=custom_fire_locations,
        )


def test_remove_path_on_fire():
    """
    Test to make sure that if a path goes on fire,
    they are removed from the state space for paths.
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Manually set path on fire
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(
        test_world.state_space[PATHS_INDEX], np.zeros((num_rows, num_cols))
    )
    assert test_world.paths[0][1] == False


def test_remove_multiple_paths_on_fire():
    """
    Test to make sure that if multiple paths go on fire after a step, they are both removed from
    the paths state space.
    """
    populated_areas = np.array([[1, 2], [3, 3]])
    paths = np.array([[[1, 0], [1, 1]], [[3, 4]]], dtype=object)
    paths_to_pops = {0: [[1, 2]], 1: [[3, 3]]}
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
    assert np.array_equal(
        test_world.state_space[PATHS_INDEX], np.zeros((num_rows, num_cols))
    )
    assert test_world.paths[0][1] == False
    assert test_world.paths[1][1] == False


def test_remove_path_on_fire_intersecting_paths():
    """
    Test for if two paths intersect only the one on fire disappears
    """
    populated_areas = np.array([[1, 2], [2, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 1], [1, 1]]])
    paths_to_pops = {0: [[1, 2]], 1: [2, 1]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Manually set path on fire
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    check_grid = np.zeros((num_rows, num_cols))
    check_grid[0, 1] = 1
    check_grid[1, 1] = 1
    assert np.array_equal(test_world.state_space[PATHS_INDEX], check_grid)


def test_stop_evacuating():
    """
    Test to make sure that if a populated area was taking a path that caught on fire, it stops
    evacuating.
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Manually set popualted area to be evacuating
    populated_area = populated_areas[0]
    test_world.state_space[EVACUATING_INDEX, populated_area[0], populated_area[1]] = 1
    test_world.evacuating_paths[0] = [populated_area]

    # Set path populated area is using to evacuate on fire
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(
        test_world.state_space[EVACUATING_INDEX], np.zeros((num_rows, num_cols))
    )
    assert 0 not in test_world.evacuating_paths


def test_multiple_stop_evacuating():
    """
    Test to make sure that if two areas are taking the same path, they both stop evacuating.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2], [0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Manually set popualted area to be evacuating
    first_populated_area = populated_areas[0]
    test_world.state_space[
        EVACUATING_INDEX, first_populated_area[0], first_populated_area[1]
    ] = 1
    test_world.evacuating_paths[0] = [first_populated_area]
    second_populated_area = populated_areas[1]
    test_world.state_space[
        EVACUATING_INDEX, second_populated_area[0], second_populated_area[1]
    ] = 1
    test_world.evacuating_paths[0].append(second_populated_area)

    # Set path populated areas are using to evacuate on fire
    path_cell = paths[0][0]
    test_world.state_space[FIRE_INDEX, path_cell[0], path_cell[1]] = 1

    test_world.update_paths_and_evactuations()
    assert np.array_equal(
        test_world.state_space[EVACUATING_INDEX], np.zeros((num_rows, num_cols))
    )
    assert 0 not in test_world.evacuating_paths


def test_evacuation_decrement():
    """
    Test to make sure that if a path is evacuating its evacuating timestamp is decremented when a step
    is taken.
    """
    populated_areas = np.array([[1, 2]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Set populated area evacuation timstamp
    pop_area = populated_areas[0]
    test_world.evacuating_timestamps[pop_area[0], pop_area[1]] = 10
    test_world.evacuating_paths[0] = [pop_area]

    test_world.update_paths_and_evactuations()

    assert test_world.evacuating_timestamps[pop_area[0], pop_area[1]] == 9


def test_multiple_evacuation_decrement():
    """
    Test to make sure if two areas are evacuating on the same path, they both have their
    timestamps decremented when a step is taken.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2], [0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Set populated areas evacuation timstamp
    first_pop_area = populated_areas[0]
    test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] = 10
    test_world.evacuating_paths[0] = [first_pop_area]
    second_pop_area = populated_areas[1]
    test_world.evacuating_timestamps[second_pop_area[0], second_pop_area[1]] = 10
    test_world.evacuating_paths[0].append(second_pop_area)

    test_world.update_paths_and_evactuations()

    assert test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] == 9
    assert test_world.evacuating_timestamps[first_pop_area[0], first_pop_area[1]] == 9


def test_finished_evacuating():
    """
    Test to make sure that if a populated area finishes evacuating it is removed from the evacuating
    populated areas state and is added to finished evacuating cells.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]]])
    paths_to_pops = {0: [[1, 2], [0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    # Turn off fires
    test_world.state_space[FIRE_INDEX] = np.zeros((num_rows, num_cols))

    # Set populated areas evacuation timstamp
    pop_area = list(populated_areas[0])
    test_world.evacuating_timestamps[pop_area[0], pop_area[1]] = 1
    test_world.evacuating_paths[0] = [pop_area]

    # Set populated area to be evacuating
    test_world.state_space[EVACUATING_INDEX, pop_area[0], pop_area[1]] = 1

    test_world.update_paths_and_evactuations()

    assert test_world.state_space[EVACUATING_INDEX, pop_area[0], pop_area[1]] == 0
    assert test_world.state_space[POPULATED_INDEX, pop_area[0], pop_area[1]] == 0
    assert 0 not in test_world.evacuating_paths
    assert test_world.evacuating_timestamps[pop_area[0], pop_area[1]] == np.inf
    assert len(test_world.finished_evacuating_cells) == 1


def test_set_actions():
    """
    Test to make sure self.actions is set up correctly.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    assert len(test_world.actions) == 4  # 4 because action to do nothing adds 1


def test_bad_action():
    """
    Test to make sure that if an action that doesn't exist is given, nothing happens
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    old_state_space = np.copy(test_world.state_space)
    test_world.set_action(4)
    assert np.equal(test_world.state_space, old_state_space).all()


def test_do_nothing_action():
    """
    Test to make sure that if the "do nothing" action is given, nothing happens
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    old_state_space = np.copy(test_world.state_space)
    test_world.set_action(3)
    assert np.equal(test_world.state_space, old_state_space).all()


def test_burned_down_path():
    """
    Test to make sure that if the chosen path has burned down, nothing happens.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
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

    assert np.equal(old_evacuating_paths, test_world.evacuating_paths).all()
    assert np.equal(old_state_space, test_world.state_space).all()
    assert np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all()


def test_burned_down_pop():
    """
    Test to make sure that if the chosen population center has burned down, nothing happens.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
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

    assert np.equal(old_evacuating_paths, test_world.evacuating_paths).all()
    assert np.equal(old_state_space, test_world.state_space).all()
    assert np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all()


def test_already_evacuating():
    """
    Test to make sure that if populated cell is already evacuating, nothing happens when it is told to evacuate again
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.evacuating_timestamps[1, 2] = (
        9  # Intentially make this lower than default to see if it's reset
    )
    test_world.state_space[EVACUATING_INDEX, 1, 2] = 1
    test_world.evacuating_paths[0] = [[1, 2]]

    old_evacuating_paths = np.copy(test_world.evacuating_paths)
    old_state_space = np.copy(test_world.state_space)
    old_evacuating_timestamps = np.copy(test_world.evacuating_timestamps)

    test_world.set_action(0)

    assert np.equal(old_evacuating_paths, test_world.evacuating_paths).all()
    assert np.equal(old_state_space, test_world.state_space).all()
    assert np.equal(old_evacuating_timestamps, test_world.evacuating_timestamps).all()


def test_pop_taking_first_action():
    """
    Test to make sure that taking an action for the first time for a populated cell works
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.set_action(1)

    assert test_world.evacuating_paths[0] == [[0, 1]]
    assert test_world.state_space[EVACUATING_INDEX, 0, 1] == 1
    assert test_world.evacuating_timestamps[0, 1] == 10


def test_multiple_pop_cells_same_path():
    """
    Test to make sure that taking an action works for one populated area
    if another populated area is already taking the same path.
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = np.array([[[1, 0], [1, 1]], [[0, 0]]], dtype=object)
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

    test_world.set_action(0)
    test_world.set_action(1)

    assert test_world.evacuating_paths[0] == [[1, 2], [0, 1]]
    assert test_world.state_space[EVACUATING_INDEX, 0, 1] == 1
    assert test_world.evacuating_timestamps[0, 1] == 10
    assert test_world.state_space[EVACUATING_INDEX, 1, 2] == 1
    assert test_world.evacuating_timestamps[1, 2] == 10


def test_wind_bias():
    """
    Test that relative value of the fire mask changes when adding wind or no wind
    """
    populated_areas = np.array([[1, 2], [0, 1]])
    paths = [[[1, 0], [1, 1]], [[0, 0]]]
    paths_to_pops = {0: [[1, 2], [0, 1]], 1: [[0, 1]]}
    num_rows = 5
    num_cols = 5

    # Initialize fire world
    test_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)
    test_wind_world = FireWorld(
        num_rows,
        num_cols,
        populated_areas,
        paths,
        paths_to_pops,
        wind_angle=np.pi,
        wind_speed=20,
    )

    # Calculate the wind and no wind fire masks
    windless_mask = test_world.fire_mask.reshape((5, 5))
    wind_mask = test_wind_world.fire_mask.reshape((5, 5))

    # Check difference between wind and no wind bias
    assert (windless_mask[:, 0] < wind_mask[:, 0]).all().item()
    assert (windless_mask[:, 4] > wind_mask[:, 4]).all().item()
    assert (windless_mask[:, 2] == wind_mask[:, 2]).all().item()
