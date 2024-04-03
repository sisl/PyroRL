"""
Example of how to use the wildfire evacuation RL environment.
"""

import gymnasium
import numpy as np
import pyrorl
import shutil
from pyrorl.envs.map_helpers.create_map_info import *


if __name__ == "__main__":
    """
    Run basic environment.
    """
    # Set up parameters
    num_rows, num_cols = 20, 20
    num_populated_areas = 5

    # example of generating map (other parameters are set to their default values)
    populated_areas, paths, paths_to_pops = generate_map_info(num_rows, num_cols, num_populated_areas, save_map = True, steps_lower_bound = 2, steps_upper_bound = 4, percent_go_straight = 50, num_paths_mean = 3, num_paths_stdev = 1)

    # showing how to load in map just created for good measure, would otherwise provide the 
    # desired map pth to load_map_info
    map_info_root = os.path.join(os.getcwd(), MAP_DIRECTORY)
    current_map_directory = max(os.listdir(map_info_root), key=lambda f: os.path.getctime(os.path.join(map_info_root, f)))
    map_info_path = os.path.join(map_info_root, current_map_directory)
    num_rows, num_cols, populated_areas, paths, paths_to_pops, num_populated_areas = load_map_info(map_info_path)

    # destroy the saved map info created for this example
    shutil.rmtree(map_info_path)
    if len(os.listdir(map_info_root)) == 0:
        shutil.rmtree(map_info_root)

    # Create environment
    kwargs = {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "populated_areas": populated_areas,
        "paths": paths,
        "paths_to_pops": paths_to_pops,
    }
    env = gymnasium.make("pyrorl/PyroRL-v0", **kwargs)

    # Run a simple loop of the environment
    env.reset()
    for _ in range(10):

        # Take action and observation
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)

        # Render environment and print reward
        env.render()
        print("Reward: " + str(reward))

    # Generate the gif
    env.generate_gif()