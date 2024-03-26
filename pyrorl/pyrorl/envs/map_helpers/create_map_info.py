import random
import numpy as np
import pickle as pkl
import os
from pyrorl.envs.environment.environment import FireWorld

# randomly generate populated areas
def generate_pop_locations(num_rows, num_cols, num_populated_areas):
    populated_areas = set()
    for _ in range(num_populated_areas):
        pop_row = random.randint(0, num_rows - 1)
        pop_col = random.randint(0, num_cols - 1)
        while (pop_row, pop_col) in populated_areas:
            pop_row = random.randint(0, num_rows - 1)
            pop_col = random.randint(0, num_cols - 1)
        populated_areas.add((pop_row, pop_col))
    populated_areas = np.array(list(populated_areas))
    return populated_areas

def create_orientations():
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
    return orientations

def save_map_info(num_rows, num_cols, percent_map_populated, populated_areas, paths, paths_to_pops):
    user_working_directory = os.getcwd()
    maps_info_directory = os.path.join(user_working_directory, "pyrorl_map_info")
    if not os.path.exists(maps_info_directory):
        os.makedirs(maps_info_directory)
    current_map_info = str(num_rows)+ "_rows_" + str(num_cols) + "_cols_" + str(percent_map_populated) + "_percent_map_populated"
    generation = 0
    current_map_directory = os.path.join(maps_info_directory, current_map_info + "_generation" + str(generation))
    while os.path.exists(current_map_directory):
        generation += 1
        current_map_directory = os.path.join(maps_info_directory, current_map_info + "_generation" + str(generation))
    os.makedirs(current_map_directory)
    populated_areas_filename = os.path.join(current_map_directory, "popualted_areas_array.pkl")
    with open(populated_areas_filename, 'wb') as f:
        pkl.dump(populated_areas, f)
    paths_filename = os.path.join(current_map_directory, "paths_array.pkl")
    with open(paths_filename, 'wb') as f:
        pkl.dump(paths, f)
    paths_to_pops_filename = os.path.join(current_map_directory, "paths_to_pops_array.pkl")
    with open(paths_to_pops_filename, 'wb') as f:
        pkl.dump(paths_to_pops, f)
    map_size_and_percent_popualted_list = [num_rows, num_cols, percent_map_populated]
    map_size_and_percent_popualted_list_filename = os.path.join(current_map_directory, "map_size_and_percent_popualted_list.pkl")
    with open(map_size_and_percent_popualted_list_filename, 'wb') as f:
        pkl.dump(map_size_and_percent_popualted_list, f)

def load_map_info(map_directory_path):
    populated_areas_filename = os.path.join(map_directory_path, "popualted_areas_array.pkl")
    with open(populated_areas_filename, 'rb') as f:
        populated_areas = pkl.load(f)
    paths_filename = os.path.join(map_directory_path, "paths_array.pkl")
    with open(paths_filename, 'rb') as f:
        paths = pkl.load(f)
    paths_to_pops_filename = os.path.join(map_directory_path, "paths_to_pops_array.pkl")
    with open(paths_to_pops_filename, 'rb') as f:
        paths_to_pops = pkl.load(f)
    map_size_and_percent_popualted_list_filename = os.path.join(map_directory_path, "map_size_and_percent_popualted_list.pkl")
    with open(map_size_and_percent_popualted_list_filename, 'rb') as f:
        map_size_and_percent_popualted_list = pkl.load(f)
    num_rows = map_size_and_percent_popualted_list[0]
    num_cols = map_size_and_percent_popualted_list[1]
    percent_map_populated = map_size_and_percent_popualted_list[2]
    return num_rows, num_cols, populated_areas, paths, paths_to_pops, percent_map_populated


def generate_map_info(num_rows, num_cols, percent_map_populated, save_map = True):
    if percent_map_populated > 100:
        raise Exception("Cannot have more than 100 percent of the map be populated!")

    orientations = create_orientations()
    directions = {0: "left", 1: "right", 2: "straight"}

    paths_to_pops = {}
    num_populated_areas = int(num_rows * num_cols * percent_map_populated * 0.01)
    populated_areas = generate_pop_locations(
        num_rows, num_cols, num_populated_areas
    )

    # the number of paths for each populated area is chosen from normal distribution
    num_paths_array = np.random.normal(3, 1, num_populated_areas).astype(int)
    # each populated area must have at least one path
    while 0 in num_paths_array:
        num_paths_array = np.random.normal(3, 1, num_populated_areas).astype(int)

    paths = []
    path_num = 0

    for i in range(len(populated_areas)):
        pop_row, pop_col = populated_areas[i]

        num_pop_paths_created = 0  # for cases where a path couldn't be made
        while num_pop_paths_created < num_paths_array[i]:
            current_path = []

            cur_row, cur_col = pop_row, pop_col

            # initialize bounds to not restrict to start
            x_min = num_rows
            x_max = -1
            y_min = num_cols
            y_max = -1

            # which direction to span out from first
            orientation = random.choice(["north", "south", "east", "west"])

            done = False
            while not done:

                # we want to make sure that the current path will not intersect with itself
                direction_chosen = False
                num_steps = random.randint(2, 4)

                while not direction_chosen:
                    # have a bias toward going straight
                    direction_index = random.randint(0, 1)
                    if direction_index == 2:
                        direction_index = random.randint(1, 2)
                    direction = directions[direction_index]

                    if orientation == "north" and direction == "left":
                        if cur_row - num_steps < x_min:
                            direction_chosen = True
                    elif orientation == "south" and direction == "right":
                        if cur_row + num_steps > x_max:
                            direction_chosen = True
                    elif orientation == "east" and direction == "left":
                        if cur_col + num_steps > y_max:
                            direction_chosen = True
                    elif orientation == "west" and direction == "right":
                        if cur_col - num_steps < y_min:
                            direction_chosen = True
                    else:
                        direction_chosen = True

                row_update = orientations[orientation][direction][0][0]
                col_update = orientations[orientation][direction][0][1]

                for _ in range(num_steps):
                    cur_row += row_update
                    cur_col += col_update

                    if cur_row > x_max:
                        x_max = cur_row
                    if cur_row < x_min:
                        x_min = cur_row
                    if cur_col > y_max:
                        y_max = cur_col
                    if cur_col < y_min:
                        y_min = cur_col

                    # the population center is on the edge of the map, so we don't want to add a path in this direction
                    if (
                        cur_row == -1
                        or cur_row == num_cols
                        or cur_col == -1
                        or cur_col == num_rows
                    ):
                        done = True
                        break

                    current_path.append([cur_row, cur_col])
                    if (
                        cur_row == 0
                        or cur_row == num_cols - 1
                        or cur_col == 0
                        or cur_col == num_rows - 1
                    ):
                        done = True
                        paths.append(current_path)
                        paths_to_pops[path_num] = [[pop_row, pop_col]]
                        path_num += 1
                        num_pop_paths_created += 1
                        break

                # update orientation
                orientation = orientations[orientation][direction][1]
    if save_map:
        save_map_info(num_rows, num_cols, percent_map_populated, populated_areas, paths, paths_to_pops)
    return populated_areas, np.array(paths, dtype=object), paths_to_pops

# populated_areas, paths, paths_to_pops = generate_map_info(10, 10, 5)

num_rows, num_cols, populated_areas, paths, paths_to_pops, percent_map_populated = load_map_info("./pyrorl_map_info/10_rows_10_cols_5_percent_map_populated_generation0")

example_world = FireWorld(num_rows, num_cols, populated_areas, paths, paths_to_pops)

print(example_world.state_space[4])
