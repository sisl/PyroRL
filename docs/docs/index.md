# PyroRL

PyroRL is a new reinforcement learning OpenAI Gym environment built for the simulation of wildfire evacuation.

<div style="position: relative; padding-bottom: 62.5%; height: 0;"><iframe src="https://www.loom.com/embed/39ddd19c790a49c0a1ea7e13cd4d1005?sid=f14dd119-f833-4ed5-a2e7-56c96593d8c1" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></iframe></div>
<br />

## Motivation

One of the main effects of climate change in the world today is the [increased frequency and intensity of wildfires](https://www.epa.gov/climate-indicators/climate-change-indicators-wildfires). This reality has led to an increase in interest in wildfire response as demonstrated by recent work done by the [Stanford Intelligent Systems Lab](https://sisl.stanford.edu/publications/). This Python package builds off of existing research within wildfire disaster response. The central motivation is to simulate an environment over a wide area with residential sectors and a spreading wildfire. Unlike [previous research](https://arxiv.org/abs/1810.04244), which focused on monitoring the spread of fire, this environment focuses on developing a community’s response to the wildfire in the form of evacuation in an environment that presumes perfect information about the fire’s current state. More specifically, the motivation will be to identify areas that must be evacuated and the ideal path to “safe areas.” We hope to enable researchers to use deep reinforcement learning techniques to accomplish this task.
