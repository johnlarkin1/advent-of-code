from pathlib import Path
from typing import Literal

from input_util import Matrix, parse_input_as_matrix

DirKeyType = Literal["up", "down", "left", "right"]
DirType = tuple[int, int]
Coordinate = tuple[int, int]

STARTING_VAL = "0"
PRE_TARGET_VAL = "8"
TARGET_VAL = "9"
DIRECTIONS: dict[DirKeyType, DirType] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


def format_path(matrix: Matrix, path: list[Coordinate]) -> str:
    """Format a path showing both coordinates and values in a readable way."""
    steps = []
    for coord in path:
        value = matrix[coord[0]][coord[1]]
        steps.append(f"({coord[0]},{coord[1]})[{value}]")
    return " -> ".join(steps)


def visualize_matrix_path(matrix: Matrix, path: list[Coordinate]) -> str:
    """Create a visual representation of the path in the matrix."""
    # Create a copy of the matrix with dots for better visualization
    visual_matrix = [[str(cell) for cell in row] for row in matrix]

    # Add path markers
    for idx, coord in enumerate(path):
        visual_matrix[coord[0]][coord[1]] = f"*{visual_matrix[coord[0]][coord[1]]}"

    # Format the matrix as a string
    return "\n".join(" ".join(str(cell).rjust(3)) for cell in visual_matrix)


def find_starting_locations(matrix) -> list[Coordinate]:
    starting_locs: list[Coordinate] = []
    for row_idx, row in enumerate(matrix):
        for col_idx, cell in enumerate(row):
            if cell == STARTING_VAL:
                starting_locs.append((row_idx, col_idx))
    return starting_locs


def is_in_bounds(matrix: Matrix, loc: Coordinate) -> bool:
    return loc[0] >= 0 and loc[0] < len(matrix) and loc[1] >= 0 and loc[1] < len(matrix[0])


def can_find_target_from_loc(matrix: Matrix, loc: Coordinate) -> bool:
    return matrix[loc[0]][loc[1]] == TARGET_VAL


def dfs_explore(
    matrix: Matrix,
    starting_loc: Coordinate,
    visited: set[Coordinate],
    target_locs: set[Coordinate],
    debug_path: list[Coordinate],
) -> tuple[int, int]:
    if starting_loc in visited:
        # we are in a cycle somehow, or we've already visited this location
        return 0, 0

    visited.add(starting_loc)
    debug_path.append(starting_loc)

    curr_loc = starting_loc
    curr_val = matrix[starting_loc[0]][starting_loc[1]]
    total_paths = 0

    for _, direction_vec in DIRECTIONS.items():
        next_loc = (curr_loc[0] + direction_vec[0], curr_loc[1] + direction_vec[1])
        if is_in_bounds(matrix, next_loc):
            next_val = matrix[next_loc[0]][next_loc[1]]

            if next_val == TARGET_VAL and curr_val == PRE_TARGET_VAL:
                total_paths += 1
                target_locs.add(next_loc)
                continue

            if next_val == ".":
                continue

            if int(next_val) == int(curr_val) + 1:
                total_paths += dfs_explore(matrix, next_loc, visited, target_locs, debug_path)[0]

    debug_path.pop()
    visited.remove(starting_loc)
    return len(target_locs), total_paths


def soln(input_file: Path) -> tuple[int, int]:
    matrix = parse_input_as_matrix(input_file.read_text(), "str")
    starting_locs = find_starting_locations(matrix)
    sum_trailhead_scores = 0
    sum_trailhead_rating = 0
    for starting_loc in starting_locs:
        visited = set()
        target_locs = set()
        trailhead_score, trailhead_rating = dfs_explore(matrix, starting_loc, visited, target_locs, [])
        sum_trailhead_scores += trailhead_score
        sum_trailhead_rating += trailhead_rating
    return (sum_trailhead_scores, sum_trailhead_rating)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day10_true_small.txt"
    input_file = curr_dir.parent / "inputs" / "day10.txt"
    print(soln(input_file))
