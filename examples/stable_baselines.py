"""
An example of how to use our environment with Stable Baselines 3

To run, make sure to install Stable Baselines 3:
pip install stable-baselines3
"""

import gymnasium
import numpy as np
from stable_baselines3 import DQN
import pyrorl

if __name__ == "__main__":
    """
    Run basic environment.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
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

    # Create environment
    kwargs = {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "populated_areas": populated_areas,
        "paths": paths,
        "paths_to_pops": paths_to_pops,
    }
    env = gymnasium.make("pyrorl/PyroRL-v0", **kwargs)

    # Train a model and delete
    model = DQN("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=1000, log_interval=4)
    model.save("sample_baseline")
    del model

    # Load and reset the environment
    model = DQN.load("sample_baseline")
    obs, info = env.reset()

    # Run a simple loop of the environment
    for _ in range(10):
        action, _states = model.predict(obs, deterministic=True)
        observation, reward, terminated, truncated, info = env.step(int(action))

        # Render environment and print reward
        env.render()
        print("Reward: " + str(reward))
