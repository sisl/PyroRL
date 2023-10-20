"""
OpenAI Gym Environment Wrapper Class
"""
from environment.environment import *
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame

# Grid Constants
WIDTH, HEIGHT = 475, 475
GRID_SIZE = 10
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Color Constants
FIRE_COLOR = pygame.Color("#ef476f")
POPULATED_COLOR = pygame.Color("#073b4c")
EVACUATING_COLOR = pygame.Color("#118ab2")
PATH_COLOR = pygame.Color("#ffd166")
GRASS_COLOR = pygame.Color("#06d6a0")

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
        (_, rows, cols) = state_space.shape

        # Set up pygame and font
        pygame.init()
        font = pygame.font.Font(None, 25)

        # Set screen details
        screen = pygame.display.set_mode([600, 725])
        screen.fill((255, 255, 255))
        pygame.display.set_caption("Wildfire Evacuation RL Gym Environment")

        # Running the loop!
        running = True
        while running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            """
            Title
            """
            timestep = self.fire_env.get_timestep()
            text = font.render("Timestep #: " + str(timestep), True, (0, 0, 0))
            screen.blit(text, (50, 25))

            """
            Footer
            """

            # Grass component
            text = font.render("Grass", True, (0, 0, 0))
            screen.blit(text, (115, 587))
            pygame.draw.rect(screen, GRASS_COLOR, (50, 575, 50, 50))

            # Fire component
            text = font.render("Fire", True, (0, 0, 0))
            screen.blit(text, (115, 672))
            pygame.draw.rect(screen, FIRE_COLOR, (50, 650, 50, 50))

            # Populated component
            text = font.render("Populated", True, (0, 0, 0))
            screen.blit(text, (290, 587))
            pygame.draw.rect(screen, POPULATED_COLOR, (225, 575, 50, 50))

            # Evacuating component
            text = font.render("Evacuating", True, (0, 0, 0))
            screen.blit(text, (290, 672))
            pygame.draw.rect(screen, EVACUATING_COLOR, (225, 650, 50, 50))

            # Path component
            text = font.render("Path", True, (0, 0, 0))
            screen.blit(text, (465, 587))
            pygame.draw.rect(screen, PATH_COLOR, (400, 575, 50, 50))

            # Iterate through all of the squares
            # Note: try to vectorize?
            for x in range(rows):
                for y in range(cols):

                    # Set color of the square
                    color = GRASS_COLOR
                    if (state_space[0][x][y] == 1):
                        color = FIRE_COLOR
                    if (state_space[2][x][y] == 1):
                        color = POPULATED_COLOR
                    if (state_space[3][x][y] > 0):
                        color = EVACUATING_COLOR
                    if (state_space[4][x][y] > 0):
                        color = PATH_COLOR

                    # Draw the square
                    # Note: make these constants somehow
                    square_rect = pygame.Rect(50 + x * (GRID_WIDTH + 2), 50 + y * (GRID_HEIGHT + 2), GRID_WIDTH, GRID_HEIGHT)
                    pygame.draw.rect(screen, color, square_rect)

            # Render and then quit outside
            pygame.display.flip()
        pygame.quit()

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
        env.render()
        print(reward)
