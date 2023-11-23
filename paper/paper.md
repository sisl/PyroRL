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
  - name: Mykel Kochenderfer
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

One of the main effects of climate change today is the increased frequency and intensity of wildfires. This reality has led to increased research in wildfire response, particularly with reinforcement learning (RL). However, while much effort has centered around modeling wildfire spread or surveillance, there is a lack of work around wildfire evacuation. To this end, we present Wildfire-Evac, a new RL environment for wildfire evacuation. The environment, which builds upon the Gymnasium API standard [@towers_gymnasium_2023], simulates evacuating populated areas through paths from a grid world lit by wildfires. We aim for our work to be the basis of new strategies for wildfire evacuation based on RL methods.

# Statement of Need

There has been significant traction in the use of algorithmic and computational methods to study wildfires. In particular, reinforcement learning -- a subdomain of artificial intelligence (AI) where models learn through interaction with their environment -- has seen much interest from researchers. There have been two prominent areas in reinforcement learning based wildfire research. The first, while not directly related to reinforcement learning, is modeling the spread of wildfires. Traditionally, modeling was predominantly done using physics-based methods [@rothermel1972mathematical; @andrews1986behave]. However, newer methods are more data-driven, enabling the use of a higher diversity of features [@joseph2019spatiotemporal; @diao2020uncertainty].

As better models of wildfire spread are developed, researchers have now been able to focus on the second prominent area of research: wildfire surveillance and monitoring. While various forms of machine learning (ML), such as computer vision [@ganapathi2018using], have been used to solve this task, the most popular method by far has been to employ reinforcement learning [@julian2019distributed; @altamimi2022large; @viseras2021wildfire].

As wildfires continue to be prevalent as a result of climate change, there has been newfound emphasis on the evacuation process [@mccaffrey2018should]. However, there exists no significant literature on the application of computational methods to model and simulate evacuation. Subsequently, while there has been much work around open-source environments for modeling wildfire spread and surveillance [@cellular_automata; @forest_fire], none exist for the task of evacuation. Thus, we believe that by creating a generalizable environment for reinforcement learning, we can encourage more research -- through a new lens -- in the realm of wildfire evacuation.

# Methods

Our environment for wildfire evacuation builds upon the Gymnasium API standard. This standard has functions to help the user `step` through a single time frame of the environment, `reset` the environment back to its original state, and `render` the environment to the user.

## Wildfire Evacuation as a Markov Decision Process

Under the hood, the environment is a gridworld, with dimensions that the user can specify. Each cell in the grid is one of the following:

- Normal terrain
- A populated area
- A fire cell
- Part of an evacuation path

The task at hand is to evacuate all of the populated areas through paths before they are burned down. Akin to how evacuation would occur in real life, the action taker oversees the entire site. Furthermore, the amount of time to evacuate a populated area is proportional to the number of grid squares in the path.

Researchers can thus model the problem as a fully observable Markov Decision Process (MDP):

- State Space: each possible configuration of the grid. Internally, this is represented as a $5$ by $m$ by $n$ tensor, where $m$ and $n$ represent the number of rows and columns of the grid world, respectively. Each of the $5$ indices corresponds to a specific attribute:
    - `0 = FIRE_INDEX` – whether or not a square in the grid world is on fire or not
    - `1 = FUEL_INDEX` – the amount of fuel in the square, which is used to determine if an area will be enflamed or not
    - `2 = POPULATED_INDEX` – whether or not a square is a populated area or not
    - `3 = EVACUATING_INDEX` – whether or not a square is evacuating or not
    - `4 = PATHS_INDEX` – the number of paths a square is a part of
- Action Space: whether or not to evacuate. If evacuating, the action taker must choose a specific populated area to evacuate, as well as a path to evacuate from.
- Transition Model: determined by the stochastic nature of the wildfire implementation, which we describe below
- Reward Model: +1 for every populated area that has not evacuated and isn't burned down, and -100 if a populated area is burned down

## Modeling the Spread of Wildfires

Finally, our stochastic wildfire model is taken from Julian, et. al [@julian2018autonomous]:

- *Fuel*: Each fire cell has an initial fuel level $\sim \mathcal{N}(8.5,\,3)$
    - A cell currently on fire has its fuel levels drop by $1$ after each time step until it runs out of fuel
- *Fire Spread*: We define the spread of the fire by the following equation: $p(s)=1-\Pi_{s'}(1-.094 \cdot d(s,s') \cdot B(s'))$
    - $p(s)$ represents the probability of non-inflamed cell $s$ alighting
    - $s'$ represents an adjacent cell
    - $d(s,s')$ is the $L2$ distance between cells
    - $B(s)$ is a boolean to check if cell is currently on fire

# Features

Firstly, users have a lot of control over the configuration of their environments. Specifically: users can set the dimensions of the grid world, the locations of populated areas and paths, and even manually place where the fire is at initially. Of course, if users just want to get a feel for the package, they can also select from our library of example environments -- which range in size -- or even have the program dynamically generate environments for them. We also offer examples of how to use popular RL libraries with our environment, such as Stable Baselines 3 (cite).

In addition, users can view visualizations of the environment by calling the `render` function of the Gymnasium environment object. At the end of a executing a set of actions on the environment, the user can also call `generate_gif`, which stitches together all of the images rendered by the user into a single GIF to view.

# References
