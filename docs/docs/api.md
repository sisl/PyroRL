# API Reference

We provide API documentation for the public endpoints that are intended to be utilized by the end user. Namely, we describe the functionality of our wildfire evacuation environment and our map generation functions.

## `WildfireEvacuationEnv`

Below are the member functions for the core wildfire evacuation environment, which is an extension of the [Gymnasium API](https://gymnasium.farama.org/index.html) Standard.

### `__init__`

```
__init__(
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
    fuel_mean: float = 8.5,
    fuel_stdev: float = 3,
    fire_propagation_rate: float = 0.094,
    skip: bool = False,
):
```

This function is the constructor for our wildfire environment.

#### Parameters
- `num_rows` (`int`) -- The number of rows in the grid.
- `num_cols` (`int`) -- The number of columns in the grid.
- `populated_areas` (`np.ndarray`) -- A `numpy` array containing the information of the location of every populated area in the map. Formatting is specified as `[[row_i,col_i],[row_i, col_i]]`
- `paths` (`np.ndarray`) -- A `numpy` array of type object where each element represents a list of locations taken by a single path. Formatting is specified for j as `[[[row_{j0},col_{j0}],[row_{j1},col_{j1}]]_j]`
- `paths_to_pops` (`dict`) -- The i'th path specified in paths is specified by the key i in this dict which leads to a location of a populated area specified in `populated_areas` to identify that path as servicing that populated area.
- `num_fire_cells` (`int`) -- The number of fires the user wishes to start the simulation with.
- `custom_fire_locations` (`Optional[np.ndarray]`) -- A user can specify the exact location fires will start at. Overrides `num_fire_cells` if given by user.
- `wind_speed` (`optional[float]`) -- Optional parameter specifying the speed of wind to affect fire propogation patterns. If used, user must also specify wind_angle.
- `wind_angle` (`optional[float]`) -- Optional parameter specifying the angle of wind in radians to affect fire propogation patterns. If used, user must also specify wind_speed.
- `fuel_mean` (`float`) -- Mean in normal distribution to decide the amount of fuel in a given cell.
- `fuel_stdev` (`float`) -- Standard deviation in normal distribution to decide the amount of fuel in a given cell.
- `fire_propagation_rate` (`float`) -- Proportional scaling term to describe the chance an enflamed cell lights another cell.
- `skip` (`bool`) -- If set to true, calls to visualization will not display visualization at runtime, but just save data for post simulation complete visualization. 

#### Return Values
- None

### `reset`

```
WildfireEvacuationEnv.reset(
    self, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None
) -> tuple[np.ndarray, dict[str, Any]]:
```

This function resets the wildfire environment to its initial state.

#### Parameters
- `seed` (`Optional[int]`) -- Ignored
- `options` (`Optional[dict[str, Any]]`) -- Ignored

#### Return Values
- `state_space` (`np.ndarray`) -- The reset state space after performing the action
- `info` (`dict`) -- Ignored

### `step`

```
WildfireEvacuationEnv.step(self, action: int) -> tuple
```

This function takes an action in the wildfire environment and also updates the corresponding state space.

#### Parameters
- `action` (`int`) -- the action to take in our environment. In this context, the action is sampled from the environment's `action_space` and corresponds to evacuating a singular populated area from a singular path.

#### Return Values
- `observations` (`np.ndarray`) -- The updated state space after performing the action
- `rewards` (`int`) -- The reward accrued after taking an action
- `terminated` (`bool`) -- Whether or not the simulation has come to an end
- `truncated` (`bool`) -- Ignored
- `info` (`dict`) -- Ignored

### `render`

```
WildfireEvacuationEnv.render(self) -> None
```

This function renders the environment in a Pygame grid for the user to visualize or save. 

#### Parameters
- None

#### Return Values
- None

### `generate_gif`

```
WildfireEvacuationEnv.generate_gif(self) -> None
```

This function saves a stitched GIF of all visualizations rendered by the user.

#### Parameters
- None

#### Return Values
- None

## `create_map_info`

Below are the member functions for the helper fiile that helps generate maps dynamically.

### `load_map_info`

```
create_map_info.load_map_info(map_directory_path: str) -> tuple:
```
This function loads in the saved information for a grid. 

#### Parameters
- `map_directory_path` (`str`): The path for the subdirectory where the data for the relevant grid is stored.

#### Return Values
- `num_rows` (`int`) -- The number of rows in the grid.
- `num_cols` (`int`) -- The number of columns in the grid.
- `populated_areas` (`np.ndarray`) -- A `numpy` array containing the information of the location of every populated area in the map. Formatting is specified as `[[row_i,col_i],[row_i, col_i]]`
- `paths` (`np.ndarray`) -- A `numpy` array of type object where each element represents a list of locations taken by a single path. Formatting is specified for j as `[[[row_{j0},col_{j0}],[row_{j1},col_{j1}]]_j]`
- `paths_to_pops` (`dict`) -- The i'th path specified in paths is specified by the key i in this dict which leads to a location of a populated area specified in `populated_areas` to identify that path as servicing that populated area.
- `num_populated_areas` (`int`) -- The number of populated areas on the grid.

### `generate_map_info`

```
generate_map_info(
    num_rows: int,
    num_cols: int,
    num_populated_areas: int,
    save_map: bool = True,
    steps_lower_bound: int = 2,
    steps_upper_bound: int = 4,
    percent_go_straight: int = 50,
    num_paths_mean: int = 3,
    num_paths_stdev: int = 1,
) -> tuple:
```
This function generates the data needed to create a grid.

#### Parameters
- `num_rows` (`int`) -- The number of rows in the grid.
- `num_cols` (`int`) -- The number of columns in the grid.
- `num_populated_areas` (`int`) -- The number of populated areas in the grid.
- `save_map` (`bool`) -- Whether or not the information for the map generation should be saved for later use.
- `steps_lower_bound` (`int`) -- The lower bound for the random generation of how many steps are taken during each iteration of a path creation.t- `steps_upper_bound` (`int`) -- The upper bound for the random generation of how many steps are taken during each iteration of a path creation.
- `percent_go_straight` (`int`) -- What percent of the time a path will try to continue straight rather than taking a turn.
- `num_paths_mean` (`int`) -- The mean of the normal distribution that is sampled from to determine the number of paths for a populated area.
- `num_paths_stdev` (`int`) -- The standard deviation of the normal distribution that is sampled from to determine the number of paths for a populated area.

#### Return Values
- `populated_areas` (`np.ndarray`) -- A `numpy` array containing the information of the location of every populated area in the map. Formatting is specified as `[[row_i,col_i],[row_i, col_i]]`
- `paths` (`np.ndarray`) -- A `numpy` array of type object where each element represents a list of locations taken by a single path. Formatting is specified for j as `[[[row_{j0},col_{j0}],[row_{j1},col_{j1}]]_j]`
- `paths_to_pops` (`dict`) -- The i'th path specified in paths is specified by the key i in this dict which leads to a location of a populated area specified in `populated_areas` to identify that path as servicing that populated area.