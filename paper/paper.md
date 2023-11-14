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

One of the main effects of climate change today is the increased frequency and intensity of wildfires. This reality has led to increased research in wildfire response, particularly with reinforcement learning (RL). However, while much effort has centered around modeling wildfire spread or surveillance, there is a lack of work around wildfire evacuation. To this end, we present Wildfire-Evac, a new RL environment for wildfire evacuation. The environment, which builds upon the Gymnasium API standard (Towers 2023), simulates evacuating populated areas through paths from a grid world lit by wildfires. We aim for our work to be the basis of new strategies for wildfire evacuation based on RL methods.

# Statement of Need

There has been significant traction in the use of algorithmic and computational methods to study wildfires. In particular, reinforcement learning -- a subdomain of artificial intelligence (AI) where models learn through interaction with their environment -- has seen much interest from researchers. There have been two prominent areas in reinforcement learning based wildfire research. The first, while not directly related to reinforcement learning, is modeling the spread of wildfires. Traditionally, modeling was predominantly done using physics-based methods (Rothermel 1972, Andrews 1986). However, newer methods are more data-driven, enabling the use of a higher diversity of features (Joseph 2019, Singla 2021).

As better models of wildfire spread are developed, researchers have now been able to focus on the second prominent area of research: wildfire surveillance and monitoring. While various forms of machine learning (ML), such as computer vision (Subramanian 2017), have been used to solve this task, the most popular method by far has been to employ reinforcement learning (Julian 2019, Altamimi 2022, Viseras 2021).

As wildfires continue to be prevalent as a result of climate change, there has been newfound emphasis on the evacuation process (McCaffrey 2018). However, there exists no significant literature on the application of computational methods to model and simulate evacuation. Subsequently, while there has been much work around open-source environments for modeling wildfire spread and surveillance (https://github.com/sahandrez/gym_forestfire, https://github.com/elbecerrasoto/gym-cellular-automata), none exist for the task of evacuation. Thus, we believe that by creating a generalizable environment for reinforcement learning, we can encourage more research -- through a new lens -- in the realm of wildfire evacuation.

# Methods

## Overview of Environment
- How is the grid world set up? Describe the agent, the task, the state, and the action space

## Wildfire Propagation
- How does wildfire propagate? What does wind bias look like?

# Features
- How can users create custom environments/use standalone environments? Integration with other libraries? Visualization?
