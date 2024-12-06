"""
hm ok this doesn't seem that bad. basically just walking the guard through the map...

---

ok yeah this - being pt2 - seems like a bit of a bear....

we're trying to figure out where the *many* single points where
we could add a blocker and we could trap the guard in a loop

maybe it's not as bad as i think it is?
we have the visited locations, so... we can just use
that after the fact and then see if there are any basically squares
that we could create in that pattern right? Because then we would basically
have a loop.

Ah ok ok wait but maybe we need a bit more information.

I think we should keep track of everywhere where the
guard has hit a blocker or a wall. And then we can
just see if we can create squares out of that pattern.

Actually.... hm yeah it seems like just going off the full visited set
is going to be the best. that gives us a more holistic view of the
map.
"""

from pathlib import Path
from typing import Literal

GuardDirType = Literal["^", "v", "<", ">"]
LocationType = tuple[int, int]

BLOCKER = "#"

# direction -> (row, col)
GUARD_NEXT_POSITIONS: dict[GuardDirType, LocationType] = {
    "^": (-1, 0),
    "v": (1, 0),
    "<": (0, -1),
    ">": (0, 1),
}


def parse_input_as_matrix(input_str: str) -> list[list[str]]:
    return [list(line) for line in input_str.split("\n") if line]


def find_guard_starting_loc(matrix: list[list[str]]) -> tuple[LocationType, GuardDirType]:
    for row_idx, row in enumerate(matrix):
        for col_idx, cell in enumerate(row):
            if cell in GUARD_NEXT_POSITIONS:
                return (row_idx, col_idx), cell

    return (-1, -1), "<"


def turn_guard(curr_dir: GuardDirType) -> GuardDirType:
    if curr_dir == "^":
        return ">"
    if curr_dir == "v":
        return "<"
    if curr_dir == "<":
        return "^"
    if curr_dir == ">":
        return "v"


def advance_guard(curr_dir: GuardDirType, curr_loc: LocationType) -> LocationType:
    row, col = curr_loc
    next_row, next_col = GUARD_NEXT_POSITIONS[curr_dir]
    return row + next_row, col + next_col


def is_out_of_bounds(next_loc: LocationType, num_rows: int, num_cols: int) -> bool:
    row, col = next_loc
    return row < 0 or row >= num_rows or col < 0 or col >= num_cols


def is_guard_blocked(next_loc: LocationType, map: list[list[str]]) -> bool:
    return map[next_loc[0]][next_loc[1]] == "#"


def find_guard_blocker_positions(visited_locations: set[LocationType], hit_wall_locations: list[LocationType]) -> int:
    """
    Ok this attempt still isn't working because I think the loops could be way more
    complex than just the simple geometry so let's just basically put in a wall at various
    locations and resimulate
    """
    # so this is going to get the locations of the hit walls,
    # and we're going to see if we can basically create a rectangle
    # with three of them and then a location that we could insert into
    # the map
    #
    # so like in the tiny example, we get this:
    # hit_wall_locations
    # [(6, 4),
    # (1, 4),
    # (1, 8),
    # (6, 8),
    # (6, 2),
    # (4, 2),
    # (4, 6),
    # (8, 6),
    # (8, 1),
    # (7, 1),
    # (7, 7)]
    # and we should be able to put a blocker at (6, 3) basically
    # because that would cause us to:
    # 1. start at 6,4 going up
    # 2. hit the wall at 0,4 (so we'd turn at 1,4)
    # 3. hit the wall at 1,8 (so we'd turn at 1,7)
    # 4. hit the wall at 6,8 (so we'd turn at 5,8)
    # 5. then we'd be back at the start and hit the new wall
    #    at 6,3
    # so we need to basically look at (1, 4), (1, 8), (6, 8)
    # and see if we can detect that that's a rectangle

    num_potential_blocking_locs = 0
    rectangles = set()

    for p1_idx, p1 in enumerate(hit_wall_locations):
        for p2_idx, p2 in enumerate(hit_wall_locations):
            # avoid dups
            if p1_idx >= p2_idx:
                continue

            for p3_idx, p3 in enumerate(hit_wall_locations):
                p1_row, p1_col = p1
                p2_row, p2_col = p2
                p3_row, p3_col = p3

                # avoid dups
                if p2_idx >= p3_idx:
                    continue

                # ok so now we can just check if there's an example here where there are
                # 3 points where we could add a fourth where there could be a rectangle

                # so let's assume we're working with:
                # p1: (1, 4), p2: (1, 8), p3: (6, 8)
                # so we're looking for a p4 that would be (6, 3)
                # and we want to use our visited locations to see if we can
                # create a rectangle
                if p1_row == p2_row and p2_col == p3_col:
                    # Horizontal (p1 -> p2) and vertical (p2 -> p3)
                    p4 = (p3_row, p1_col)
                elif p1_row == p3_row and p3_col == p2_col:
                    # Horizontal (p1 -> p3) and vertical (p3 -> p2)
                    p4 = (p2_row, p1_col)
                elif p1_col == p2_col and p2_row == p3_row:
                    # Vertical (p1 -> p2) and horizontal (p2 -> p3)
                    p4 = (p1_row, p3_col)
                elif p1_col == p3_col and p3_row == p2_row:
                    # Vertical (p1 -> p3) and horizontal (p3 -> p2)
                    p4 = (p2_row, p1_col)
                else:
                    # Not forming a rectangle
                    continue

                # Check if p4 completes the rectangle and is in visited locations
                if p4 in visited_locations and p4 not in {p1, p2, p3}:
                    rectangle = frozenset({p1, p2, p3, p4})
                    if rectangle not in rectangles:
                        rectangles.add(rectangle)
                        num_potential_blocking_locs += 1

    return num_potential_blocking_locs


