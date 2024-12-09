from collections import defaultdict
from pathlib import Path
from pprint import pprint

from input_util import Coordinate, Matrix, matrix_to_string, parse_input_as_matrix


def is_alphanumeric(char: str) -> bool:
    return char.isalpha() or char.isdigit()


def algo(matrix: Matrix) -> tuple[int, int]:
    """We're going to create a mapping
    of the characters to their positions in the matrix."""

    num_rows = len(matrix)
    num_cols = len(matrix[0])
    antinode_locations_pt1: set[Coordinate] = set()
    antinode_locations_pt2: set[Coordinate] = set()

    antenna_frequency_to_position: dict[str, list[Coordinate]] = defaultdict(list)
    for row_idx, row in enumerate(matrix):
        for col_idx, _ in enumerate(row):
            matrix_val = matrix[row_idx][col_idx]
            if is_alphanumeric(matrix_val):
                antenna_frequency_to_position[matrix_val].append((row_idx, col_idx))

    # Now that we have the mapping, we can iterate through the mapping
    # and take every two positions and see if their antinodes are in the
    # matrix
    pprint(antenna_frequency_to_position)
    count_of_antinodes = 0
    matrix_copy = [row[:] for row in matrix]
    for key, positions in antenna_frequency_to_position.items():
        if len(positions) < 2:
            continue

        for idx, p1 in enumerate(positions):
            for p2 in positions[idx + 1 :]:
                # We can calculate the distance between the two positions
                # using the distance formula.
                # Then we can calculate the frequency using the speed of light
                # and the distance.
                # We can then return the frequency and the distance.
                run = p2[0] - p1[0]
                rise = p2[1] - p1[1]

                # We count these
                antinode_locations_pt2.add(p1)
                antinode_locations_pt2.add(p2)

                in_bounds_forward = True
                in_bounds_backward = True

                forward_point = p2
                backward_point = p1

                is_part1_forward = True
                is_part1_backward = True

                while in_bounds_forward:
                    # basically calculating a ray from the two points
                    potential_antinode = (forward_point[0] + run, forward_point[1] + rise)
                    if potential_antinode[1] < 0 or potential_antinode[1] >= num_cols:
                        in_bounds_forward = False
                        break

                    if potential_antinode[0] < 0 or potential_antinode[0] >= num_rows:
                        in_bounds_forward = False
                        break

                    if is_part1_forward and potential_antinode not in antinode_locations_pt1:
                        antinode_locations_pt1.add(potential_antinode)

                    if potential_antinode not in antinode_locations_pt2:
                        if matrix_copy[potential_antinode[0]][potential_antinode[1]] == ".":
                            matrix_copy[potential_antinode[0]][potential_antinode[1]] = "#"

                        antinode_locations_pt2.add(potential_antinode)

                    forward_point = potential_antinode
                    is_part1_forward = False

                while in_bounds_backward:
                    potential_antinode = (backward_point[0] - run, backward_point[1] - rise)

                    if potential_antinode[1] < 0 or potential_antinode[1] >= num_cols:
                        in_bounds_backward = False
                        break

                    if potential_antinode[0] < 0 or potential_antinode[0] >= num_rows:
                        in_bounds_backward = False
                        break

                    if is_part1_backward and potential_antinode not in antinode_locations_pt1:
                        antinode_locations_pt1.add(potential_antinode)

                    if potential_antinode not in antinode_locations_pt2:
                        if matrix_copy[potential_antinode[0]][potential_antinode[1]] == ".":
                            matrix_copy[potential_antinode[0]][potential_antinode[1]] = "#"
                        antinode_locations_pt2.add(potential_antinode)

                    is_part1_backward = False
                    backward_point = potential_antinode

                # print(f"Calculating antinode for {key} at {p1} and {p2}")
                # print(f"Distance between the two positions: {rise}, {run}")
                # print(f"Potential antinodes: {potential_antinode_1}, {potential_antinode_2}")

                # potential_antinode_1 = (p1[0] - run, p1[1] - rise)
                # potential_antinode_2 = (p2[0] + run, p2[1] + rise)

                # # pt1
                # for potential_antinode in [potential_antinode_1, potential_antinode_2]:
                #     if potential_antinode[0] < 0 or potential_antinode[0] >= num_rows:
                #         continue
                #     if potential_antinode[1] < 0 or potential_antinode[1] >= num_cols:
                #         continue

                #     if potential_antinode in antinode_locations:
                #         continue

                #     if matrix_copy[potential_antinode[0]][potential_antinode[1]] == ".":
                #         matrix_copy[potential_antinode[0]][potential_antinode[1]] = "#"

                #     antinode_locations.add(potential_antinode)
                #     count_of_antinodes += 1

    print(matrix_to_string(matrix_copy))
    return (len(antinode_locations_pt1), len(antinode_locations_pt2))


def soln(input_file: Path) -> tuple[int, int]:
    input_matrix = parse_input_as_matrix(input_file.read_text())

    pprint(input_matrix)
    num_antinodes, num_antinodes_with_resonance = algo(input_matrix)
    return (num_antinodes, num_antinodes_with_resonance)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day08.txt"

    print(soln(input_file))
    # time_solution("day07", soln, input_file)
