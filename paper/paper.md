---
title: 'PyroRL: A Reinforcement Learning Environment for Wildfire Evacuation'
tags:
  - python
  - gymanisum
  - rl
  - wildfire
authors:
  - name: Joseph Guman
    equal-contrib: true
    affiliation: 1
  - name: Joseph C. O'Brien
    equal-contrib: true
    affiliation: 1
  - name: Christopher Pondoc
    equal-contrib: true
    affiliation: 1
  - name: Mykel J. Kochenderfer
    affiliation: 2
affiliations:
 - name: Department of Computer Science, Stanford University
   index: 1
 - name: Department of Aeronautics and Astronautics, Stanford University
   index: 2
date: 13 November 2023
bibliography: paper.bib
---

# Summary

A major effect of climate change today is the increased frequency and intensity of wildfires. This reality has led to increased research in wildfire response, particularly with reinforcement learning (RL). While much effort has centered on modeling wildfire spread or surveillance, wildfire evacuation has received less attention. We present PyroRL, a new RL environment for wildfire evacuation. The environment, which builds upon the Gymnasium API standard [@towers_gymnasium_2023], simulates evacuating populated areas through paths from a grid world containing wildfires. This work can serve as a basis for new strategies for wildfire evacuation.

# Statement of Need

There has been significant traction in the use of computational methods to study wildfires. In particular, reinforcement learning -- a subdomain of artificial intelligence where models learn through interaction with their environment -- has seen growing interest from researchers. Applying reinforcement learning requires modeling the spread of wildfires. Traditionally, modeling was primarily done using physics-based methods [@rothermel1972mathematical; @Andrews_1986]. However, newer methods are more data-driven, enabling the use of a higher diversity of features [@https://doi.org/10.1002/eap.1898; @diao2020uncertainty].

Researchers have recently been studying wildfire surveillance and monitoring. While various forms of machine learning, such as computer vision [@ganapathi2018using], have been used to solve this task, the most popular method by far has been reinforcement learning [@julian2019distributed; @altamimi2022large; @9340340]. Research in surveillance and monitoring has been supported by open-source environments for modeling wildfire spread and surveillance [@cellular_automata; @forest_fire].

There has also been emerging interest in optimizing the evacuation process using computational methods [@https://doi.org/10.1111/risa.12944]. However, no reinforcement learning environments exist for the task of evacuation. We hope that open-source tools for evacuation will spur development in this area.

# Methods

Our environment for wildfire evacuation builds upon the Gymnasium API standard. This standard has functions to help the user `step` through a single discrete time step of the environment, `reset` the environment back to its original state, and `render` the environment for the user.

## Wildfire Evacuation as a Markov Decision Process

Under the hood, the environment is a grid world with dimensions that the user can specify. Each cell in the grid is one of the following:

- Normal terrain
- A populated area
- A fire cell
- Part of an evacuation path

The task at hand is to evacuate all of the populated areas through paths before they are ignited. Similar to how evacuation would occur in real life, a centralized decision maker assigns paths to populated areas. Furthermore, the amount of time to evacuate a populated area is proportional to the number of grid squares in the path.

The problem is modeled as a fully observable Markov Decision Process (MDP) [@kochenderfer2022algorithms].
 
### State Space

The state space is each possible configuration of the grid. Internally, this is represented as a $5$ by $m$ by $n$ tensor, where $m$ and $n$ represent the number of rows and columns of the grid world, respectively. Each of the $5$ indices corresponds to a specific attribute:

- `0 = FIRE_INDEX` – whether or not a square in the grid world is on fire or not
- `1 = FUEL_INDEX` – the amount of fuel in the square, which is used to determine if an area will be enflamed or not
- `2 = POPULATED_INDEX` – whether or not a square is a populated area or not
- `3 = EVACUATING_INDEX` – whether or not a square is evacuating or not
- `4 = PATHS_INDEX` – the number of paths a square is a part of

### Action Space
The action space describes whether or not a populated area should evacuate. If evacuating, the agent must choose a specific populated area to evacuate, as well as a path from which to evacuate.

- Transition Model: determined by the stochastic nature of the wildfire implementation, which we describe below
- Reward Model: $+1$ for every populated area that has not evacuated and is not ignited, and $-100$ if a populated area is burned down

## Modeling the Spread of Wildfires

Finally, our stochastic wildfire model is based on prior work [@Julian2019]:

### Fuel

Each fire cell has an initial fuel level $\sim \mathcal{N}(\mu, \, (\sigma)^{2})$

- A cell currently on fire has its fuel level drop by $1$ after each time step until it runs out of fuel

Users can configure $\mu$ and $\sigma$. By defualt, their respective values are $\mu=8.5$ and $\sigma=\sqrt 3$

### Fire Spread

We define the spread of the fire by the following equation: $p(s)=1-\Pi_{s'}(1 - \lambda \cdot d(s,s') \cdot B(s'))$

- $p(s)$ represents the probability of non-inflamed cell $s$ alighting
- $s'$ represents an adjacent cell
- $\lambda$ is a hyperparameter that affects the probability of fire spreading from one cell to an adjacent one
- $d(s,s')$ is the Euclidean distance between cells
- $B(s)$ is a Boolean to check if cell is currently on fire

Users can configure $\lambda$. By defualt, the value is $\lambda=0.094$.

### Wind

The spread of wildfire is also influenced by wind. This bias is modeled through a linear transformation using two properties. First, the wind speed affects the probability of neighboring cells igniting the current cell. In addition, for each cell, we calculate the vectors that point in the direction of each neighboring cell. We then take the dot product between this vector and the direction of the wind.

# Features

Users can control the configuration of the environment, including the dimensions of the grid world, the locations of populated areas and paths, and initial fire placement. Users can also select from our library of example environments or have the program dynamically generate environments. We also offer examples of how to use popular RL libraries with our environment, such as Stable-Baselines3 [@JMLR:v22:20-1364].

In addition, users can generate visualizations of the environment by calling the `render` function of the Gymnasium environment object. After executing a set of actions on the environment, the user can call `generate_gif`, which stitches together all of the images rendered by the user into a single GIF.

# References
