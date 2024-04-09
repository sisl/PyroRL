# How it works

## Wildfire Evacuation as a Markov Decision Process

### Overview of State Space
The state space is each possible configuration of the grid. Internally, this is represented as a $5$ by $m$ by $n$ tensor, where $m$ and $n$ represent the number of rows and columns of the grid world respectively. Each of the $5$ indices corresponds to a specific attribute:

- `0 = FIRE_INDEX` – whether or not a square in the grid world is on fire or not
- `1 = FUEL_INDEX` – the amount of fuel in the square, which is used to determine if an area will be enflamed or not
- `2 = POPULATED_INDEX` – whether or not a square is a populated area or not
- `3 = EVACUATING_INDEX` – whether or not a square is evacuating or not
- `4 = PATHS_INDEX` – the number of paths a square is a part of

### Overview of Action Space

The action space describes whether or not a populated area should evacuate. If evacuating, the agent must choose a specific populated area to evacuate, as well as a path from which to evacuate.

- Transition Model: determined by the stochastic nature of the wildfire implementation, which we describe below
- Reward Model: $+1$ for every populated area that has not evacuated and is not ignited, and $-100$ if a populated area is burned down

### Spread of Wildfire

Finally, our stochastic wildfire model is based on [prior work](https://arxiv.org/abs/1810.04244):

#### Fuel

Each fire cell has an initial fuel level $\sim \mathcal{N}(\mu, \, (\sigma)^{2})$

- A cell currently on fire has its fuel level drop by $1$ after each time step until it runs out of fuel

Users can configure $\mu$ and $\sigma$. By defualt, their respective values are $\mu=8.5$ and $\sigma=\sqrt 3$

#### Fire Spread

We define the spread of the fire by the following equation: $p(s)=1-\Pi_{s'}(1 - \lambda \cdot d(s,s') \cdot B(s'))$

- $p(s)$ represents the probability of non-inflamed cell $s$ alighting
- $s'$ represents an adjacent cell
- $\lambda$ is a hyperparameter that affects the probability of fire spreading from one cell to an adjacent one
- $d(s,s')$ is the Euclidean distance between cells
- $B(s)$ is a Boolean to check if cell is currently on fire

Users can configure $\lambda$. By defualt, the value is $\lambda=0.094$.

#### Wind

The spread of wildfire is also influenced by wind. This bias is modeled through a linear transformation using two properties. First, the wind speed affects the probability of neighboring cells igniting the current cell. In addition, for each cell, we calculate the vectors that point in the direction of each neighboring cell. We then take the dot product between this vector and the direction of the wind.

## Custom Map Generation

### How to Load and Generate Maps
To generate and load maps, the two functions of note are `generate_map_info` and `load_map_info` located within the `create_map_info.py` file in the `map_helpers` directory. 

For the `generate_map_info` function, the main parameters that the user must provide are the size of the grid -- in terms of the number of rows (`num_rows`) and the number of columns (`num_cols`) -- and the number of populated cells the user would like the map to have (`num_populated_areas`). The maps are saved automatically, but this behavior can be turned off by setting the `save_map` parameter to `False`. Furthermore, the number of steps that are taken each iteration (every time a direction is chosen) are randomly chosen in the range stipulated by `steps_lower_bound` and `steps_upper_bound` which are 2 and 4 by default. The standard behavior of the map generation is to favor going straight $50$% of the time, but this behavior can be changed by altering the `percent_go_straight` parameter. The number of paths generated for each populated area are also selected from a normal distribution with a mean of $3$ and standard deviation of $1$, but these values can be altered by specifying the `num_paths_mean` and `num_paths_stdev` parameters. 

If the `save_map` parameter is set to `True` when generating maps (the default behavior), the map is saved to the user’s current working directory by first creating a new subdirectory called `pyrorl_map_info` which stores all the subdirectories created for each subsequent map generation. For a given map generation, a new subdirectory is created within the `pyrorl_map_info` folder that is titled with the timestamp of when the map was created. Within this folder is a text file that is present for the user to easily see the number of rows, number of columns, and number of populated areas for the generation. This folder also contains pickle files that store the `populated_areas` array, `paths` array, `paths_to_pops` array, and a list that contains the number of rows, number of columns, and number of populated areas. 

To load in a map, the path for the directory containing the relevant map information must be provided to the `load_map_info` function (by default, the title of the directory will by a timestamp). This function will then return the number of rows, the number of columns, the `populated_areas` array, the `paths` array, the `paths_to_pops` array, and the number of populated areas. 

### Deep Dive on Map Generation Implementation
As a quick note, know that paths are allowed to overlap with each other and that paths can proceed through other populated areas.

In terms of the actual implementation of the map generation code, the populated areas are first randomly generated on the grid. These populated areas cannot be generated on the edge of the grid. Once the populated areas are selected, the number of paths for each area are then selected from a normal distribution with the mean and standard deviation taken from the provided parameters. 

Each path is then generated for their respective populated area. Each path is generated starting from the coordinates of their respective populated areas. When creating a path, orientation and direction lie at the heart of the generation. Orientation is the cardinal direction an individual would be facing if they were to walk straight along the path, with north pointing to the top of the map (lower values of rows), south pointing to the bottom of the map (higher values of rows), east pointing to the right of the map (higher values of columns), and west pointing to the left of the map (lower values of columns). At the start of the map generation, the beginning orientation is selected randomly. Direction refers to how a person would proceed if they were to continue walking along the path given their current orientation, with the three directions being left, right, and straight. To update a path, a direction is first chosen. Once a direction is chosen, the orientation is updated and the path is extended along the new orientation for a given number of steps which is randomly chosen as a value between a given lower bound and upper bound provided as a parameter (2 and 3 by default). This process continues until the path reaches the edge of the map. 

As an example of a generation iteration, consider the current orientation being “east” and the number of steps being 3. If the direction chosen is straight, the path will continue to extend east 3 steps. If the direction chosen is left, the orientation will change to north and the path will extend north 3 steps. If the direction chosen is right, the orientation will change to south and the path will extend south 3 steps. 

Lastly, the code was designed so that paths will not overlap/intersect with themselves, meaning that as the paths are generated they will continue to proceed outwards towards the edge of the map. This is achieved by noting the minimum and maximum row index and minimum and maximum column index that the path has reached so far. There are then some special restrictions for each orientation on whether or not they can turn left or right (i.e. not proceed straight). If the orientation is north, then to take a turn the horizon (i.e. edge) of the path must currently be the minimum row index. If the orientation is south, then to take a turn the horizon (i.e. edge) of the path must currently be the maximum row index. If the orientation is east, then to take a turn the horizon (i.e. edge) of the path must currently be the maximum column index. If the orientation is west, then to take a turn the horizon (i.e. edge) of the path must currently be the minimum column index. 
