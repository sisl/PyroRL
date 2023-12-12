---
title: 'Wildfire-Evac: A Reinforcement Learning Environment for Wildfire Evacuation'
tags:
  - python
  - gymanisum
  - rl
  - wildfire
authors:
  - name: Joseph Guman
    equal-contrib: true
    affiliation: 1
  - name: Joseph O'Brien
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

A major effect of climate change today is the increased frequency and intensity of wildfires. This reality has led to increased research in wildfire response, particularly with reinforcement learning (RL). However, while much effort has centered on modeling wildfire spread or surveillance, there is a lack of work around wildfire evacuation. We present Wildfire-Evac, a new RL environment for wildfire evacuation. The environment, which builds upon the Gymnasium API standard [@towers_gymnasium_2023], simulates evacuating populated areas through paths from a grid world containing wildfires. This work can serve as a basis for new strategies for wildfire evacuation.

# Statement of Need

There has been significant traction in the use of computational methods to study wildfires. In particular, reinforcement learning -- a subdomain of artificial intelligence where models learn through interaction with their environment -- has seen growing interest from researchers. Applying reinforcement learning requires modeling the spread of wildfires. Traditionally, modeling was primarily done using physics-based methods [@rothermel1972mathematical; @andrews1986behave]. However, newer methods are more data-driven, enabling the use of a higher diversity of features [@joseph2019spatiotemporal; @diao2020uncertainty].

Researchers have recently been studying wildfire surveillance and monitoring. While various forms of machine learning (ML), such as computer vision [@ganapathi2018using], have been used to solve this task, the most popular method by far has been to employ reinforcement learning [@julian2019distributed; @altamimi2022large; @viseras2021wildfire].

There has also been interest in optimizing the evacuation process [@mccaffrey2018should]. However, there exists no significant literature on the application of computational methods to model and simulate evacuation. Subsequently, while there has been much work around open-source environments for modeling wildfire spread and surveillance [@cellular_automata; @forest_fire], none exist for the task of evacuation. We believe that by creating a generalizable environment for reinforcement learning, we can encourage more research in the realm of wildfire evacuation.

# Methods

Our environment for wildfire evacuation builds upon the Gymnasium API standard. This standard has functions to help the user `step` through a single discrete time step of the environment, `reset` the environment back to its original state, and `render` the environment to the user.

## Wildfire Evacuation as a Markov Decision Process

Under the hood, the environment is a gridworld, with dimensions that the user can specify. Each cell in the grid is one of the following:

- Normal terrain
- A populated area
- A fire cell
- Part of an evacuation path

The task at hand is to evacuate all of the populated areas through paths before they are ignited. Similar to how evacuation would occur in real life, a centralized decision maker assigns paths to populated areas. Furthermore, the amount of time to evacuate a populated area is proportional to the number of grid squares in the path.

The problem is modeled a fully observable Markov Decision Process (MDP) [@kochenderfer2022algorithms].

### State Space

Each possible configuration of the grid. Internally, this is represented as a $5$ by $m$ by $n$ tensor, where $m$ and $n$ represent the number of rows and columns of the grid world, respectively. Each of the $5$ indices corresponds to a specific attribute:

- `0 = FIRE_INDEX` – whether or not a square in the grid world is on fire or not
- `1 = FUEL_INDEX` – the amount of fuel in the square, which is used to determine if an area will be enflamed or not
- `2 = POPULATED_INDEX` – whether or not a square is a populated area or not
- `3 = EVACUATING_INDEX` – whether or not a square is evacuating or not
- `4 = PATHS_INDEX` – the number of paths a square is a part of

### Action Space
Whether or not to evacuate. If evacuating, the agent must choose a specific populated area to evacuate, as well as a path to evacuate from.

- Transition Model: determined by the stochastic nature of the wildfire implementation, which we describe below
- Reward Model: $+1$ for every populated area that has not evacuated and is not ignited, and $-100$ if a populated area is burned down

## Modeling the Spread of Wildfires

Finally, our stochastic wildfire model is taken from Julian, et al. [@julian2018autonomous]:

### Fuel

Each fire cell has an initial fuel level $\sim \mathcal{N}(8.5, \, (\sqrt{3})^{2})$

- A cell currently on fire has its fuel level drop by $1$ after each time step until it runs out of fuel

### Fire Spread

We define the spread of the fire by the following equation: $p(s)=1-\Pi_{s'}(1-.094 \cdot d(s,s') \cdot B(s'))$

- $p(s)$ represents the probability of non-inflamed cell $s$ alighting
- $s'$ represents an adjacent cell
- $d(s,s')$ is the $L2$ distance between cells
- $B(s)$ is a boolean to check if cell is currently on fire

### Wind

We can add wind bias by modifying the convolution filter. In our working implementation, wind speed is linearly scale of how wind affects probability of neighboring cell alighting current cell. linear scale is further scaled for each neighboring cell by cosine similarity of vector between direction to neighboring cell to wind direction.

# Features

Users are given control over the configuration of their environments, including: the dimensions of the grid world, the locations of populated areas and paths, and initial fire placement. Users can also select from our library of example environments or have the program dynamically generate environments. We also offer examples of how to use popular RL libraries with our environment, such as Stable-Baselines3 [@JMLR:v22:20-1364].

In addition, users can generate visualizations of the environment by calling the `render` function of the Gymnasium environment object. After executing a set of actions on the environment, the user can call `generate_gif`, which stitches together all of the images rendered by the user into a single GIF.

# References
