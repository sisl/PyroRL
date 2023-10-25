"""
OpenAI Gym Environment Wrapper Class
"""
from wildfire_evac.envs.environment.environment import *
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame

# Constants for visualization
WIDTH, HEIGHT = 475, 475
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
        # Save parameters and set up environment
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.populated_areas = populated_areas
        self.paths = paths
        self.paths_to_pops = paths_to_pops
        self.fire_env = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

        # Set up action space
        actions = self.fire_env.get_actions()
        self.action_space = spaces.Discrete(len(actions))

        # Set up observation space
        observations = self.fire_env.get_state()
        self.observation_space = spaces.Box(low=0, high=200, shape = observations.shape, dtype=np.float64)

        # Set up grid constants
        self.grid_width = WIDTH // num_rows
        self.grid_height = HEIGHT // num_cols

    def reset(self, seed = None, options = None):
        """
        Reset the environment to its initial state.
        """
        self.fire_env = FireWorld(self.num_rows, self.num_cols, self.populated_areas, self.paths, self.paths_to_pops)
        state_space = self.fire_env.get_state()
        return state_space, { "": "" }

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

    def render_hf(self, screen, font):
        """
        Set up header and footer
        """
        # Set title of the screen
        timestep = self.fire_env.get_timestep()
        text = font.render("Timestep #: " + str(timestep), True, (0, 0, 0))
        screen.blit(text, (50, 25))

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

        return screen

    def render(self):
        """
        Render the environment (to-do)
        """
        state_space = self.fire_env.get_state()
        (_, rows, cols) = state_space.shape

        # Set up pygame and font
        pygame.init()
        screen = pygame.display.set_mode([600, 725])
        font = pygame.font.Font(None, 25)

        # Set screen details
        screen.fill((255, 255, 255))
        pygame.display.set_caption("Wildfire Evacuation RL Gym Environment")
        screen = self.render_hf(screen, font)

        # Running the loop!
        running = True
        while running:
            # Did the user click the window close button?
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

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
                    square_rect = pygame.Rect(50 + x * (self.grid_width + 2), 50 + y * (self.grid_height + 2), self.grid_width, self.grid_height)
                    pygame.draw.rect(screen, color, square_rect)

            # Render and then quit outside
            pygame.display.flip()
        pygame.quit()
