import numpy as np
import torch

# Mask used for calculating the probability a cell alighting following the same propagation formula from existing research
# Distance along axis from origin. Origin is referring to the cell we are presently trying to determine if becomes enflamed in the next timestep
distance_to_probability_of_enflaming_ratio = .094
distance_matrix = torch.tensor([[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2]])
# Squaring of values for later calculating square of L2 norm
temp = distance_matrix ** 2
# Calculate the probability an enflamed neighboring cell does not enflame the cell located at the origin
distance_matrix = 1 - 1 / (temp + temp.T) * distance_to_probability_of_enflaming_ratio
# As there is zero distance between the origin and itself, we set this value to 1, so the contribution of the origin is ignored in the product
distance_matrix[2,2] = 1
# Flatten probably mask so it can be efficiently used as a kernel
base_fire_mask = distance_matrix.reshape((25,1))
fire_mask = np.copy(base_fire_mask)

# Wind components
# The rate with which speed of wind converts to a percent change in the chance of a neighbor cell igniting the center cell
speed_to_percent_ratio = 0.1
axis_distance = np.array([5 * [-i] for i in range(-2,3)])
# a 5x5 matrix where each element represents a vector pointing in the direction of the corresponding neihboring cell
neighbor_vectors = np.stack((-axis_distance.T, axis_distance), axis=2).reshape((-1,2))
neighbor_vectors[12,:] = 1
# Normalizes these vectors to unit vectors
normalizer = np.linalg.norm(neighbor_vectors, axis = 1).reshape((neighbor_vectors.shape[0], 1))
neighbor_vectors = neighbor_vectors / normalizer.reshape((normalizer.size, 1))
neighbor_vectors[12,:] = 0


# Computes a simple linear transformation of fire propogation probabilities scaled linearly by the speed of the wind and the dot product
# between the wind direction and the direction to the neighboring cell
# Probabilities are clamped around 0 and 1
def linear_wind_transform(wind_speed : float, wind_angle : float):
    wind_vector = np.array([[np.cos(wind_angle)], [np.sin(wind_angle)]])
    scaling_term = -(neighbor_vectors @ wind_vector) * speed_to_percent_ratio * wind_speed + 1
    return np.clip(scaling_term * base_fire_mask, a_min=0, a_max=1)