from collections import defaultdict, deque
from pathlib import Path
from pprint import PrettyPrinter
from typing import Literal

from input_util import Coordinate, Matrix, MatrixStr, matrix_to_string, parse_input_as_matrix

printer = PrettyPrinter(width=200)

ROBOT_MARKER = "@"
DIRECTION_TYPE = Literal["<", "^", ">", "v"]
DIRECTION_MAP_TO_VEC: dict[DIRECTION_TYPE, Coordinate] = {
    "<": (0, -1),
    "^": (-1, 0),
    ">": (0, 1),
    "v": (1, 0),
}

BOX_TO_CORRESPONDING_TYPE = {"[": "]", "]": "["}


def find_robot_starting_coordinate(robot_map: Matrix) -> Coordinate:
    for row_idx, row in enumerate(robot_map):
        for col_idx, cell in enumerate(row):
            if cell in ROBOT_MARKER:
                return (row_idx, col_idx)
    return (-1, -1)


def move_robot_with_instruction_pt1(
    robot_map: Matrix, robot_loc: Coordinate, instruction: DIRECTION_TYPE
) -> Coordinate:
    x, y = robot_loc
    dir_vec = DIRECTION_MAP_TO_VEC[instruction]
    next_loc = (x + dir_vec[0], y + dir_vec[1])
    next_loc_val = robot_map[next_loc[0]][next_loc[1]]
    if next_loc_val == "#":
        return robot_loc

    if next_loc_val == ".":
        robot_map[next_loc[0]][next_loc[1]] = ROBOT_MARKER
        robot_new_loc = next_loc
        robot_map[x][y] = "."
        return robot_new_loc

    num_consecutive_boxes = 0
    next_check_loc = next_loc
    if robot_map[next_check_loc[0]][next_check_loc[1]] == "O":
        while robot_map[next_check_loc[0]][next_check_loc[1]] == "O":
            next_check_loc = (next_check_loc[0] + dir_vec[0], next_check_loc[1] + dir_vec[1])
            num_consecutive_boxes += 1

        final_check_space = next_check_loc
        if robot_map[final_check_space[0]][final_check_space[1]] == "#":
            return robot_loc

        if robot_map[final_check_space[0]][final_check_space[1]] == ".":
            # we need to move all the boxes to this location
            robot_map[final_check_space[0]][final_check_space[1]] = "O"
            robot_map[next_loc[0]][next_loc[1]] = ROBOT_MARKER
            robot_map[x][y] = "."
            return next_loc

    return robot_loc


def push_up(robot_map: MatrixStr, robot_loc: Coordinate) -> Coordinate:
    robot_r, robot_c = robot_loc
    start_r = robot_r - 1
    start_c = robot_c
    start = (start_r, start_c)

    queue = deque([start])
    visited = set([start])
    to_shift = defaultdict(set)
    blocked = False

    while queue:
        r, c = queue.pop()

        # Stop if blocked by a wall
        if robot_map[r][c] == "#":
            blocked = True
            break

        match robot_map[r][c]:
            case "[":
                to_shift[r].update([c, c + 1])
                if (r - 1, c) not in visited:
                    visited.add((r - 1, c))
                    queue.append((r - 1, c))
                if (r - 1, c + 1) not in visited:
                    visited.add((r - 1, c + 1))
                    queue.append((r - 1, c + 1))
            case "]":
                to_shift[r].update([c, c - 1])
                if (r - 1, c) not in visited:
                    visited.add((r - 1, c))
                    queue.append((r - 1, c))
                if (r - 1, c - 1) not in visited:
                    visited.add((r - 1, c - 1))
                    queue.append((r - 1, c - 1))
            case ".":
                to_shift[r].add(c)

    if not blocked:
        # Start from top down given we're moving up,
        # so we know that top is going to be free
        for row in sorted(to_shift.keys(), reverse=False):
            for col in sorted(to_shift[row]):
                # robot_map[row][col] = robot_map[row + 1][col]
                if (row + 1 in to_shift) and (col in to_shift[row + 1]):
                    # Shift the value up
                    robot_map[row][col] = robot_map[row + 1][col]
                else:
                    # Set to empty
                    robot_map[row][col] = "."

        # Move the robot up
        robot_map[robot_r - 1][robot_c] = "@"
        robot_map[robot_r][robot_c] = "."
        robot_loc = (robot_r - 1, robot_c)

    return robot_loc


def push_down(robot_map: MatrixStr, robot_loc: Coordinate) -> Coordinate:
    robot_r, robot_c = robot_loc
    start_r = robot_r + 1
    start_c = robot_c
    start = (start_r, start_c)

    queue = deque([start])
    visited = set([start])
    to_shift = defaultdict(set)
    blocked = False

    while queue:
        r, c = queue.pop()
        if r >= len(robot_map) or robot_map[r][c] == "#":
            blocked = True
            break

        match robot_map[r][c]:
            case "[":
                to_shift[r].update([c, c + 1])
                if (r + 1, c) not in visited:
                    visited.add((r + 1, c))
                    queue.append((r + 1, c))
                if (r + 1, c + 1) not in visited:
                    visited.add((r + 1, c + 1))
                    queue.append((r + 1, c + 1))
            case "]":
                to_shift[r].update([c, c - 1])
                if (r + 1, c) not in visited:
                    visited.add((r + 1, c))
                    queue.append((r + 1, c))
                if (r + 1, c - 1) not in visited:
                    visited.add((r + 1, c - 1))
                    queue.append((r + 1, c - 1))
            case ".":
                to_shift[r].add(c)

    if not blocked:
        for row in sorted(to_shift.keys(), reverse=True):
            for col in sorted(to_shift[row]):
                if (row - 1 in to_shift) and (col in to_shift[row - 1]):
                    robot_map[row][col] = robot_map[row - 1][col]
                else:
                    robot_map[row][col] = "."

        robot_map[robot_r + 1][robot_c] = "@"
        robot_map[robot_r][robot_c] = "."
        robot_loc = (robot_r + 1, robot_c)

    return robot_loc


