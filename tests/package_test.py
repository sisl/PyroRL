"""
Testing the OpenAI Gym Package itself.
"""
import gymnasium
import numpy as np
import pygame
import pytest 
import pyrorl

def PGEvent():
    def __init__(self):
        self.type = pygame.QUIT

def test_constructor():
    """
    Test the constructor to make sure all variables are accounted for.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Create environment
    kwargs = {
        'num_rows': num_rows,
        'num_cols': num_cols,
        'populated_areas': populated_areas,
        'paths': paths,
        'paths_to_pops': paths_to_pops
    }
    env = gymnasium.make('pyrorl/PyroRL-v0', **kwargs)
    
    # Make basic checks for the constructor
    assert(env.num_rows == num_rows)
    assert(env.num_cols == num_cols)
    np.testing.assert_array_equal(env.populated_areas, populated_areas)
    np.testing.assert_array_equal(env.paths, paths)

    # Special check for paths to populated areas
    for key in paths_to_pops:
        np.testing.assert_array_equal(np.array(env.paths_to_pops[key]), np.array(paths_to_pops[key]))

def test_reset():
    """
    Testing if the initial state of the environment is reset.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Create environment
    kwargs = {
        'num_rows': num_rows,
        'num_cols': num_cols,
        'populated_areas': populated_areas,
        'paths': paths,
        'paths_to_pops': paths_to_pops
    }
    env = gymnasium.make('pyrorl/PyroRL-v0', **kwargs)

    # Run a simple loop of the environment
    env.reset()
    for _ in range(10):

        # Take action and observation
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
    
    # Check that reset makes it all the same
    env.reset()
    assert(env.num_rows == num_rows)
    assert(env.num_cols == num_cols)
    np.testing.assert_array_equal(env.populated_areas, populated_areas)
    np.testing.assert_array_equal(env.paths, paths)

    # Special check for paths to populated areas
    for key in paths_to_pops:
        np.testing.assert_array_equal(np.array(env.paths_to_pops[key]), np.array(paths_to_pops[key]))

def test_reset(mocker):
    """
    Test that basic rendering is working through mocking.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Create environment
    kwargs = {
        'num_rows': num_rows,
        'num_cols': num_cols,
        'populated_areas': populated_areas,
        'paths': paths,
        'paths_to_pops': paths_to_pops
    }
    env = gymnasium.make('pyrorl/PyroRL-v0', **kwargs)

    # Render and make simple test check
    env.reset()
    display_mock = mocker.patch('pygame.display')
    draw_mock = mocker.patch('pygame.draw')
    image_mock = mocker.patch('pygame.image')
    event_mock = mocker.patch('pygame.event.get')
    event_mock.return_value = [pygame.event.Event(pygame.QUIT)]
    env.render()
    #pygame.quit()
    pygame.display.set_mode.assert_called_once_with([600, 725])

    
