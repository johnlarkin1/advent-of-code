"""
Ok cool so the question is how many of these towel combinations are possible?

And basically this is a screaming memoization and DP programming

So i'm thinking it's probably best if we do some type of building this up
yeah this is definitely DP because it's like just repeated subproblems

So we're going to use recursion and we're going to use lru_cache probably aaaaand
yeah I think that's it
"""

from functools import lru_cache
from pathlib import Path

IS_TEST = False


def parse_input(input_file: Path) -> tuple[set[str], list[str]]:
    """Returns our building blocks for the towels,
    and then the desired designs"""
    with open(input_file) as f:
        building_blocks = set()
        designs = []
        for line in f.readlines():
            line = line.strip()
            if line:
                if "," in line:
                    building_blocks.update(block.strip() for block in line.split(","))
                else:
                    designs.append(line)
    return building_blocks, designs


@lru_cache(None)
def can_make_design(design: str, patterns: tuple[str, ...]) -> tuple[bool, int]:
    @lru_cache(None)
    def dfs(index: int) -> int:
        if index == len(design):
            return 1

        total_ways = 0
        for pattern in patterns:
            if design.startswith(pattern, index):
                total_ways += dfs(index + len(pattern))
        return total_ways

    num_ways_to_make = dfs(0)
    return num_ways_to_make > 0, num_ways_to_make


def soln(input_file: Path) -> tuple[int, int]:
    num_possible_combinations_pt1 = 0
    total_num_ways_to_make_everything_pt2 = 0
    building_blocks, designs = parse_input(input_file)
    # print(f"Building blocks: {building_blocks}")
    # print(f"Designs: {designs}")

    building_blocks_tuple = tuple(building_blocks)
    for design in designs:
        can_make, soln_cnt = can_make_design(design, building_blocks_tuple)
        print(f"Design: {design} can make: {can_make} with {soln_cnt} ways")
        if can_make:
            num_possible_combinations_pt1 += 1
        total_num_ways_to_make_everything_pt2 += soln_cnt

    return num_possible_combinations_pt1, total_num_ways_to_make_everything_pt2


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file: Path
    if IS_TEST:
        input_file = curr_dir.parent / "inputs" / "day19_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day19.txt"

    print(soln(input_file))
