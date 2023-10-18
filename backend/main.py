"""
OpenAI Gym Environment Wrapper Class
"""
from environment.environment import *
import gymnasium as gym
from gymnasium import spaces
import numpy as np

class WildfireEvacuationEnv(gym.Env):
    def __init__(self, num_rows, num_cols, populated_areas, paths, paths_to_pops):
        """
        Set up the basic environment and its parameters.
        """
        # Set up wildfire environment (and save extra copy)
        self.fire_env = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)
        self.saved_fire_env = self.fire_env

        # Set up action space
        actions = self.fire_env.get_actions()
        self.action_space = spaces.Discrete(len(actions))

        # Set up observation space
        observations = self.fire_env.get_state()
        self.observation_space = spaces.Box(low=0, high=200, shape = observations.shape, dtype=np.float64)

    def reset(self):
        """
        Reset the environment to its initial state.
        """
        self.fire_env = self.saved_fire_env
        state_space = self.fire_env.get_state()
        return state_space, { "" : "" }

    def step(self, action):
        """
        Take a step and advance the environment after taking an action.
        """
        # Take the action and advance to the next timestep
        self.fire_env.set_action(action)
        self.fire_env.advance_to_next_timestep()

        # Gather observations and rewards
        observations = self.fire_env.get_state()
        rewards = self.fire_env.get_state_utility()
        terminated = self.fire_env.get_terminated()
        return observations, rewards, terminated, False, { "" : "" }

    def render(self):
        """
        Render the environment (to-do)
        """
        state_space = self.fire_env.get_state()
        print(state_space)

if __name__ == "__main__":
    """
    Run basic environment.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Create the environment and test loop
    env = WildfireEvacuationEnv(num_rows, num_cols, populated_areas, paths, paths_to_pops)
    for _ in range(10):
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        print(reward)
