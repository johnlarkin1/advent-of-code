from functools import lru_cache
import math
from pathlib import Path

NUM_BLINKS = 75
MULTIPLE_FACTOR = 2024


def apply_rules_for_num_blinks(stone_list: list[int], num_blinks: int) -> list[int]:
    def transform_zero_to_one(stone: int) -> tuple[bool, list[int]]:
        if stone == 0:
            return True, [1]
        return False, [stone]

    def transform_even_num_digits(stone: int) -> tuple[bool, list[int]]:
        str_stone = str(stone)
        if len(str_stone) % 2 == 0:
            return True, [int(str_stone[: len(str_stone) // 2]), int(str_stone[len(str_stone) // 2 :])]
        return False, [stone]

    def transform_others(stone: str) -> tuple[bool, list[str]]:
        return True, [stone * 2024]

    rules = [
        transform_zero_to_one,
        transform_even_num_digits,
        transform_others,
    ]

    # for part 2 we can basically memoize the results
    # because we know we're going to do redundant work
    # for a given stone, and how many blinks are remaining
    # so instead of building the memo cache myself, i'm just going to use lru_cache
    @lru_cache(maxsize=None)
    def process_stone(stone: int, num_blinks: int) -> list[int]:
        if num_blinks == 0:
            return [stone]
        new_stone_list = []
        new_stones = apply_rules(stone)
        for new_stone in new_stones:
            new_stone_list.extend(process_stone(new_stone, num_blinks - 1))
        return new_stone_list

    result_stones = []
    for stone in stone_list:
        result_stones.extend(process_stone(stone, num_blinks))
    return result_stones


@lru_cache(maxsize=None)
def apply_rules(stone: int) -> list[int]:
    if stone == 0:
        return [1]
    digit_count = 1 if stone == 0 else int(math.log10(stone)) + 1
    if digit_count % 2 == 0:
        half_len = digit_count // 2
        factor = 10**half_len
        left = stone // factor
        right = stone % factor
        return [left, right]

    # Rule 3: others -> stone * 2024
    return [stone * MULTIPLE_FACTOR]


def apply_rules_for_num_blinks_just_count(stone_list: list[int], num_blinks: int) -> int:
    # Ok let's forget about even keeping track of the list and just count how
    # many stones are in each transformation
    @lru_cache(maxsize=None)
    def count_stones(stone: int, blinks: int) -> int:
        if blinks == 0:
            return 1
        new_stones = apply_rules(stone)
        return sum(count_stones(ns, blinks - 1) for ns in new_stones)

    # Sum the counts for all initial stones after num_blinks transformations
    return sum(count_stones(stone, num_blinks) for stone in stone_list)


def soln(input_file: Path) -> tuple[int, int]:
    num_stones_pt1 = 0
    num_stones_pt2 = 0

    input_str = input_file.read_text()
    stone_list = list(map(int, input_str.split(" ")))
    transformed_stones = apply_rules_for_num_blinks_just_count(stone_list, NUM_BLINKS)
    num_stones_pt2 = transformed_stones
    # num_stones_pt1 = len(transformed_stones)
    return (num_stones_pt1, num_stones_pt2)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day11_small.txt"
    input_file = curr_dir.parent / "inputs" / "day11.txt"
    print(soln(input_file))
