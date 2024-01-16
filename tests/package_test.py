"""
Testing the OpenAI Gym Package itself.
"""
import gymnasium
import numpy as np
import wildfire_evac

def test_constructor():
    """
    Test the constructor to make sure all variables are accounted for.
    """
    # Set up parameters
    num_rows, num_cols = 10, 10
    populated_areas = np.array([[1,2],[4,8], [6,4], [8, 7]])
    paths = np.array([[[1,0],[1,1]], [[2,2],[3,2],[4,2],[4,1],[4,0]], [[2,9],[2,8],[3,8]], [[5,8],[6,8],[6,9]], [[7,7], [6,7], [6,8], [6,9]], [[8,6], [8,5], [9,5]], [[8,5], [9,5], [7,5],[7,4]]], dtype=object)
    paths_to_pops = {0:[[1,2]], 1:[[1,2]], 2: [[4,8]], 3:[[4,8]], 4:[[8, 7]], 5:[[8, 7]], 6:[[6,4]]}

    # Create environment
    kwargs = {
        'num_rows': num_rows,
        'num_cols': num_cols,
        'populated_areas': populated_areas,
        'paths': paths,
        'paths_to_pops': paths_to_pops
    }
    env = gymnasium.make('wildfire_evac/WildfireEvacuation-v0', **kwargs)
    
    # Make basic checks
    assert(env.num_rows == num_rows)