"""Jesus what a prompt.

Took me like 15 minutes to understand what was even happening.

Ok so basically a couple layers of misdirection.

I'm pressing buttons which is controlling one robot, which then controls another, which then finally enters a code on a door.

So this is a great part:

```
Were you to choose this sequence of button presses, here are all of the buttons that would be pressed on your directional keypad, the two robots' directional keypads, and the numeric keypad:

<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A
v<<A>>^A<A>AvA<^AA>A<vAAA>^A
<A^A>^^AvvvA
029A
```

Ok i think I'm getting the idea. It's like multiple BFS (given we want shortest)
but like kinda in a nested manner and there's some layer of reconstruction / DP here.

And we basically have to backtrack... Or do we?

So we kinda have like three connected graphs...
Our keypad, robot #1 keypad, robot #2 keypad, and true numeric keypad.

-----
So let's have our algoirthm basically be this:
1. assume all machines are starting at position A
2. on the numeric keypad, we're going to do a BFS to find the shortest path to the target door code
3. for each keystroke in that path, we're going to do a BFS on the robot directional keypad
   to figure out how to get that efficiently.
4. we're going to do that one more time for the robot's robot's directional keypad
5. we're going to save that path
6. we'll do this for all target door codes
7. we'll sum up the complexities
8. we'll be done
"""  # noqa: E501

import heapq
import re
from collections import defaultdict, deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypedDict

DirectionType = Literal["UP", "DOWN", "LEFT", "RIGHT"]
MovementType = Literal["^", "v", "<", ">"]


@dataclass
class Move:
    target: str
    direction: DirectionType
    command: MovementType


@dataclass
class State:
    position: str
    last_direction: str | None
    path: str

    def __lt__(self, other):
        # Required for heapq, but we'll use the cost in the priority queue tuple
        return False


ARE_TESTING = False

SMALL_ANSWER: dict[str, str] = {
    "029A": "<vA<AA>>^AvAA<^A>A<v<A>>^AvA^A<vA>^A<v<A>^A>AAvA^A<v<A>A>^AAAvA<^A>A",
    "980A": "<v<A>>^AAAvA^A<vA<AA>>^AvAA<^A>A<v<A>A>^AAAvA<^A>A<vA>^A<A>A",
    "179A": "<v<A>>^A<vA<A>>^AAvAA<^A>A<v<A>>^AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
    "456A": "<v<A>>^AA<vA<A>>^AAvAA<^A>A<vA>^A<A>A<vA>^A<A>A<v<A>A>^AAvA<^A>A",
    "379A": "<v<A>>^AvA^A<vA<AA>>^AAvA<^A>AAvA^A<vA>^AA<A>A<v<A>A>^AAAvA<^A>A",
}

# This graph is going to encode this:
# +---+---+---+
# | 7 | 8 | 9 |
# +---+---+---+
# | 4 | 5 | 6 |
# +---+---+---+
# | 1 | 2 | 3 |
# +---+---+---+
#     | 0 | A |
#     +---+---+
# NUMERIC_KEYPAD_GRAPH: dict[str, list[str]] = {
#     "7": ["4", "8"],
#     "8": ["7", "5", "9"],
#     "9": ["8", "6"],
#     "4": ["1", "7", "5"],
#     "5": ["2", "4", "6", "8"],
#     "6": ["3", "5", "9"],
#     "1": ["4", "2"],
#     "2": ["0", "1", "3", "5"],
#     "3": ["2", "6", "A"],
#     "0": ["2", "A"],
#     "A": ["3", "0"],
# }
NUMERIC_KEYPAD_GRAPH: dict[str, list[Move]] = {
    "7": [Move(target="4", direction="DOWN", command="v"), Move(target="8", direction="RIGHT", command=">")],
    "8": [
        Move(target="7", direction="LEFT", command="<"),
        Move(target="5", direction="DOWN", command="v"),
        Move(target="9", direction="RIGHT", command=">"),
    ],
    "9": [Move(target="8", direction="LEFT", command="<"), Move(target="6", direction="DOWN", command="v")],
    "4": [
        Move(target="1", direction="DOWN", command="v"),
        Move(target="7", direction="UP", command="^"),
        Move(target="5", direction="RIGHT", command=">"),
    ],
    "5": [
        Move(target="2", direction="DOWN", command="v"),
        Move(target="4", direction="LEFT", command="<"),
        Move(target="6", direction="RIGHT", command=">"),
        Move(target="8", direction="UP", command="^"),
    ],
    "6": [
        Move(target="3", direction="DOWN", command="v"),
        Move(target="5", direction="LEFT", command="<"),
        Move(target="9", direction="UP", command="^"),
    ],
    "1": [Move(target="4", direction="UP", command="^"), Move(target="2", direction="RIGHT", command=">")],
    "2": [
        Move(target="1", direction="LEFT", command="<"),
        Move(target="0", direction="DOWN", command="v"),
        Move(target="3", direction="RIGHT", command=">"),
        Move(target="5", direction="UP", command="^"),
    ],
    "3": [
        Move(target="2", direction="LEFT", command="<"),
        Move(target="6", direction="UP", command="^"),
        Move(target="A", direction="DOWN", command="v"),
    ],
    "0": [Move(target="2", direction="UP", command="^"), Move(target="A", direction="RIGHT", command=">")],
    "A": [Move(target="3", direction="UP", command="^"), Move(target="0", direction="LEFT", command="<")],
}


