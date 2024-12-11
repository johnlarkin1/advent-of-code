"""
Woof this is for sure the hardest one yet. A noticeable increase in hardness fwiw.

Ok so here's my thinking. We need to check for:
* horizontal
* vertical
* diagonal
* backwards
* overlapping (?) not sure what this means

My thinking is we can just parse this as a matrix and then iterate through.
"""

import sys
from pathlib import Path

from input_util import Matrix, parse_input_as_matrix
from timing_util import TimeUnit, TimingOptions, time_solution

TARGET = "XMAS"
TARGET_PT2 = "MAS"

TARGET_REVERSE = TARGET[::-1]
TARGET_PT2_REVERSE = TARGET_PT2[::-1]

LEN_TARGET = len(TARGET)
LEN_TARGET_PT2 = len(TARGET_PT2)

TEST_MODE = False


def check_xmas_horizontal_fwd(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> bool:
    curr_value = matrix[curr_row_idx][curr_col_idx]
    if curr_value != "X":
        return False
    return "".join(matrix[curr_row_idx][curr_col_idx : curr_col_idx + LEN_TARGET]) == TARGET


def check_xmas_horizontal_bck(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> bool:
    return "".join(matrix[curr_row_idx][curr_col_idx : curr_col_idx + LEN_TARGET]) == TARGET_REVERSE


def check_xmas_vertical_fwd(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> bool:
    vertical_chars = [matrix[curr_row_idx + i][curr_col_idx] for i in range(LEN_TARGET)]
    return "".join(vertical_chars) == TARGET


def check_xmas_vertical_bck(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> bool:
    vertical_chars = [matrix[curr_row_idx + i][curr_col_idx] for i in range(LEN_TARGET)]
    return "".join(vertical_chars) == TARGET_REVERSE


def count_xmas_horizontal(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> int:
    if curr_row_idx >= len(matrix) or curr_col_idx + LEN_TARGET > len(matrix[0]):
        return 0

    curr_value = matrix[curr_row_idx][curr_col_idx]
    if curr_value != "X" and curr_value != "S":
        return 0

    horizontal_chars = "".join(matrix[curr_row_idx][curr_col_idx : curr_col_idx + LEN_TARGET])
    xmas_count = 0
    if horizontal_chars == TARGET:
        xmas_count += 1
    if horizontal_chars == TARGET_REVERSE:
        xmas_count += 1
    return xmas_count


def count_xmas_vertical(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> int:
    if curr_row_idx + LEN_TARGET > len(matrix) or curr_col_idx >= len(matrix[0]):
        return 0

    curr_value = matrix[curr_row_idx][curr_col_idx]
    if curr_value != "X" and curr_value != "S":
        return 0

    vertical_chars = "".join([matrix[curr_row_idx + i][curr_col_idx] for i in range(LEN_TARGET)])
    xmas_count = 0
    if vertical_chars == TARGET:
        xmas_count += 1
    if vertical_chars == TARGET_REVERSE:
        xmas_count += 1
    return xmas_count


def check_xmas_diagonal(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> int:
    xmas_count = 0
    # forward
    if curr_row_idx + LEN_TARGET <= len(matrix) and curr_col_idx + LEN_TARGET <= len(matrix[0]):
        diagonal_chars = "".join([matrix[curr_row_idx + i][curr_col_idx + i] for i in range(LEN_TARGET)])
        if diagonal_chars == TARGET or diagonal_chars == TARGET_REVERSE:
            xmas_count += 1

    # backward
    if curr_row_idx + LEN_TARGET <= len(matrix) and curr_col_idx - (LEN_TARGET - 1) >= 0:
        diagonal_chars = "".join([matrix[curr_row_idx + i][curr_col_idx - i] for i in range(LEN_TARGET)])
        if diagonal_chars == TARGET or diagonal_chars == TARGET_REVERSE:
            xmas_count += 1
    return xmas_count


def check_x_mas_x_shape(curr_row_idx: int, curr_col_idx: int, matrix: Matrix) -> int:
    xmas_xshape_count = 0
    # let's only check around the center so we'll only do this if we're currently at an A
    # because MAS written forwards and backwards has the A at the center

    curr_val = matrix[curr_row_idx][curr_col_idx]
    if curr_val != "A":
        return 0

    # now we check for the
    # M.S
    # .A.
    # M.S
    # shape

    # bounds check
    if not (
        curr_row_idx - 1 >= 0
        and curr_row_idx + 1 < len(matrix)
        and curr_col_idx - 1 >= 0
        and curr_col_idx + 1 < len(matrix[0])
    ):
        return 0

    # check one diagonal
    should_proceed = False
    top_left_to_bottom_right_diag = (
        matrix[curr_row_idx - 1][curr_col_idx - 1]
        + matrix[curr_row_idx][curr_col_idx]
        + matrix[curr_row_idx + 1][curr_col_idx + 1]
    )
    if top_left_to_bottom_right_diag == TARGET_PT2 or top_left_to_bottom_right_diag == TARGET_PT2_REVERSE:
        should_proceed = True

    if should_proceed:
        # check top_right_to_bottom_left_diag
        top_right_to_bottom_left_diag = (
            matrix[curr_row_idx - 1][curr_col_idx + 1]
            + matrix[curr_row_idx][curr_col_idx]
            + matrix[curr_row_idx + 1][curr_col_idx - 1]
        )
        if top_right_to_bottom_left_diag == TARGET_PT2 or top_right_to_bottom_left_diag == TARGET_PT2_REVERSE:
            xmas_xshape_count += 1
    return xmas_xshape_count


def soln(input_file: Path) -> tuple[int, int]:
    with open(input_file, "r") as f:
        input_str = f.read()
    matrix = parse_input_as_matrix(input_str, "str")
    total_xmas_count = 0
    total_xmas_xshape_count = 0
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            total_xmas_count += count_xmas_horizontal(i, j, matrix)
            total_xmas_count += count_xmas_vertical(i, j, matrix)
            total_xmas_count += check_xmas_diagonal(i, j, matrix)
            total_xmas_xshape_count += check_x_mas_x_shape(i, j, matrix)

    print("total_xmas_count:", total_xmas_count)
    print("total_xmas_xshape_count:", total_xmas_xshape_count)
    return total_xmas_count, total_xmas_xshape_count


if __name__ == "__main__":
    if TEST_MODE:
        test_matrix = [
            ["X", "M", "A", "S"],
            ["S", "A", "M", "X"],
            ["X", ".", ".", "."],
            ["M", ".", ".", "."],
            ["A", ".", ".", "."],
            ["S", ".", ".", "."],
            ["S", ".", ".", "."],
            ["A", ".", ".", "."],
            ["M", ".", ".", "."],
            ["X", ".", ".", "."],
        ]
        rez = check_xmas_horizontal_fwd(0, 0, test_matrix)
        print("test mode rez:", rez)
        rez = check_xmas_horizontal_bck(1, 0, test_matrix)
        print("test mode rez:", rez)

        rez = check_xmas_vertical_fwd(2, 0, test_matrix)
        print("test mode rez:", rez)
        rez = check_xmas_vertical_bck(6, 0, test_matrix)
        print("test mode rez:", rez)
        sys.exit(0)

    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day04.txt"

    time_solution(
        "day04",
        soln,
        input_file,
        method=TimingOptions.AVERAGE,
        unit=TimeUnit.MILLISECONDS,
        iterations=1,
    )