def would_loop_with_blocker(guard_map: list[list[str]]) -> bool:
    num_rows = len(guard_map)
    num_cols = len(guard_map[0])
    guard_loc, guard_dir = find_guard_starting_loc(guard_map)
    visited_states = set()

    while True:
        state = (guard_loc, guard_dir)
        if state in visited_states:
            # If we revisit the same location with the same direction, it's a loop
            return True
        visited_states.add(state)

        next_loc = advance_guard(guard_dir, guard_loc)
        if is_out_of_bounds(next_loc, num_rows, num_cols):
            return False
        if is_guard_blocked(next_loc, guard_map):
            guard_dir = turn_guard(guard_dir)
        else:
            guard_loc = next_loc


def simulate_blocker_positions_from_visited_locs(
    guard_map: list[list[str]], visited_locations: set[LocationType]
) -> int:
    num_potential_blocking_spots = 0
    orig_map = guard_map
    for location in visited_locations:
        row, col = location
        sim_guard_map = [row[:] for row in orig_map]
        sim_guard_map[row][col] = BLOCKER
        if would_loop_with_blocker(sim_guard_map):
            num_potential_blocking_spots += 1
    return num_potential_blocking_spots


def soln(input_file: Path) -> tuple[int, int]:
    """
    So we're basically just going to keep track of unique nodes
    we've visited in our matrix and then return the count of unique ones
    """

    guard_map = parse_input_as_matrix(input_file.read_text())
    num_rows = len(guard_map)
    num_cols = len(guard_map[0])
    guard_loc, guard_dir = find_guard_starting_loc(guard_map)
    guard_in_map = True
    visited_nodes: set[tuple[int, int]] = set()
    visited_nodes.add(guard_loc)

    # this is basically a list of where we had to turn
    # not the actual wall locations, but where we turned
    # we also want to include our starting location
    hit_wall_guard_locations: list[tuple[int, int]] = []

    while guard_in_map:
        # this part is going to:
        # 1. check the next location
        # 2. if we can't take the next step, turn the guard
        # 3. take the next step
        # 4. check if we're out of bounds, if so we're done
        # 5. add the location to the node
        # 6. repeat
        next_loc = advance_guard(guard_dir, guard_loc)
        if is_out_of_bounds(next_loc, num_rows, num_cols):
            guard_in_map = False
            break

        if is_guard_blocked(next_loc, guard_map):
            hit_wall_guard_locations.append(guard_loc)
            guard_dir = turn_guard(guard_dir)
        true_next_loc = advance_guard(guard_dir, guard_loc)
        visited_nodes.add(true_next_loc)
        guard_loc = true_next_loc

    # num_blocking_instructions = find_guard_blocker_positions(visited_nodes, hit_wall_guard_locations)
    num_blocking_locations = simulate_blocker_positions_from_visited_locs(guard_map, visited_nodes)
    return len(visited_nodes), num_blocking_locations


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day06.txt"
    print(soln(input_file))