NUMERIC_KEYPAD_LOCATIONS: dict[str, tuple[int, int]] = {
    "7": (0, 0),
    "8": (0, 1),
    "9": (0, 2),
    "4": (1, 0),
    "5": (1, 1),
    "6": (1, 2),
    "1": (2, 0),
    "2": (2, 1),
    "3": (2, 2),
    "0": (3, 1),
    "A": (3, 2),
}


# This graph is going to encode this:
#     +---+---+
#     | ^ | A |
# +---+---+---+
# | < | v | > |
# +---+---+---+
# DIRECTIONAL_KEYPAD_GRAPH: dict[str, list[str]] = {
#     "^": ["v", "A"],
#     "A": ["^", ">"],
#     "<": ["v"],
#     "v": ["<", "^", ">"],
#     ">": ["A", "v", "^"],
# }

DIRECTIONAL_KEYPAD_GRAPH = {
    "^": [Move(target="v", direction="DOWN", command="v"), Move(target="A", direction="RIGHT", command=">")],
    "A": [Move(target="^", direction="LEFT", command="<"), Move(target=">", direction="DOWN", command="v")],
    "<": [Move(target="v", direction="RIGHT", command=">")],
    "v": [
        Move(target="<", direction="LEFT", command="<"),
        Move(target=">", direction="RIGHT", command=">"),
        Move(target="^", direction="UP", command="^"),
    ],
    ">": [
        Move(target="v", direction="LEFT", command="<"),
        Move(target="A", direction="UP", command="^"),
    ],
}
DIRECTIONAL_KEYPAD_LOCATIONS = {
    "^": (0, 1),
    "A": (0, 2),
    "<": (1, 0),
    "v": (1, 1),
    ">": (1, 2),
}


class PadInfoDict(TypedDict):
    coords: dict[str, tuple[int, int]]
    gap: str


def get_pad_info(is_directional: bool = False) -> PadInfoDict:
    """
    Create a pad info structure similar to the JavaScript version
    """
    if is_directional:
        locations = DIRECTIONAL_KEYPAD_LOCATIONS
        gap = "0,0"  # Top-left corner is the gap in directional pad
    else:
        locations = NUMERIC_KEYPAD_LOCATIONS
        gap = "3,0"  # Bottom-left corner is the gap in numeric pad

    return {"coords": locations, "gap": gap}


NUMERIC_PAD = get_pad_info(is_directional=False)
DIRECTIONAL_PAD = get_pad_info(is_directional=True)


def get_alphanumeric_value(code: str) -> int:
    match = re.match(r"(\d+)", code)
    return int(match.group(1)) if match else 0


def parse_target_door_codes(input_file: Path) -> list[str]:
    with open(input_file) as f:
        lines = f.readlines()
        return [line.strip() for line in lines]


def calculate_complexities(code_to_shortest_path: dict[str, str]) -> int:
    total_complexities = 0
    for code, path in code_to_shortest_path.items():
        print(f"code: {code} len(path): {len(path)}")
        total_complexities += len(path) * get_alphanumeric_value(code)
    return total_complexities


