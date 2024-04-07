"""
Unit tests for each of the functions in create_map_info.py
"""

import numpy as np
from pyrorl.map_helpers.create_map_info import (
    generate_map_info,
    MAP_DIRECTORY,
    load_map_info,
)
from pyrorl.envs.environment.environment import FireWorld, PATHS_INDEX, POPULATED_INDEX
import os
import shutil


def test_path_structure():
    """
    Make sure that paths are continuous and reach the end of the map.
    """
    num_rows = 200
    num_cols = 200
    num_populated_areas = 20
    _, paths, _ = generate_map_info(
        num_rows, num_cols, num_populated_areas, save_map=False
    )
    for path in paths:
        previous_cell = None
        for cell in path:
            if previous_cell is None:
                previous_cell = cell
                continue
            assert (
                previous_cell[0] == cell[0] - 1
                or previous_cell[0] == cell[0] + 1
                or previous_cell[1] == cell[1] - 1
                or previous_cell[1] == cell[1] + 1
            )
            previous_cell = cell
        assert (
            previous_cell[0] == 0
            or previous_cell[1] == 0
            or previous_cell[0] == num_rows - 1
            or previous_cell[1] == num_cols - 1
        )


def test_paths_not_fold():
    """
    Make sure that paths do not intersect with themselves.
    """
    num_rows = 1000
    num_cols = 1000
    num_populated_areas = 1
    for _ in range(100):
        populated_areas, paths, paths_to_pops = generate_map_info(
            num_rows,
            num_cols,
            num_populated_areas,
            save_map=False,
            num_paths_mean=1,
            num_paths_stdev=0,
        )
        test_world = FireWorld(
            num_rows, num_cols, populated_areas, paths, paths_to_pops
        )
        test_world.state_space[PATHS_INDEX][
            test_world.state_space[PATHS_INDEX] == 1
        ] = 0
        assert np.sum(test_world.state_space[PATHS_INDEX]) == 0


def test_path_each_area():
    """
    Make sure that each populated area has at least one path.
    """
    for i in range(5000):
        num_rows = 50
        num_cols = 50
        num_populated_areas = 10
        _, _, paths_to_pops = generate_map_info(
            num_rows, num_cols, num_populated_areas, save_map=False
        )
        pops_seen = set()
        for path in paths_to_pops:
            for pop_cell in paths_to_pops[path]:
                pops_seen.add(tuple(pop_cell))
        assert len(pops_seen) == num_populated_areas


def test_each_path_has_pop():
    """
    Make sure that each path has at least one populated area.
    """
    num_rows = 50
    num_cols = 50
    num_populated_areas = 10
    _, _, paths_to_pops = generate_map_info(
        num_rows, num_cols, num_populated_areas, save_map=False
    )
    for path in paths_to_pops:
        assert len(paths_to_pops[path]) != 0


def test_map_loading_and_saving():
    """
    Make sure that loading and saving a map works properly.
    """
    num_rows = 10
    num_cols = 10
    num_populated_areas = 10
    populated_areas, paths, paths_to_pops = generate_map_info(
        num_rows, num_cols, num_populated_areas
    )
    original_fireworld = FireWorld(
        num_rows, num_cols, populated_areas, paths, paths_to_pops
    )
    map_info_root = os.path.join(os.getcwd(), MAP_DIRECTORY)
    current_map_directory = max(
        os.listdir(map_info_root),
        key=lambda f: os.path.getctime(os.path.join(map_info_root, f)),
    )
    map_info_path = os.path.join(map_info_root, current_map_directory)
    (
        loaded_num_rows,
        loaded_num_cols,
        loaded_populated_areas,
        loaded_paths,
        loaded_paths_to_pops,
        loaded_num_populated_areas,
    ) = load_map_info(map_info_path)
    shutil.rmtree(map_info_path)
    if len(os.listdir(map_info_root)) == 0:
        shutil.rmtree(map_info_root)
    loaded_fireworld = FireWorld(
        loaded_num_rows,
        loaded_num_cols,
        loaded_populated_areas,
        loaded_paths,
        loaded_paths_to_pops,
    )

    assert num_rows == loaded_num_rows
    assert num_cols == loaded_num_cols
    assert num_populated_areas == loaded_num_populated_areas
    assert np.equal(
        original_fireworld.state_space[POPULATED_INDEX],
        loaded_fireworld.state_space[POPULATED_INDEX],
    ).all()
    assert np.equal(
        original_fireworld.state_space[PATHS_INDEX],
        loaded_fireworld.state_space[PATHS_INDEX],
    ).all()
