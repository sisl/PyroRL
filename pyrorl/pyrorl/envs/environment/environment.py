"""
Environment for Wildfire Spread
"""

import numpy as np
import random
import torch
from typing import Optional, Any, Tuple, Dict, List

# For wind bias
from .environment_constant import set_fire_mask, linear_wind_transform

"""
Indices corresponding to each layer of state
"""
FIRE_INDEX = 0
FUEL_INDEX = 1
POPULATED_INDEX = 2
EVACUATING_INDEX = 3
PATHS_INDEX = 4


class FireWorld:
    """
    We represent the world as a 5 by n by m tensor:
    - n by m is the size of the grid world,
    - 5 represents each of the following:
        - [fire, fuel, populated_areas, evacuating, paths]
    """

    def __init__(
        self,
        num_rows: int,
        num_cols: int,
        populated_areas: np.ndarray,
        paths: np.ndarray,
        paths_to_pops: dict,
        num_fire_cells: int = 2,
        custom_fire_locations: Optional[np.ndarray] = None,
        wind_speed: Optional[float] = None,
        wind_angle: Optional[float] = None,
        fuel_mean:float = 8.5,
        fuel_stdev:float = 3
    ):
        """
        The constructor defines the state and action space, initializes the fires,
        and sets the paths and populated areas.
        - wind angle is in radians
        """
        # Assert that number of rows, columns, and fire cells are both positive
        if num_rows < 1:
            raise ValueError("Number of rows should be positive!")
        if num_cols < 1:
            raise ValueError("Number of rows should be positive!")
        if num_fire_cells < 1:
            raise ValueError("Number of fire cells should be positive!")

        # Check that populated areas are within the grid
        valid_populated_areas = (
            (populated_areas[:, 0] >= 0)
            & (populated_areas[:, 1] >= 0)
            & (populated_areas[:, 0] < num_rows)
            & (populated_areas[:, 1] < num_cols)
        )
        if np.any(~valid_populated_areas):
            raise ValueError("Populated areas are not valid with the grid dimensions")

        # Check that each path has squares within the grid
        valid_paths = [
            (
                (np.array(path)[:, 0] >= 0)
                & (np.array(path)[:, 1] >= 0)
                & (np.array(path)[:, 0] < num_rows)
                & (np.array(path)[:, 1] < num_cols)
            )
            for path in paths
        ]
        if np.any(~np.hstack(valid_paths)):
            raise ValueError("Pathed areas are not valid with the grid dimensions")

        # Define the state and action space
        self.reward = 0
        self.state_space = np.zeros([5, num_rows, num_cols])

        # Set up actions -- add extra action for doing nothing
        num_paths, num_actions = np.arange(len(paths)), 0
        for key in paths_to_pops:

            # First, check that path index actually exists
            if not np.isin(key, num_paths):
                raise ValueError("Key is not a valid index of a path!")

            # Then, check that each populated area exists
            areas = np.array(paths_to_pops[key])
            if np.any(~np.isin(areas, populated_areas)):
                raise ValueError("Corresponding populated area does not exist!")

            # Increment total number of actions to be taken
            for _ in range(len(paths_to_pops[key])):
                num_actions += 1
        self.actions = list(np.arange(num_actions + 1))

        # We want to remember which action index corresponds to which population center
        # and which path (because we just provide an array like [1,2,3,4,5,6,7]) which
        # would each be mapped to a given population area taking a given path
        self.action_to_pop_and_path: dict[Any, Optional[Tuple[Any, Any]]] = {
            self.actions[-1]: None
        }

        # Map each action to a populated area and path
        index = 0
        for path in paths_to_pops:
            for pop in paths_to_pops[path]:
                self.action_to_pop_and_path[index] = (pop, path)
                index += 1

        # State for the evacuation of populated areas
        self.evacuating_paths: Dict[int, list] = (
            {}
        )  # path_index : list of pop x,y indices that are evacuating [[x,y],[x,y],...]
        self.evacuating_timestamps = np.full((num_rows, num_cols), np.inf)

        # If the user specifies custom fire locations, set them
        self.num_fire_cells = num_fire_cells
        if custom_fire_locations is not None:

            # Check that populated areas are within the grid
            valid_fire_locations = (
                (custom_fire_locations[:, 0] >= 0)
                & (custom_fire_locations[:, 1] >= 0)
                & (custom_fire_locations[:, 0] < num_rows)
                & (custom_fire_locations[:, 1] < num_cols)
            )
            if np.any(~valid_fire_locations):
                raise ValueError(
                    "Populated areas are not valid with the grid dimensions"
                )

            # Only once valid, set them!
            fire_rows = custom_fire_locations[:, 0]
            fire_cols = custom_fire_locations[:, 1]
            self.state_space[FIRE_INDEX, fire_rows, fire_cols] = 1

        # Otherwise, randomly generate them
        else:
            for _ in range(self.num_fire_cells):
                self.state_space[
                    FIRE_INDEX,
                    random.randint(0, num_rows - 1),
                    random.randint(0, num_cols - 1),
                ] = 1

        # Initialize fuel levels
        # Note: make the fire spread parameters to constants?
        num_values = num_rows * num_cols
        self.state_space[FUEL_INDEX] = np.random.normal(
            fuel_mean, fuel_stdev, num_values
        ).reshape((num_rows, num_cols))

        # Initialize populated areas
        pop_rows, pop_cols = populated_areas[:, 0], populated_areas[:, 1]
        self.state_space[POPULATED_INDEX, pop_rows, pop_cols] = 1

        # Initialize self.paths
        self.paths: List[List[Any]] = []
        for path in paths:
            path_array = np.array(path)
            path_rows, path_cols = path_array[:, 0].astype(int), path_array[
                :, 1
            ].astype(int)
            self.state_space[PATHS_INDEX, path_rows, path_cols] += 1

            # Each path in self.paths is a list that records what the path is and
            # whether the path still exists (i.e. has not been destroyed by a fire)
            self.paths.append([np.zeros((num_rows, num_cols)), True])
            self.paths[-1][0][path_rows, path_cols] += 1

        # Set the timestep
        self.time_step = 0

        # set fire mask
        self.fire_mask = set_fire_mask(0.094)

        # Factor in wind speeds
        if wind_speed is not None or wind_angle is not None:
            if wind_speed is None or wind_angle is None:
                raise TypeError(
                    "When setting wind details, "
                    "wind speed and wind angle must both be provided"
                )
            self.fire_mask = linear_wind_transform(wind_speed, wind_angle)
        else:
            self.fire_mask = torch.from_numpy(self.fire_mask)

        # Record which population cells have finished evacuating
        self.finished_evacuating_cells = []

    def sample_fire_propogation(self):
        """
        Sample the next state of the wildfire model.
        """
        # Drops fuel level of enflamed cells
        self.state_space[FUEL_INDEX, self.state_space[FIRE_INDEX] == 1] -= 1
        self.state_space[FUEL_INDEX, self.state_space[FUEL_INDEX] < 0] = 0

        # Extinguishes cells that have run out of fuel
        self.state_space[FIRE_INDEX, self.state_space[FUEL_INDEX, :] <= 0] = 0

        # Runs kernel of neighborhing cells where each row
        # corresponds to the neighborhood of a cell
        torch_rep = torch.tensor(self.state_space[FIRE_INDEX]).unsqueeze(0)
        y = torch.nn.Unfold((5, 5), dilation=1, padding=2)
        z = y(torch_rep)

        # The relative importance of each neighboring cell is weighted
        z = z * self.fire_mask

        # Unenflamed cells are set to 1 to eliminate their role to the
        # fire spread equation
        z[z == 0] = 1
        z = z.prod(dim=0)
        z = 1 - z.reshape(self.state_space[FIRE_INDEX].shape)

        # From the probability of an ignition in z, new fire locations are
        # randomly generated
        prob_mask = torch.rand_like(z)
        new_fire = (z > prob_mask).float()

        # These new fire locations are added to the state
        self.state_space[FIRE_INDEX] = np.maximum(
            np.array(new_fire), self.state_space[FIRE_INDEX]
        )

    def update_paths_and_evactuations(self):
        """
        Performs three functions:
        1. Remove paths that been burned down by a fire
        2. Also stops evacuating any areas that were taking a burned down path
        3. Also decrements the evacuation timestamps
        """
        for i in range(len(self.paths)):
            # Decrement path counts and remove path if path is on fire
            if (
                self.paths[i][1]
                and np.sum(
                    np.logical_and(self.state_space[FIRE_INDEX], self.paths[i][0])
                )
                > 0
            ):
                self.state_space[PATHS_INDEX] -= self.paths[i][0]
                self.paths[i][1] = False

                # Stop evacuating an area if it was taking the removed path
                if i in self.evacuating_paths:
                    pop_centers = np.array(self.evacuating_paths[i])
                    pop_rows, pop_cols = pop_centers[:, 0], pop_centers[:, 1]

                    # Reset timestamp and evacuation index for populated areas
                    self.evacuating_timestamps[pop_rows, pop_cols] = np.inf
                    self.state_space[EVACUATING_INDEX, pop_rows, pop_cols] = 0
                    del self.evacuating_paths[i]

            # We need to decrement the evacuating paths timestamp
            elif i in self.evacuating_paths:

                # For the below, this code works for if multiple population centers
                # are taking the same path and finish at the same time, but if we have
                # it so that two population centers can't take the same
                # path it could probably be simplified
                pop_centers = np.array(self.evacuating_paths[i])
                pop_rows, pop_cols = pop_centers[:, 0], pop_centers[:, 1]
                self.evacuating_timestamps[pop_rows, pop_cols] -= 1
                done_evacuating = np.where(self.evacuating_timestamps == 0)

                self.state_space[
                    EVACUATING_INDEX, done_evacuating[0], done_evacuating[1]
                ] = 0
                self.state_space[
                    POPULATED_INDEX, done_evacuating[0], done_evacuating[1]
                ] = 0

                # Note that right now it is going to be vastly often the case that two
                # population cases don't finish evacuating along the same path at the
                # same time right now, so this is an extremely rare edge case, meaning
                # that most often this for loop will run for a single iteration
                done_evacuating = np.array([done_evacuating[0], done_evacuating[1]])
                done_evacuating = np.transpose(done_evacuating)
                for j in range(done_evacuating.shape[0]):
                    self.evacuating_paths[i].remove(list(done_evacuating[j]))

                    # This population center is done evacuating, so we can set its
                    # timestamp back to infinity (so we don't try to remove this
                    # from self.evacuating paths twice - was causing a bug)
                    update_row, update_col = (
                        done_evacuating[j, 0],
                        done_evacuating[j, 1],
                    )
                    self.evacuating_timestamps[update_row, update_col] = np.inf
                    self.finished_evacuating_cells.append([update_row, update_col])

                # No more population centers are using this path, so we delete it
                if len(self.evacuating_paths[i]) == 0:
                    del self.evacuating_paths[i]

    def accumulate_reward(self):
        """
        Mark enflamed areas as no longer populated or evacuating and calculate reward.
        """
        # Get which populated_areas areas are on fire and evacuating
        populated_areas = np.where(self.state_space[POPULATED_INDEX] == 1)
        fire = self.state_space[FIRE_INDEX][populated_areas]
        evacuating = self.state_space[EVACUATING_INDEX][populated_areas]

        # Mark enflamed areas as no longer populated or evacuating
        enflamed_populated_areas = np.where(fire == 1)[0]
        enflamed_rows = populated_areas[0][enflamed_populated_areas]
        enflamed_cols = populated_areas[1][enflamed_populated_areas]

        # Depopulate enflamed areas and remove evacuations
        self.state_space[POPULATED_INDEX, enflamed_rows, enflamed_cols] = 0
        self.state_space[EVACUATING_INDEX, enflamed_rows, enflamed_cols] = 0

        # Update reward
        self.reward -= 100 * len(enflamed_populated_areas)
        self.reward += len((np.where(fire + evacuating == 0))[0])

    def advance_to_next_timestep(self):
        """
        Take three steps:
        1. Advance fire forward one timestep
        2. Update paths and evacuation
        3. Accumulate reward and document enflamed areas
        """
        self.sample_fire_propogation()
        self.update_paths_and_evactuations()
        self.accumulate_reward()
        self.time_step += 1

    def set_action(self, action: int):
        """
        Allow the agent to take an action within the action space.
        """
        # Check that there is an action to take
        if (
            action in self.action_to_pop_and_path
            and self.action_to_pop_and_path[action] is not None
        ):
            action_val = self.action_to_pop_and_path[action]
            if action_val is not None and len(action_val) > 0:
                pop_cell, path_index = action_val
                pop_cell_row, pop_cell_col = pop_cell[0], pop_cell[1]

                # Ensure that the path chosen and populated cell haven't
                # burned down and it's not already evacuating and it has not
                # already evacuated
                if (
                    self.paths[path_index][1]
                    and self.state_space[POPULATED_INDEX, pop_cell_row, pop_cell_col]
                    == 1
                    and self.evacuating_timestamps[pop_cell_row, pop_cell_col] == np.inf
                ):

                    # Add to evacuating paths and update state + timestamp
                    if path_index in self.evacuating_paths:
                        self.evacuating_paths[path_index].append(pop_cell)
                    else:
                        self.evacuating_paths[path_index] = [pop_cell]
                    self.state_space[EVACUATING_INDEX, pop_cell_row, pop_cell_col] = 1
                    self.evacuating_timestamps[pop_cell_row, pop_cell_col] = 10

    def get_state_utility(self) -> int:
        """
        Get the total amount of utility given a current state.
        """
        present_reward = self.reward
        self.reward = 0
        return present_reward

    def get_actions(self) -> list:
        """
        Get the set of actions available to the agent.
        """
        return self.actions

    def get_timestep(self) -> int:
        """
        Get current timestep of simulation
        """
        return self.time_step

    def get_state(self) -> np.ndarray:
        """
        Get the state space of the current configuration of the gridworld.
        """
        returned_state = np.copy(self.state_space)
        returned_state[PATHS_INDEX] = np.clip(returned_state[PATHS_INDEX], 0, 1)
        return returned_state

    def get_terminated(self) -> bool:
        """
        Get the status of the simulation.
        """
        return self.time_step >= 100

    def get_finished_evacuating(self) -> list:
        """
        Get the populated areas that are finished evacuating.
        """
        return self.finished_evacuating_cells