def calculate_compexities_pt2(code_to_shortest_path: dict[str, int]) -> int:
    total_complexities = 0
    for code, length in code_to_shortest_path.items():
        total_complexities += length * get_alphanumeric_value(code)
    return total_complexities


def find_path_to_target(
    start_position: str,
    target_position: str,
    graph: dict[str, list[Move]],
) -> str:
    # BFS
    bfs_queue = deque([(start_position, "")])
    visited = set()
    while bfs_queue:
        curr_position, path = bfs_queue.popleft()
        if curr_position == target_position:
            return path

        if curr_position in visited:
            continue

        visited.add(curr_position)
        for move in graph[curr_position]:
            bfs_queue.append((move.target, path + move.command))
    return ""


def find_path_to_target_with_direction_cost(
    start_position: str,
    target_position: str,
    graph: dict[str, list[Move]],
) -> str:
    # (position, lastDir) -> best cost so far
    best = {}
    # (cost, position, lastDir, path)
    pq = []
    # Initialize
    start_state = (0, start_position, None, "")
    heapq.heappush(pq, start_state)
    best[(start_position, None)] = 0

    while pq:
        cost_so_far, curr_pos, last_dir, path = heapq.heappop(pq)

        # If we've arrived at the target, done:
        if curr_pos == target_position:
            return path

        # If we've found a better cost for this state since we popped from pq, skip it
        if best.get((curr_pos, last_dir), float("inf")) < cost_so_far:
            continue

        # Explore neighbors
        for move in graph[curr_pos]:  # move.command is ^, v, <, or >
            new_pos = move.target
            dir = move.command  # The direction we want to press
            # Cost depends on whether we switched directions
            add_cost = 1 if (dir == last_dir) else 2
            new_cost = cost_so_far + add_cost
            new_path = path + dir

            if new_cost < best.get((new_pos, dir), float("inf")):
                best[(new_pos, dir)] = new_cost
                heapq.heappush(pq, (new_cost, new_pos, dir, new_path))

    return ""  # no path found


def compute_robot_steps(
    numeric_keypad_cache: dict,
    start_position: str,
    target_position: str,
    graph: dict[str, list[Move]],
) -> str:
    if (start_position, target_position) in numeric_keypad_cache:
        return numeric_keypad_cache[(start_position, target_position)]
    path = find_path_to_target_with_direction_cost(start_position, target_position, graph)
    numeric_keypad_cache[(start_position, target_position)] = path
    return path


def modified_bfs_explore(target_door_codes: list[str], debug: bool = False) -> dict[str, str]:
    """
    Damn absolute bummer.

    I don't think this is going to work even with the idea that we want to prefer going
    the same direction and minimize turning.

    So I think we kinda need to use dijkstras or consider the search space as the whole
    puzzle rather than from level to level.
    """
    # these two caches are going to be going from starting position and desired target
    # to the shortest path.
    # we're basically memoizing the shortest path from a starting position to a target
    numeric_keypad_cache: dict[tuple[str, str], str] = {}
    directional_keypad_cache: dict[tuple[str, str], str] = {}

    # again levels go:
    # our keypad -> robot keypad (robot1) -> robot's robot keypad (robot2) -> numeric keypad
    robot_one_keypad_position = "A"
    robot_two_keypad_position = "A"
    numeric_keypad_position = "A"
    # this will hold our answers basically
    should_break = False
    code_mapping: dict[str, str] = {}
    for target_door_code in target_door_codes:
        if should_break:
            break
        top_level_level_movements = ""
        for target_char in target_door_code:
            if should_break:
                break
            # STEP: numeric keypad to robot 2
            door_to_robot_two_steps = compute_robot_steps(
                numeric_keypad_cache,
                numeric_keypad_position,
                target_char,
                NUMERIC_KEYPAD_GRAPH,
            )
            door_to_robot_two_steps += "A"
            # we've now updated our position to the target_char
            numeric_keypad_position = target_char

            # we have gotten the path from the numeric keypad to robot2
            # now we need to get the path from robot2 to robot1
            # we're going to use the robot_keypad_cache to store this
            # STEP: robot2 -> robot1
            robot_two_to_robot_one_steps = ""
            for robot_two_char in door_to_robot_two_steps:
                partial_rez = compute_robot_steps(
                    directional_keypad_cache,
                    robot_two_keypad_position,
                    robot_two_char,
                    DIRECTIONAL_KEYPAD_GRAPH,
                )
                robot_two_to_robot_one_steps += partial_rez
                if debug:
                    print(
                        f"for keypad position: {robot_two_keypad_position} and "
                        f"target: {robot_two_char} we got {partial_rez} (full path: {robot_two_to_robot_one_steps})"
                    )
                robot_two_to_robot_one_steps += "A"
                robot_two_keypad_position = robot_two_char

            # STEP: robot1 -> our keypad
            for robot_one_char in robot_two_to_robot_one_steps:
                top_level_level_movements += compute_robot_steps(
                    directional_keypad_cache,
                    robot_one_keypad_position,
                    robot_one_char,
                    DIRECTIONAL_KEYPAD_GRAPH,
                )
                top_level_level_movements += "A"
                robot_one_keypad_position = robot_one_char

            if debug:
                print(f"Top-Level Directional Keypad: {top_level_level_movements}")
                print(f"Robot 1 Directional Keypad: {robot_two_to_robot_one_steps}")
                print(f"Robot 2 Directional Keypad: {door_to_robot_two_steps}")
                print(f"Numeric Keypad: {target_door_code}")
                print(f"Target Char: {target_char}")
                # should_break = True
        code_mapping[target_door_code] = top_level_level_movements
    return code_mapping


