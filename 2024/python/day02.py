from pathlib import Path

from input_util import Location
from timing_util import TimeUnit, TimingOptions, time_solution


def is_report_safe(report_line: list[int]) -> bool:
    """
    Determines if a report is safe or unsafe.

    Only safe if:
    * The levels are either all increasing or all decreasing.
    * Any two adjacent levels differ by at least one and at most three.

    e.g.
    7 6 4 2 1: Safe because the levels are all decreasing by 1 or 2.
    1 2 7 8 9: Unsafe because 2 7 is an increase of 5.
    9 7 6 2 1: Unsafe because 6 2 is a decrease of 4.
    1 3 2 4 5: Unsafe because 1 3 is increasing but 3 2 is decreasing.
    8 6 4 4 1: Unsafe because 4 4 is neither an increase or a decrease.
    1 3 6 7 9: Safe because the levels are all increasing by 1, 2, or 3.
    """

    starting_level = report_line[0]
    is_increasing = False
    is_decreasing = False
    min_tol = 1
    max_tol = 3
    if starting_level > report_line[1]:
        is_decreasing = True
    elif starting_level < report_line[1]:
        is_increasing = True
    else:
        # if any are equal, it's not increasing or decreasing
        return False

    if is_increasing or is_decreasing:
        for i in range(1, len(report_line)):
            curr_val = report_line[i]
            prev_val = report_line[i - 1]
            if is_increasing and curr_val < prev_val:
                return False
            elif is_decreasing and curr_val > prev_val:
                return False
            if abs(curr_val - prev_val) > max_tol or abs(curr_val - prev_val) < min_tol:
                return False
    return True


def is_report_safe_with_one_allowed(report_line: list[int]) -> bool:
    """
    Now, the same rules apply as before, except if removing a single level from an unsafe report would make it safe, the report instead counts as safe.

    More of the above example's reports are now safe:

    7 6 4 2 1: Safe without removing any level.
    1 2 7 8 9: Unsafe regardless of which level is removed.
    9 7 6 2 1: Unsafe regardless of which level is removed.
    1 3 2 4 5: Safe by removing the second level, 3.
    8 6 4 4 1: Safe by removing the third level, 4.
    1 3 6 7 9: Safe without removing any level.
    """  # noqa: E501

    # if it's safe normally, we can just return true
    if is_report_safe(report_line):
        return True

    # otherwise, let's look for one bad apple
    for i in range(len(report_line)):
        if is_report_safe(report_line[:i] + report_line[i + 1 :]):
            return True

    return False


def soln(input_file: Path) -> Location:
    safe_reports = 0
    safe_reports_with_one_allowed = 0
    with open(input_file, "r") as f:
        for line in f:
            report_line = list(map(int, line.strip().split()))
            if is_report_safe(report_line):
                safe_reports += 1
            if is_report_safe_with_one_allowed(report_line):
                safe_reports_with_one_allowed += 1
    return safe_reports, safe_reports_with_one_allowed


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day02.txt"
    time_solution(
        "day02",
        soln,
        input_file,
        method=TimingOptions.TIMEIT,
        unit=TimeUnit.MICROSECONDS,
        iterations=10,
    )
