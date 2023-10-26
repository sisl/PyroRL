# Wildfire Evacuation RL Gym Environment

A new reinforcement learning OpenAI Gym environment built for the simulation of wildfire evacuation. Check out the [docs](https://docs.google.com/document/d/1IpA1HS6_81OnfwQktYsEsL9z5eDfbmcg-3HQZxJtLYs/edit?usp=sharing).

## How To Use

First, install our package:

```bash
pip install wildfire-evac
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
env = gymnasium.make('wildfire_evac/WildfireEvacuation-v0', **kwargs)

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

For more examples, check out `examples/`.

## Set-Up

To set up our codebase, create a virtual environment and install a local copy of the package.

```bash
python3 -m venv env
source env/bin/activate
cd wildfire_evac/
pip install .
```

## Tests

We use `pytest` for our backend tests. To keep the state of our package as small as possible, we don't include `pytest`. Thus, make sure to install the package before running.

```bash
pip install pytest
python3 -m pytest -s
```
