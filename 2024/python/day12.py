from pathlib import Path
from pprint import pprint
from typing import Literal, TypedDict

from input_util import Coordinate, Matrix, is_in_bounds, parse_input_as_matrix

DirKeyType = Literal["up", "down", "left", "right"]
DirType = tuple[int, int]
EdgeType = tuple[Coordinate, DirKeyType]

DIRECTIONS: dict[DirKeyType, DirType] = {
    "up": (-1, 0),
    "left": (0, -1),
    "down": (1, 0),
    "right": (0, 1),
}
TOP_WALL_DIR_TO_NEXT_LOC_DIR: dict[DirKeyType, DirKeyType] = {
    "up": "right",
    "down": "left",
    "right": "down",
    "left": "up",
}
BOTTOM_WALL_DIR_TO_NEXT_LOC_DIR: dict[DirKeyType, DirKeyType] = {
    "down": "right",
    "left": "down",
}

WALL_LOC_TO_DIR: dict[DirKeyType, DirKeyType] = {
    "up": "right",
    "right": "down",
    "down": "left",
    "left": "up",
}


class Region(TypedDict):
    area: int
    perimeter: int
    sides: int


def rotate_direction_clockwise(d: DirKeyType) -> DirKeyType:
    if d == "up":
        return "right"
    elif d == "right":
        return "down"
    elif d == "down":
        return "left"
    elif d == "left":
        return "up"


def walk_wall(curr_edge: EdgeType, region_edges: set[EdgeType], visited_edges: set[EdgeType]) -> int:
    """
    Ok this is just a huge pain in the ass and I can optimize it later, but have
    struggled too long with the whole like directional and up and down bit
    compared to just moving along a rail basically.
    _______
    ^ this is fine
    x -> ... -> x
    _______
    ^ but counting this one for nested regions was fucking annoying
    """
    sides = 1

    # we do know that we're at the top left most, so
    # we should always progress top -> bottom
    # we shoudl always progress left -> right
    while True:
        curr_loc, wall_loc = curr_edge
        visited_edges.add(curr_edge)
        region_edges.discard(curr_edge)

        if wall_loc == "up" or wall_loc == "down":
            next_loc = (curr_loc[0], curr_loc[1] + 1)
            next_edge = (next_loc, wall_loc)
            if next_edge in region_edges:
                curr_edge = next_edge
            else:
                break
        else:
            next_loc = (curr_loc[0] + 1, curr_loc[1])
            next_edge = (next_loc, wall_loc)
            if next_edge in region_edges:
                curr_edge = next_edge
            else:
                break

    return sides


def calculate_sides_with_directions(region_key: str, region_edges: set[tuple[Coordinate, DirKeyType]]) -> int:
    """
    So now that we have the edges and the directions of the walls here's what we're going to do
    """
    visited_edges = set()
    region_sides = 0

    print(f"Exploring region: {region_key}")
    while region_edges:
        start_edge = min(region_edges, key=lambda edge: (edge[0][0], edge[0][1], edge[1]))
        curr_edge = start_edge
        wall_side_count = walk_wall(curr_edge, region_edges, visited_edges)
        region_sides += wall_side_count
    return region_sides


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
    # ok and yeah for the edges, we should keep track of where the kinda wall was
    region_edges: set[tuple[Coordinate, DirKeyType]] = set()
    explore_stack: list[Coordinate] = [start_loc]
    while explore_stack:
        curr_loc = explore_stack.pop()
        for dir_key, dir_vec in DIRECTIONS.items():
            neighbor = (curr_loc[0] + dir_vec[0], curr_loc[1] + dir_vec[1])
            if not is_in_bounds(matrix, neighbor):
                region_info["perimeter"] += 1
                region_edges.add((curr_loc, dir_key))
                continue

            new_val = matrix[neighbor[0]][neighbor[1]]
            if neighbor in visited_farm_locations:
                if new_val != curr_val:
                    region_edges.add((curr_loc, dir_key))
                    region_info["perimeter"] += 1
                continue

            if new_val == curr_val:
                region_info["area"] += 1
                visited_farm_locations.add(neighbor)
                explore_stack.append(neighbor)
            else:
                region_edges.add((curr_loc, dir_key))
                region_info["perimeter"] += 1

    print("Region edges:")
    pprint(region_edges)

    region_info["sides"] = calculate_sides_with_directions(curr_val, region_edges)
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
    # input_file = curr_dir.parent / "inputs" / "day12_very_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day12_small_pt2.txt"
    # input_file = curr_dir.parent / "inputs" / "day12_small.txt"
    input_file = curr_dir.parent / "inputs" / "day12.txt"
    print(soln(input_file))
