import random
import numpy as np

FIRE_INDEX = 0
FUEL_INDEX = 1
POPULATED_INDEX = 2
EVACUATING_INDEX = 3
PATHS_INDEX = 4


def create_map_info(num_rows, num_cols, percent_map_populated):
    if percent_map_populated > 100:
        raise Exception("Cannot have more than 100 percent of the map be populated!")

    orientations = {}
    orientations["north"] = {
        "left": [[0, -1], "west"],
        "right": [[0, 1], "east"],
        "straight": [[-1, 0], "north"],
    }
    orientations["south"] = {
        "left": [[0, 1], "east"],
        "right": [[0, -1], "west"],
        "straight": [[1, 0], "south"],
    }
    orientations["east"] = {
        "left": [[-1, 0], "north"],
        "right": [[1, 0], "south"],
        "straight": [[0, 1], "east"],
    }
    orientations["west"] = {
        "left": [[1, 0], "south"],
        "right": [[-1, 0], "north"],
        "straight": [[0, -1], "west"],
    }
    directions = {0: "left", 1: "right", 2: "straight"}

    state_space = np.zeros([5, num_rows, num_cols])
    paths_to_pops = {}
    num_populated_areas = int(num_rows * num_cols * percent_map_populated * 0.01)
    populated_areas, state_space = generate_pop_locations(
        num_rows, num_cols, num_populated_areas, state_space
    )
    num_paths_array = np.random.normal(3, 1, num_populated_areas).astype(int)
    while 0 in num_paths_array:
        num_paths_array = np.random.normal(3, 1, num_populated_areas).astype(int)

    path_num = 0


def generate_pop_locations(num_rows, num_cols, num_populated_areas, state_space):
    populated_areas = set()
    for _ in range(num_populated_areas):
        pop_row = random.randint(0, num_rows - 1)
        pop_col = random.randint(0, num_cols - 1)
        while (pop_row, pop_col) in populated_areas:
            pop_row = random.randint(0, num_rows - 1)
            pop_col = random.randint(0, num_cols - 1)
        populated_areas.add((pop_row, pop_col))
        state_space[POPULATED_INDEX, pop_row, pop_col] = 1
    populated_areas = np.array(list(populated_areas))
    return populated_areas, state_space
