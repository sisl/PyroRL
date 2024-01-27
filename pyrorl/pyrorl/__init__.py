from gymnasium import register

register(
    id='pyrorl/PyroRL-v0',
    entry_point='pyrorl.envs:WildfireEvacuationEnv',
    max_episode_steps=200,
)