@lru_cache(maxsize=None)
def shortest_path(key1: str, key2: str, is_numeric: bool) -> str:
    """
    Find shortest path between two keys, considering gaps.

    This follows the same logic as the JavaScript version but with our graph structure:
    1. Calculate vertical and horizontal movements needed
    2. Choose order of movements that avoids gaps
    3. Always append 'A' at the end

    This logic is basically ripped straight from here:
    * https://observablehq.com/@jwolondon/advent-of-code-2024-day-21
    basically just replacing my shortest path logic with a way more imperative approach
    """
    pad = NUMERIC_PAD if is_numeric else DIRECTIONAL_PAD
    # Get coordinates
    r1, c1 = pad["coords"][key1]
    r2, c2 = pad["coords"][key2]

    # Calculate required movements
    ud = "v" * (r2 - r1) if r2 > r1 else "^" * (r1 - r2)
    lr = ">" * (c2 - c1) if c2 > c1 else "<" * (c1 - c2)

    # Case 1: Moving right and safe to move vertically first
    if c2 > c1 and f"{r2},{c1}" != pad["gap"]:
        return f"{ud}{lr}A"

    # Case 2: Safe to move horizontally first
    if f"{r1},{c2}" != pad["gap"]:
        return f"{lr}{ud}A"

    # Case 3: Must be safe to move vertically first
    return f"{ud}{lr}A"


def compute_sequence(code: str, debug: bool = False) -> str:
    """
    Compute the full sequence for a given code.
    """

    # Start positions
    robot_one_pos = "A"
    robot_two_pos = "A"
    numeric_pos = "A"

    final_sequence = ""

    for target_char in code:
        # Get numeric keypad to robot 2 sequence
        door_to_robot_sequence = shortest_path(numeric_pos, target_char, is_numeric=True)
        numeric_pos = target_char

        # Get robot 2 to robot 1 sequence
        robot_two_sequence = ""
        for char in door_to_robot_sequence:
            partial = shortest_path(robot_two_pos, char, False)
            robot_two_sequence += partial
            robot_two_pos = char

        # Get robot 1 to our keypad sequence
        for char in robot_two_sequence:
            partial = shortest_path(robot_one_pos, char, False)
            final_sequence += partial
            robot_one_pos = char

        if debug:
            print(f"Target: {target_char}")
            print(f"Door to Robot 2: {door_to_robot_sequence}")
            print(f"Robot 2 to Robot 1: {robot_two_sequence}")
            print(f"Current Sequence: {final_sequence}")
            print("---")

    return final_sequence


# def compute_sequence_pt2(code: str, num_robots: int = 25, debug: bool = False) -> str:
#     # Initialize positions
#     numeric_pos = "A"
#     robot_positions = {f"R{i}": "A" for i in range(num_robots)}

#     final_sequence = ""

#     for target_char in code:
#         # step 1: move from numeric to first robot
#         door_to_robot_sequence = shortest_path(numeric_pos, target_char, is_numeric=True)
#         numeric_pos = target_char

