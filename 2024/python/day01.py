# ruff: noqa: E402
"""
solution:
seems like we're trying to get the distances between lists, and the suggestion
is that we should pair up the smallest number in the left list with the smallest
number in the right list, and so on. But... addition / subtraction is commutative
so it doesn't matter which number we pair up with which. So we can just sum the lists
and then subtract them.

Here's the example they give:
3 4
4 3
2 5
1 3
3 9
3 3

> The smallest number in the left list is 1, and the smallest number in the right list is 3. The distance between them is 2.
The second-smallest number in the left list is 2, and the second-smallest number in the right list is another 3. The distance between them is 1.
The third-smallest number in both lists is 3, so the distance between them is 0.
The next numbers to pair up are 3 and 4, a distance of 1.
The fifth-smallest numbers in each list are 3 and 5, a distance of 2.
Finally, the largest number in the left list is 4, while the largest number in the right list is 9; these are a distance 5 apart.
To find the total distance between the left list and the right list, add up the distances between all of the pairs you found. In the example above, this is 2 + 1 + 0 + 1 + 2 + 5, a total distance of 11!

But....
3+4+2+1+3+3 = 16
4+3+5+3+9+3 = 27
27 - 16 = 11

Ah ok but this doesn't totally work because we want the absolute value in there...

So i guess we do need to sort it?

First approach that got the right answer was sorting, that works.
Second approach which is better is using a heap.

Actually it's the same big 0 so maybe it's not as efficient?

So we can try to time it. Probably because of the Timsort python implementation....

But heap could be better for streamings solutions.
"""  # noqa: E501

example_str = """
3 4
4 3
2 5
1 3
3 9
3 3
"""

import heapq
from collections import defaultdict
from pathlib import Path

from timing_util import TimeUnit, TimingOptions, time_solution


# # Hm, do we really need to sort it?
def soln_easy(input_file: Path) -> tuple[int, int]:
    left: list[int] = []
    right: list[int] = []
    right_map = defaultdict(int)

    with open(input_file, "r") as f:
        for line in f:
            a, b = map(int, line.strip().split())
            left.append(a)
            right.append(b)
            right_map[b] += 1  # for part2
    left.sort()
    right.sort()
    list_distance_diff = 0
    list_similarity_score = 0
    for l, r in zip(left, right):
        list_distance_diff += abs(l - r)
        list_similarity_score += l * right_map.get(l, 0)
    return list_distance_diff, list_similarity_score


# better solution is using a minheap, but still kinda lame, I bet I can figure out a better way
def soln(input_file: Path) -> tuple[int, int]:
    left_heap: list[int] = []
    right_heap: list[int] = []
    right_map = defaultdict(int)

    with open(input_file, "r") as f:
        for line in f:
            a, b = map(int, line.strip().split())
            heapq.heappush(left_heap, a)
            heapq.heappush(right_heap, b)
            right_map[b] += 1  # for part2
    list_distance_diff = 0
    list_similarity_score = 0
    while left_heap:
        left_val = heapq.heappop(left_heap)
        right_val = heapq.heappop(right_heap)
        list_distance_diff += abs(left_val - right_val)
        list_similarity_score += left_val * right_map.get(left_val, 0)
    return list_distance_diff, list_similarity_score


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day01.txt"
    ans = soln(input_file)
    pt1_ans, pt2_ans = ans
    print(f"day01 solution (pt1): {pt1_ans}")
    print(f"day01 solution (pt2): {pt2_ans}")


def heap_solution(input_file: Path) -> tuple[int, int]:
    return soln(input_file)


def sort_solution(input_file: Path) -> tuple[int, int]:
    return soln_easy(input_file)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day01.txt"

    time_solution(
        "day01",
        soln_easy,
        input_file,
        method=TimingOptions.TIMEIT,
        unit=TimeUnit.MICROSECONDS,
        iterations=10,
    )

    # compare_functions(
    #     [
    #         ("Heap Solution", soln),
    #         ("Sort Solution", soln_easy),
    #     ],
    #     input_file,
    #     method=TimingOptions.TIMEIT,  # Options: perf_counter, timeit, average
    #     unit=TimeUnit.MILLISECONDS,  # Change to TimeUnit.NANOSECONDS or TimeUnit.SECONDS as needed
    #     iterations=10,  # Only relevant for "average"
    # )
