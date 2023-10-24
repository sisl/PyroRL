from gymnasium import register

register(
    id='wildfire_evac/WildfireEvacuation-v0',
    entry_point='wildfire_evac.envs:WildfireEvacuationEnv',
    max_episode_steps=200,
)
