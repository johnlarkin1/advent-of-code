import itertools
from functools import lru_cache
from pathlib import Path

from timing_util import time_solution

OPERATIONS = ["+", "*", "||"]


def left_to_right_eval(nums: list[int], ops: tuple[str, ...], target: int) -> int:
    """
    We can evaluate the expression left to right.
    """
    result = nums[0]
    for idx, num in enumerate(nums[1:]):
        if ops[idx] == "+":
            result += num
        elif ops[idx] == "*":
            result *= num
        elif ops[idx] == "||":
            result = int(str(result) + str(num))

        if result > target:
            return result

    return result


def can_find_equalizer(target: int, nums: list[int]) -> bool:
    """Operators are + and *
    We are assuming operator precedence is left to right
    not PEMDAS fine.

    One initial check is if adding all the numbers
    together is equal to the target, then we can return True.
    If it's greater than the target, then we can return False because
    we know that's the minimum we could have.

    We can also check if multiplying all the numbers together is equal
    to the target.
    If it's greater than the target, then we can return False
    because we know that's the minimum we could have.

    ===

    Yeah so this isn't the case because like think about
    8 1 1 1 1 1 1
    the product is actually lower than the sum... so our checks aren't exactly valid.
    """

    # lowest_possible_value = sum(nums)
    # largest_possible_value = math.prod(nums)
    # if lowest_possible_value == target:
    #     return True

    # if lowest_possible_value > target:
    #     return False

    # if largest_possible_value == target:
    #     return True

    # if largest_possible_value < target:
    #     return False

    # We need to try all combinations of + and * between the numbers
    # For n numbers, we need n-1 operators
    # We can use itertools.product to generate all combinations

    # I really should optimize this.... but.... it's kinda the easiest way
    # we could do some better more sophisticated early checking
    # where we could check if the sum of the numbers is less than the target
    # and the product of the numbers is less than the target
    num_operators_needed = len(nums) - 1
    for ops in itertools.product(OPERATIONS, repeat=num_operators_needed):
        if left_to_right_eval(nums, ops, target) == target:
            return True
    return False


@lru_cache(None)
def can_find_equalizer_cache_helper(target: int, nums: list[int]) -> bool:
    num_operators_needed = len(nums) - 1
    for ops in itertools.product(OPERATIONS, repeat=num_operators_needed):
        if left_to_right_eval(nums, ops, target) == target:
            return True
    return False


def can_find_equalizer_cache(target: int, nums: list[int]) -> bool:
    return can_find_equalizer_cache_helper(target, tuple(nums))


def soln(input_file: Path) -> tuple[int, int]:
    """
    We can analyze each line, and basically just see if
    we can hit the targets with the numbers given.

    We're then just trying to sum the valid targets.
    """
    sum_of_valid_targets = 0
    with open(input_file, "r") as f:
        for line in f:
            cleansed_line = line.strip()
            target_str, nums_str = cleansed_line.split(":")
            target = int(target_str)
            nums = list(map(int, nums_str.split()))
            if can_find_equalizer_cache(target, nums):
                sum_of_valid_targets += target

    return sum_of_valid_targets, 0


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day07.txt"
    # input_file = curr_dir.parent / "inputs" / "day07_small.txt"
    # print(soln(input_file))
    time_solution("day07", soln, input_file)
