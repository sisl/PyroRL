"""
OpenAI Gym Environment Wrapper Class
"""

from pyrorl.envs.environment.environment import FireWorld
import gymnasium as gym
from gymnasium import spaces
import imageio.v2 as imageio
import numpy as np
import os
import pygame
import shutil
import sys
from typing import Optional, Any

# Constants for visualization
WIDTH, HEIGHT = 475, 475
FIRE_COLOR = pygame.Color("#ef476f")
POPULATED_COLOR = pygame.Color("#073b4c")
EVACUATING_COLOR = pygame.Color("#118ab2")
PATH_COLOR = pygame.Color("#ffd166")
GRASS_COLOR = pygame.Color("#06d6a0")
FINISHED_COLOR = pygame.Color("#BF9ACA")


class WildfireEvacuationEnv(gym.Env):
    def __init__(
        self,
        num_rows: int,
        num_cols: int,
        populated_areas: np.ndarray,
        paths: np.ndarray,
        paths_to_pops: dict,
        custom_fire_locations: Optional[np.ndarray] = None,
        wind_speed: Optional[float] = None,
        wind_angle: Optional[float] = None,
        fuel_mean:float = 8.5,
        fuel_stdev:float = 3
    ):
        """
        Set up the basic environment and its parameters.
        """
        # Save parameters and set up environment
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.populated_areas = populated_areas
        self.paths = paths
        self.paths_to_pops = paths_to_pops
        self.custom_fire_locations = custom_fire_locations
        self.wind_speed = wind_speed
        self.wind_angle = wind_angle
        self.fire_env = FireWorld(
            num_rows,
            num_cols,
            populated_areas,
            paths,
            paths_to_pops,
            custom_fire_locations=custom_fire_locations,
            wind_speed=wind_speed,
            wind_angle=wind_angle,
        )

        # Set up action space
        actions = self.fire_env.get_actions()
        self.action_space = spaces.Discrete(len(actions))

        # Set up observation space
        observations = self.fire_env.get_state()
        self.observation_space = spaces.Box(
            low=0, high=200, shape=observations.shape, dtype=np.float64
        )

        # Set up grid constants
        self.grid_width = WIDTH // num_rows
        self.grid_height = HEIGHT // num_cols

        # Create directory to store screenshots
        if os.path.exists("grid_screenshots") is False:
            os.mkdir("grid_screenshots")

    def reset(
        self, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """
        Reset the environment to its initial state.
        """
        self.fire_env = FireWorld(
            self.num_rows,
            self.num_cols,
            self.populated_areas,
            self.paths,
            self.paths_to_pops,
            wind_speed=self.wind_speed,
            wind_angle=self.wind_angle,
        )

        state_space = self.fire_env.get_state()
        return state_space, {"": ""}

    def step(self, action: int) -> tuple:
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
        return observations, rewards, terminated, False, {"": ""}

    def render_hf(
        self, screen: pygame.Surface, font: pygame.font.Font
    ) -> pygame.Surface:
        """
        Set up header and footer
        """
        # Get width and height of the screen
        surface_width = screen.get_width()
        surface_height = screen.get_height()

        # Starting locations
        x = int(surface_width * 0.35)
        y = int(surface_height * 0.8)

        # Set title of the screen
        timestep = self.fire_env.get_timestep()
        text = font.render("Timestep #: " + str(timestep), True, (0, 0, 0))
        screen.blit(text, (50, 25))

        # Grass component
        text = font.render("Grass", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, GRASS_COLOR, (x, y, 50, 50))

        # Update y
        y += 75

        # Fire component
        text = font.render("Fire", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, FIRE_COLOR, (x, y, 50, 50))

        # Update locations
        x += 175
        y -= 75

        # Populated component
        text = font.render("Populated", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, POPULATED_COLOR, (x, y, 50, 50))

        # Update y
        y += 75

        # Evacuating component
        text = font.render("Evacuating", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, EVACUATING_COLOR, (x, y, 50, 50))

        # Update locations
        x += 175
        y -= 75

        # Path component
        text = font.render("Path", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, PATH_COLOR, (x, y, 50, 50))

        # Update y location
        y += 75

        # Evacuated component
        text = font.render("Evacuated", True, (0, 0, 0))
        screen.blit(text, (x + 65, y + 20))
        pygame.draw.rect(screen, FINISHED_COLOR, (x, y, 50, 50))

        return screen

    def render(self):
        """
        Render the environment
        """
        # Set up the state space
        state_space = self.fire_env.get_state()
        finished_evacuating = self.fire_env.get_finished_evacuating()
        (_, rows, cols) = state_space.shape

        # Get dimensions of the screen
        pygame.init()
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        # Set up pygame and font
        screen = pygame.display.set_mode([screen_width, screen_height])
        self.grid_width = (0.8 * screen_width) // self.num_rows
        self.grid_height = (0.6 * screen_height) // self.num_cols
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
                    timestep = self.fire_env.get_timestep()
                    pygame.image.save(
                        screen, "grid_screenshots/" + str(timestep) + ".png"
                    )
                    running = False

            # Iterate through all of the squares
            # Note: try to vectorize?
            for x in range(rows):
                for y in range(cols):

                    # Set color of the square
                    color = GRASS_COLOR
                    if state_space[4][x][y] > 0:
                        color = PATH_COLOR
                    if state_space[0][x][y] == 1:
                        color = FIRE_COLOR
                    if state_space[2][x][y] == 1:
                        color = POPULATED_COLOR
                    if state_space[3][x][y] > 0:
                        color = EVACUATING_COLOR
                    if [x, y] in finished_evacuating:
                        color = FINISHED_COLOR

                    # Draw the square
                    self.grid_dim = min(self.grid_width, self.grid_height)
                    square_rect = pygame.Rect(
                        50 + x * (self.grid_dim + 2),
                        50 + y * (self.grid_dim + 2),
                        self.grid_dim,
                        self.grid_dim,
                        # 50 + x * (self.grid_width + 2),
                        # 50 + y * (self.grid_height + 2),
                        # self.grid_width,
                        # self.grid_height,
                    )
                    pygame.draw.rect(screen, color, square_rect)

            # Render and then quit outside
            pygame.display.flip()
        pygame.quit()

    def generate_gif(self):
        """
        Save run as a GIF.
        """
        files = [str(i) for i in range(1, self.fire_env.get_timestep() + 1)]
        images = [imageio.imread("grid_screenshots/" + f + ".png") for f in files]
        imageio.mimsave("training.gif", images)
        shutil.rmtree("grid_screenshots")
