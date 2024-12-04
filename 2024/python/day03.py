import re
from pathlib import Path

from timing_util import TimeUnit, TimingOptions, compare_functions, time_solution


def extract_and_multiple_pt1_regex(entire_input: str) -> int:
    """
    Extracts all inputs like mul(X,Y) where X and Y are 1-3 digit integers and returns the sum of the products of X and Y.

    For example:
    xmul(2,4)%&mul[3,7]!@^do_not_mul(5,5)+mul(32,64]then(mul(11,8)mul(8,5))

    Only the four highlighted sections are real mul instructions. Adding up the result of each instruction produces 161 (2*4 + 5*5 + 11*8 + 8*5).
    """  # noqa: E501

    total = 0
    for match in re.finditer(r"mul\((\d{1,3}),(\d{1,3})\)", entire_input):
        x, y = map(int, match.groups())
        total += x * y
    return total


def extract_and_multiple_pt1_iter(entire_input: str) -> int:
    total = 0
    for i in range(len(entire_input) - 3):
        if entire_input[i : i + 3] == "mul":
            x_start = i + 4
            x_end = entire_input.find(",", x_start)
            maybe_x = entire_input[x_start:x_end]

            y_start = x_end + 1
            y_end = entire_input.find(")", y_start)
            maybe_y = entire_input[y_start:y_end]

            if maybe_x.isdigit() and maybe_y.isdigit():
                x = int(maybe_x)
                y = int(maybe_y)
                total += x * y

    return total


def extract_and_multiple_pt2_iter(entire_input: str) -> int:
    """
    Similar too the above, but now there are some new commands.

    The do() instruction enables future mul instructions.
    The don't() instruction disables future mul instructions.
    Only the most recent do() or don't() instruction applies. At the beginning of the program, mul instructions are enabled.

    For example:

    xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
    This corrupted memory is similar to the example from before, but this time the mul(5,5) and mul(11,8) instructions are disabled because there is a don't() instruction before them. The other mul instructions function normally, including the one at the end that gets re-enabled by a do() instruction.

    This time, the sum of the results is 48 (2*4 + 8*5).
    """  # noqa: E501

    are_we_live = True
    total = 0
    for i in range(len(entire_input) - 3):
        if entire_input[i : i + 3] == "do(":
            are_we_live = True
        elif entire_input[i : i + 3] == "don":
            are_we_live = False
        elif entire_input[i : i + 3] == "mul" and are_we_live:
            x_start = i + 4
            x_end = entire_input.find(",", x_start)
            maybe_x = entire_input[x_start:x_end]

            y_start = x_end + 1
            y_end = entire_input.find(")", y_start)
            maybe_y = entire_input[y_start:y_end]

            if maybe_x.isdigit() and maybe_y.isdigit():
                x = int(maybe_x)
                y = int(maybe_y)
                total += x * y

    return total


def extract_and_multiple_pt2_regex(entire_input: str) -> int:
    """
    Similar to the iterative version, but uses regex to handle
    the enabling and disabling logic for `mul` instructions.
    """
    total = 0
    are_we_live = True

    # Pattern to match `do()`, `don't()`, and `mul(X, Y)`
    instructions = re.finditer(r"(do\(\)|don't\(\)|mul\((\d{1,3}),(\d{1,3})\))", entire_input)

    for match in instructions:
        if match.group(0) == "do()":
            are_we_live = True
        elif match.group(0) == "don't()":
            are_we_live = False
        elif are_we_live and match.group(2) and match.group(3):
            x, y = map(int, (match.group(2), match.group(3)))
            total += x * y

    return total


def soln(input_file: Path) -> int:
    with open(input_file, "r") as f:
        entire_input = f.read()
    rez = extract_and_multiple_pt2_regex(entire_input)
    return rez


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day03.txt"
    time_solution(
        "day03",
        soln,
        input_file,
        method=TimingOptions.TIMEIT,
        unit=TimeUnit.MICROSECONDS,
        iterations=10,
    )

    with open(input_file, "r") as f:
        entire_input = f.read()

    compare_functions(
        [
            ("pt1 regex", extract_and_multiple_pt1_regex),
            ("pt1 iter", extract_and_multiple_pt1_iter),
            ("pt2 regex", extract_and_multiple_pt2_regex),
            ("pt2 iter", extract_and_multiple_pt2_iter),
        ],
        entire_input,
        method=TimingOptions.AVERAGE,
        unit=TimeUnit.MICROSECONDS,
        iterations=10,
    )
