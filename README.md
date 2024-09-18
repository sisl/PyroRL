<pre>
██████╗ ██╗   ██╗██████╗  ██████╗ ██████╗ ██╗     
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔═══██╗██╔══██╗██║     
██████╔╝ ╚████╔╝ ██████╔╝██║   ██║██████╔╝██║     
██╔═══╝   ╚██╔╝  ██╔══██╗██║   ██║██╔══██╗██║     
██║        ██║   ██║  ██║╚██████╔╝██║  ██║███████╗
╚═╝        ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
</pre>

![example workflow](https://github.com/sisl/PyroRL/actions/workflows/testing.yml/badge.svg) [![codecov](https://codecov.io/github/sisl/PyroRL/graph/badge.svg?token=wBlFGsd5sS)](https://codecov.io/github/sisl/PyroRL) [![](https://img.shields.io/badge/docs-latest-blue.svg)](https://sisl.github.io/PyroRL/)  [![DOI](https://joss.theoj.org/papers/10.21105/joss.06739/status.svg)](https://doi.org/10.21105/joss.06739)

PyroRL is a new reinforcement learning environment built for the simulation of wildfire evacuation. Check out the [docs](https://sisl.github.io/PyroRL/) and the [demo](https://www.loom.com/share/39ddd19c790a49c0a1ea7e13cd4d1005?sid=679b631a-74b7-41e3-bd88-3e7d14c0adc2).

## How to Use

First, install our package. Note that PyroRL requires Python version 3.8:

```bash
pip install pyrorl
```

To use our wildfire evacuation environment, define the dimensions of your grid, where the populated areas are, the paths, and which populated areas can use which path. See an example below.

```python
# Create environment
kwargs = {
    'num_rows': num_rows,
    'num_cols': num_cols,
    'populated_areas': populated_areas,
    'paths': paths,
    'paths_to_pops': paths_to_pops
}
env = gymnasium.make('pyrorl/PyroRL-v0', **kwargs)

# Run a simple loop of the environment
env.reset()
for _ in range(10):

    # Take action and observation
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)

    # Render environment and print reward
    env.render()
    print("Reward: " + str(reward))
```

A compiled visualization of numerous iterations is seen below. For more examples, check out the `examples/` folder.

![Example Visualization of PyroRL](imgs/example_visualization.gif)

For a more comprehensive tutorial, check out the [quickstart](https://sisl.github.io/PyroRL/quickstart/) page on our docs website.

## How to Contribute

For information on how to contribute, check out our [contribution guide](https://sisl.github.io/PyroRL/contribution-guide/).
