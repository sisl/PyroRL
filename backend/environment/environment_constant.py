import numpy as np
import torch

distance_matrix = torch.tensor([[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2],[2,1,0,1,2]])
temp = distance_matrix ** 2
distance_matrix = 1 - 1 / (temp + temp.T) * .094
distance_matrix[2,2] = 1
fire_mask = distance_matrix.reshape((25,1))