def move_robot_with_instruction_pt2(
    robot_map: Matrix, robot_loc: Coordinate, instruction: DIRECTION_TYPE
) -> Coordinate:
    x, y = robot_loc
    dir_vec = DIRECTION_MAP_TO_VEC[instruction]
    next_loc = (x + dir_vec[0], y + dir_vec[1])
    next_loc_val = robot_map[next_loc[0]][next_loc[1]]

    if next_loc_val == "#":
        return robot_loc

    if next_loc_val == ".":
        robot_map[next_loc[0]][next_loc[1]] = ROBOT_MARKER
        robot_new_loc = next_loc
        robot_map[x][y] = "."
        return robot_new_loc

    # Ok so now we know we're basically hitting a box
    # We should really think about moving boxes as a single unit
    # so I want to basically always grab two elements at a time
    # and then move them together
    #
    # So thinking about this more, I think we need to check both spaces
    # in the direction we're pushing. If one of them is blocked, then we're
    # stuck.
    #
    # Actually, it's a bit easier because if we're moving left or right,
    # we know the box takes up that row so we should be fine.
    if instruction in ["<", ">"]:
        num_locations_to_move = 0
        tmp_next_loc = next_loc
        tmp_next_loc_val = robot_map[tmp_next_loc[0]][tmp_next_loc[1]]
        replacement_locations: list[tuple[Coordinate, str]] = []
        while tmp_next_loc_val == "[" or tmp_next_loc_val == "]":
            num_locations_to_move += 1
            tmp_next_loc = (tmp_next_loc[0] + dir_vec[0], tmp_next_loc[1] + dir_vec[1])
            replacement_locations.append((tmp_next_loc, tmp_next_loc_val))
            tmp_next_loc_val = robot_map[tmp_next_loc[0]][tmp_next_loc[1]]
        if tmp_next_loc_val == "#":
            # we can't move any of these boxes
            return robot_loc

        if tmp_next_loc_val == ".":
            for replacement_loc, replacement_val in replacement_locations:
                robot_map[replacement_loc[0]][replacement_loc[1]] = replacement_val

            # reset the originals
            robot_map[next_loc[0]][next_loc[1]] = ROBOT_MARKER
            robot_map[x][y] = "."
            return next_loc

    # TODO: @larkin
    # implement up and down instructions

    if instruction == "^":
        # So we need to basically
        robot_loc = push_up(robot_map, robot_loc)

    if instruction == "v":
        robot_loc = push_down(robot_map, robot_loc)

    return robot_loc


def parse_input(input_file: Path) -> tuple[Matrix, list[DIRECTION_TYPE]]:
    map_lines: list[str] = []
    robot_instructions: list[DIRECTION_TYPE] = []
    with open(input_file, "r") as f:
        for line in f:
            if "#" in line:
                map_lines.append(line)
            else:
                robot_instructions.extend(list(line.strip()))  # type: ignore

    robot_map = parse_input_as_matrix("\n".join(map_lines), "str")
    return (robot_map, robot_instructions)


def compute_box_gps_coordinate_score(robot_map: Matrix) -> int:
    total_score = 0
    for row_idx, row in enumerate(robot_map):
        for col_idx, cell in enumerate(row):
            if cell == "O":
                total_score += 100 * row_idx + col_idx

            if cell == "[":
                total_score += 100 * row_idx + col_idx
    return total_score


# part 2
def transform_map(starting_robot_map: Matrix) -> MatrixStr:
    new_matrix: list[list[str]] = []
    for row in starting_robot_map:
        new_row = []
        for cell in row:
            if cell == "#":
                new_row.extend(["#", "#"])
            elif cell == "O":
                new_row.extend(["[", "]"])
            elif cell == ".":
                new_row.extend([".", "."])
            elif cell == "@":
                new_row.extend(["@", "."])
        new_matrix.append(new_row)
    return new_matrix


def soln(input_file: Path) -> tuple[int, int]:
    gps_coordinate_score_pt1 = 0
    gps_coordinate_score_pt2 = 0

    robot_map, movements = parse_input(input_file)
    translated_robot_map = transform_map(robot_map)
    robot_starting_loc = find_robot_starting_coordinate(robot_map)

    print("Part 1")
    robot_curr_loc = robot_starting_loc
    for _idx, movement in enumerate(movements):
        robot_curr_loc = move_robot_with_instruction_pt1(robot_map, robot_curr_loc, movement)
    gps_coordinate_score_pt1 = compute_box_gps_coordinate_score(robot_map)

    print("Part 2")
    robot_curr_loc = find_robot_starting_coordinate(translated_robot_map)
    for idx, movement in enumerate(movements):
        print(f"Step: {idx} with movement: {movement} with robot loc: {robot_curr_loc}")
        robot_curr_loc = move_robot_with_instruction_pt2(translated_robot_map, robot_curr_loc, movement)

    print(matrix_to_string(translated_robot_map))
    gps_coordinate_score_pt2 = compute_box_gps_coordinate_score(translated_robot_map)
    return (gps_coordinate_score_pt1, gps_coordinate_score_pt2)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day15_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day15_med.txt"
    input_file = curr_dir.parent / "inputs" / "day15.txt"
    # input_file = curr_dir.parent / "inputs" / "day15_pt2_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day15_pt2_med.txt"
    # printer.pprint(string_repr)
    # input_file = curr_dir.parent / "inputs" / "day15.txt"
    print(soln(input_file))