#         # Get robot 2 to robot 1 sequence
#         current_sequence = door_to_robot_sequence
#         for robot_id in range(1, num_robots + 1):
#             current_robot_key = f"R{robot_id}"
#             robot_starting_pos = robot_positions[current_robot_key]

#             new_sequence = ""
#             for char in current_sequence:
#                 partial = shortest_path(robot_starting_pos, char, is_numeric=False)
#                 new_sequence += partial
#                 robot_starting_pos = char

#             robot_positions[current_robot_key] = robot_starting_pos
#             current_sequence = new_sequence

#         final_sequence += current_sequence

#     return final_sequence


def get_sequences_for_pad(seq: str, is_numeric: bool = False) -> list[str]:
    current_pos = "A"
    sequences = []

    for char in seq:
        path = shortest_path(current_pos, char, is_numeric)
        if path:
            sequences.append(path)
        current_pos = char

    return sequences


def add_to_freq_table(freq_table: dict[str, int], seq: str, count: int = 1) -> None:
    freq_table[seq] = freq_table.get(seq, 0) + count


def get_sequence_counts(seq: str) -> dict[str, int]:
    """Get frequency table of subsequences for directional pad"""
    freq_table = defaultdict(int)
    sequences = get_sequences_for_pad(seq, is_numeric=False)

    for subsequence in sequences:
        add_to_freq_table(freq_table, subsequence)

    return freq_table


def calculate_complexity_part2(codes: list[str], num_dir_robots: int = 25) -> dict[str, int]:
    """
    Calculate complexity using frequency counting approach for Part 2.

    Instead of generating full sequences, we:
    1. Start with numeric keypad sequences
    2. For each robot level, compute frequency table of subsequences
    3. Scale frequencies by previous level's frequencies
    4. Sum up final complexity using frequencies

    This algorithm was brought to you by https://observablehq.com/@jwolondon/advent-of-code-2024-day-21
    """
    initial_tables = []
    for code in codes:
        freq_table = defaultdict(int)
        sequences = get_sequences_for_pad(code, is_numeric=True)
        sequence = "".join(sequences)
        freq_table[sequence] = 1
        initial_tables.append(freq_table)

    frequency_tables = initial_tables
    for _ in range(num_dir_robots):
        new_tables = []
        for freq_table in frequency_tables:
            sub_freq_table = defaultdict(int)
            for seq, freq in freq_table.items():
                subseq_counts = get_sequence_counts(seq)
                for subseq, subfreq in subseq_counts.items():
                    sub_freq_table[subseq] += subfreq * freq

            new_tables.append(sub_freq_table)
        frequency_tables = new_tables

    code_to_complexity: dict[str, int] = {}
    for freq_table, code in zip(frequency_tables, codes):
        complexity = sum(len(seq) * freq for seq, freq in freq_table.items())
        code_to_complexity[code] = complexity

    return code_to_complexity


# ok - we're going to take a different approach and just calculate the direct route not really
# using DFS or Dijkstra's or A* and instead we're just going to proceduraly compute the best
# route as straight forward lines
def compute_main_robot_step_length(target_door_codes: list[str], debug: bool = False) -> dict[str, str]:
    return {code: compute_sequence(code, debug) for code in target_door_codes}


def compute_main_robot_step_length_pt2(target_door_codes: list[str], debug: bool = False) -> dict[str, int]:
    return calculate_complexity_part2(target_door_codes)


def soln(input_file: Path) -> tuple[int, int]:
    target_door_codes = parse_target_door_codes(input_file)
    # top_level_movements = modified_bfs_explore(target_door_codes, debug=False)
    top_level_movements = compute_main_robot_step_length(target_door_codes, debug=False)
    # print("Mine:")
    # print(top_level_movements)
    pt1_score = calculate_complexities(top_level_movements)
    # print("compared to")
    # print(SMALL_ANSWER)
    # print(f"score: {calculate_complexities(SMALL_ANSWER)}")

    # part 2
    top_level_movements = compute_main_robot_step_length_pt2(target_door_codes, debug=False)
    # print("Mine:")
    # print(top_level_movements)
    pt2_score = calculate_compexities_pt2(top_level_movements)
    return pt1_score, pt2_score


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if ARE_TESTING:
        input_file = curr_dir.parent / "inputs" / "day21_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day21.txt"
    print(soln(input_file))
