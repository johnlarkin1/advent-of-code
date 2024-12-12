from pathlib import Path
from pprint import pprint
from typing import Literal, TypedDict

from input_util import Coordinate, Matrix, is_in_bounds, parse_input_as_matrix

DirKeyType = Literal["up", "down", "left", "right"]
DirType = tuple[int, int]
DIRECTIONS: dict[DirKeyType, DirType] = {
    "up": (-1, 0),
    "left": (0, -1),
    "down": (1, 0),
    "right": (0, 1),
}
NEXT_DIRECTION: dict[DirKeyType, DirKeyType] = {
    "right": "down",
    "down": "left",
    "left": "up",
    "up": "right",
}


class Region(TypedDict):
    area: int
    perimeter: int
    sides: int


def calculate_sides(region_edges: set[Coordinate]) -> int:
    visited_edges = set()
    sides = 0
    curr_point = min(region_edges, key=lambda loc: (loc[0], loc[1]))
    start_point = curr_point
    curr_dir = "right"

    while True:
        curr_dir_vec = DIRECTIONS[curr_dir]
        next_point = (curr_point[0] + curr_dir_vec[0], curr_point[1] + curr_dir_vec[1])
        edge = (curr_point, next_point)

        if edge not in visited_edges and next_point in region_edges:
            visited_edges.add(edge)
            curr_point = next_point
        else:
            # Change direction if we hit a dead end or revisit
            curr_dir = NEXT_DIRECTION[curr_dir]
            sides += 1

        if curr_point == start_point and curr_dir == "right":
            break

    return sides


def get_region_info(
    matrix: Matrix, start_loc: Coordinate, visited_farm_locations: set[Coordinate], seen_plant_types: set[str]
) -> Region:
    # initialize side count to 4 because we're starting at a corner
    region_info: Region = {"area": 1, "perimeter": 0, "sides": 0}
    curr_val = matrix[start_loc[0]][start_loc[1]]
    visited_farm_locations.add(start_loc)
    seen_plant_types.add(curr_val)

    # Ok I think for part 2, we need to keep track of the direction we're going
    # and see when that changes to denote
    region_edges: set[Coordinate] = set()
    explore_stack: list[Coordinate] = [start_loc]
    while explore_stack:
        curr_loc = explore_stack.pop()
        for _, dir_vec in DIRECTIONS.items():
            neighbor = (curr_loc[0] + dir_vec[0], curr_loc[1] + dir_vec[1])
            if not is_in_bounds(matrix, neighbor):
                region_info["perimeter"] += 1
                region_edges.add(curr_loc)
                continue

            new_val = matrix[neighbor[0]][neighbor[1]]
            if neighbor in visited_farm_locations:
                if new_val != curr_val:
                    region_edges.add(curr_loc)
                    region_info["perimeter"] += 1
                continue

            if new_val == curr_val:
                region_info["area"] += 1
                visited_farm_locations.add(neighbor)
                explore_stack.append(neighbor)
            else:
                region_edges.add(curr_loc)
                region_info["perimeter"] += 1

    region_info["sides"] = calculate_sides(region_edges)
    return region_info


def explore_farm(matrix: Matrix) -> list[tuple[str, Region]]:
    regions: list[tuple[str, Region]] = []
    visited_farm_locations: set[Coordinate] = set()
    seen_plant_types: set[str] = set()
    for row_idx, row in enumerate(matrix):
        for col_idx, cell in enumerate(row):
            if (row_idx, col_idx) in visited_farm_locations:
                # We've already seen this one, so skip it
                continue

            # We haven't seen this one yet, so let's explore it
            region_info = get_region_info(matrix, (row_idx, col_idx), visited_farm_locations, seen_plant_types)
            regions.append((cell, region_info))
            seen_plant_types.add(cell)
    return regions


def soln(input_file: Path, debug: bool = True) -> tuple[int, int]:
    pt1_ans = 0
    pt2_ans = 0
    matrix = parse_input_as_matrix(input_file.read_text(), "str")
    plant_type_to_region_info = explore_farm(matrix)
    if debug:
        pprint(plant_type_to_region_info)
    for region_key_and_info in plant_type_to_region_info:
        region_key, region_info = region_key_and_info
        perim_price = region_info["area"] * region_info["perimeter"]
        side_price = region_info["area"] * region_info["sides"]
        pt1_ans += perim_price
        pt2_ans += side_price

    return (pt1_ans, pt2_ans)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day12_very_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day12_small_pt2.txt"
    # input_file = curr_dir.parent / "inputs" / "day12_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day12.txt"
    print(soln(input_file))
