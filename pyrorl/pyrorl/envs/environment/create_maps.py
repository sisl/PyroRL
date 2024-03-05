from pickle import POP
import random
import numpy as np

FIRE_INDEX = 0
FUEL_INDEX = 1
POPULATED_INDEX = 2
EVACUATING_INDEX = 3
PATHS_INDEX = 4

"""
Notes: 
- generated paths can go through other populated areas
- add step bounds (range for number of steps taken in a direction)
- add num paths range as input paramter
"""
class TestMap:
    def __init__(self, num_rows, num_cols, percent_map_populated):
        self.state_space = np.zeros([5, num_rows, num_cols])
        self.num_rows = num_rows
        self.num_cols = num_cols

        if percent_map_populated > 100:
            raise Exception("Cannot have more than 100 percent of the map be populated!")

        self.paths_to_pops = {}

        num_populated_areas = int(num_rows*num_cols * percent_map_populated * 0.01)

        # randomly generate populated areas
        populated_areas = set()
        for _ in range(num_populated_areas):
            pop_row = random.randint(0,num_rows-1)
            pop_col = random.randint(0,num_cols-1)
            while (pop_row, pop_col) in populated_areas:
                pop_row = random.randint(0,num_rows-1)
                pop_col = random.randint(0,num_cols-1)
            populated_areas.add((pop_row,pop_col))
            self.state_space[POPULATED_INDEX,pop_row,pop_col] = 1
        self.populated_areas = np.array(list(populated_areas))


        orientations = {}
        orientations["north"] = {"left": [[0,-1],"west"], "right": [[0,1],"east"], "straight": [[-1,0],"north"]}
        orientations["south"] = {"left": [[0,1], "east"], "right": [[0,-1], "west"], "straight": [[1,0],"south"]}
        orientations["east"] = {"left": [[-1,0], "north"], "right": [[1,0],"south"], "straight": [[0,1], "east"]}
        orientations["west"] = {"left": [[1,0], "south"], "right": [[-1,0], "north"], "straight": [[0,-1], "west"]}

        directions = {1: "left", 2 : "right", 3: "straight"}

        self.paths = []

        # generate paths for each population center
        num_paths= np.random.normal(3,1,num_populated_areas).astype(int)
        # NOTe: MAKE SURE THAT num_paths IS NOT 0!!
        # num_paths = np.array([1,1,1,1,1])

        path_num = 0

        for i in range(len(self.populated_areas)):
            pop_row, pop_col = self.populated_areas[i]
        
            num_pop_paths_created = 0 # for cases where a path couldn't be made 
            while num_pop_paths_created < num_paths[i]:
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
                    num_steps = random.randint(2,4)

                    while not direction_chosen:
                        # have a bias toward going straight
                        direction_index = random.randint(1,2)
                        if direction_index == 2:
                            direction_index = random.randint(2,3)
                        direction = directions[direction_index]

                        if orientation == "north" and direction == "left":
                            if cur_row - num_steps < x_min:
                                direction_chosen = True
                        if orientation == "south" and direction == "right":
                            if cur_row + num_steps > x_max:
                                direction_chosen = True
                        if orientation == "east" and direction == "left":
                            if cur_col + num_steps > y_max:
                                direction_chosen = True
                        if orientation == "west" and direction == "right":
                            if cur_col - num_steps < y_min:
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
                        if cur_row == -1 or cur_row == self.num_cols or cur_col == -1 or cur_col == self.num_rows:
                            done = True
                            break

                        self.state_space[PATHS_INDEX, cur_row, cur_col] += 1
                        current_path.append([cur_row, cur_col])
                        if cur_row == 0 or cur_row == self.num_cols - 1 or cur_col == 0 or cur_col == self.num_rows - 1:
                            done = True
                            self.paths.append(current_path)
                            self.paths_to_pops[path_num] = [[pop_row, pop_col]]
                            path_num += 1
                            num_pop_paths_created += 1
                            break
                        
                    # update orientation
                    orientation = orientations[orientation][direction][1]



num_rows = 10
num_cols = 10

percent_map_populated = 5

map = TestMap(num_rows,num_cols, percent_map_populated)

print(map.state_space[POPULATED_INDEX])
print()
print(map.state_space[PATHS_INDEX])
"""
num_rows = 24
num_cols = 24
num_populated_areas = 5
map = TestMap(num_rows,num_cols, num_populated_areas)
print(map.state_space[POPULATED_INDEX])
print()
print(map.state_space[PATHS_INDEX])
print(map.paths)
print(map.paths_to_pops)
print(map.populated_areas)
"""

# def create_map(num_rows, num_cols, percent_map_populated):
#     if percent_map_populated > 100:
#         raise Exception("Cannot have more than 100 percent of the map be populated!")
    
#     orientations = {}
#     orientations["north"] = {"left": [[0,-1],"west"], "right": [[0,1],"east"], "straight": [[-1,0],"north"]}
#     orientations["south"] = {"left": [[0,1], "east"], "right": [[0,-1], "west"], "straight": [[1,0],"south"]}
#     orientations["east"] = {"left": [[-1,0], "north"], "right": [[1,0],"south"], "straight": [[0,1], "east"]}
#     orientations["west"] = {"left": [[1,0], "south"], "right": [[-1,0], "north"], "straight": [[0,-1], "west"]}
#     directions = {0: "left", 1: "right", 2: "straight"}
    
#     state_space = np.zeros([5, num_rows, num_cols])
#     paths_to_pops = {}
#     num_populated_areas = int(num_rows*num_cols * percent_map_populated * 0.01)
#     populated_areas, state_space = generate_pop_locations(num_rows, num_cols, num_populated_areas, state_space)
#     num_paths_array = np.random.normal(3,1,num_populated_areas).astype(int)
#     while 0 in num_paths_array:
#         num_paths_array = np.random.normal(3,1,num_populated_areas).astype(int)

#     path_num = 0
    

# def generate_pop_locations(num_rows, num_cols, num_populated_areas, state_space):
#     populated_areas = set()
#     for _ in range(num_populated_areas):
#         pop_row = random.randint(0,num_rows-1)
#         pop_col = random.randint(0,num_cols-1)
#         while (pop_row, pop_col) in populated_areas:
#             pop_row = random.randint(0,num_rows-1)
#             pop_col = random.randint(0,num_cols-1)
#         populated_areas.add((pop_row,pop_col))
#         state_space[POPULATED_INDEX,pop_row,pop_col] = 1
#     populated_areas = np.array(list(populated_areas))
#     return populated_areas, state_space