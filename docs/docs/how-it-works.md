# How it works

## Overview of State Space
We represent the state space as an (5 by `num_rows` by `num_cols`) `np.array`. Specifically, each of the 5 `np.array`s identifies a specific attribute:

- `0 = FIRE_INDEX` – whether or not a square in the grid world is on fire or not
- `1 = FUEL_INDEX` – the amount of fuel in the square, which is used to determine if an area will be enflamed or not
- `2 = POPULATED_INDEX` – whether or not a square is a populated area or not
- `3 = EVACUATING_INDEX` – whether or not a square is evacuating or not
- `4 = PATHS_INDEX` – the number of paths a square is a part of

## Overview of Action Space

Our simulation assumes that our action taker oversees the entire grid world, as this models how evacuation would occur in real life. The action space is defined as the number of possible paths to evacuate by, plus an extra action to do nothing. When an agent takes an action, three steps occur:

1. The wildfire model propagates and expands to neighboring cells
2. The available paths are updated, as well as which areas are evacuating or not
3. The environment calculates the total amount of reward accumulated

## Spread of Wildfire
Each fire cell has an initial fuel level drawn from a normal distribution. The spread of the wildfire is stochastic.
