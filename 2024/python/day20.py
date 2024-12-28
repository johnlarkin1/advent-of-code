from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import List

from input_util import (
    Coordinate,
    MatrixPoint,
    Point,
    convert_to_point_matrix,
    is_in_matrix_bounds,
    matrix_to_string,
    parse_input_as_matrix,
    point_matrix_to_string,
)

ARE_TESTING = False
TIME_SAVING_CUTOFF = 100
MAX_CHEAT_TIME = 20


@dataclass
class CheatInfo:
    location: Point
    distance_saving: int


@dataclass
class BFSState:
    current_loc: Point
    distance_traveled: int


class PointExt(Point):
    is_cheat: bool

    def __init__(self, point: Point, is_cheat: bool = False):
        super().__init__(point.x, point.y, point.value)
        self.is_cheat = is_cheat


@dataclass(frozen=True)
class ExploreState:
    current_loc: Point
    distance_traveled: int
    path: list[PointExt]
    have_activated_cheat: bool
    is_in_cheat_mode: bool
    cheats_left: int


@dataclass(frozen=True)
class FinalPathInfo:
    total_distance: int
    path: list[PointExt]
    cheat_used: bool


def group_paths_by_savings(paths: List[CheatInfo]) -> dict[int, List[CheatInfo]]:
    grouped_paths = defaultdict(list)

    for path_info in paths:
        savings = path_info.distance_saving
        grouped_paths[savings].append(path_info)

    return grouped_paths


def print_grouped_savings(grouped_paths: dict[int, List[CheatInfo]]) -> None:
    # Iterate through the groups in descending order of savings
    for savings, paths in sorted(grouped_paths.items(), key=lambda x: -x[0]):
        num_paths = len(paths)
        if num_paths == 1:
            print(f"  - There is one cheat that saves {savings} picoseconds.")
        else:
            print(f"  - There are {num_paths} cheats that save {savings} picoseconds.")


def find_starting_and_end_location(reindeer_map: MatrixPoint) -> tuple[Point, Point]:
    start_loc: Point | None = None
    end_loc: Point | None = None
    for row in reindeer_map:
        for point in row:
            if point.value == "S":
                start_loc = point
            if point.value == "E":
                end_loc = point
    assert start_loc is not None and end_loc is not None
    return start_loc, end_loc


def bfs_without_cheats(matrix: MatrixPoint, start_loc: Point, end_loc: Point) -> dict[Coordinate, int]:
    start_state = BFSState(current_loc=start_loc, distance_traveled=0)
    queue = deque([start_state])
    visited: dict[Coordinate, int] = {}

    while queue:
        curr_state = queue.popleft()
        current_point = curr_state.current_loc
        current_distance = curr_state.distance_traveled

        visited[(current_point.x, current_point.y)] = current_distance

        if (current_point.x, current_point.y) == (end_loc.x, end_loc.y):
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_x = current_point.x + dx
            new_y = current_point.y + dy

            if not is_in_matrix_bounds(matrix, (new_x, new_y)):
                continue

            if matrix[new_y][new_x].value == "#" or (new_x, new_y) in visited:
                continue

            new_point = Point(new_x, new_y, matrix[new_y][new_x])
            new_state = BFSState(current_loc=new_point, distance_traveled=current_distance + 1)
            queue.append(new_state)

    return visited


def modified_bfs_explore(
    matrix: MatrixPoint, start_loc: Point, end_loc: Point, visited: dict[tuple[int, int], int]
) -> list[CheatInfo]:
    cheats = []
    shortest_path_distance = visited[(end_loc.x, end_loc.y)]

    for (x, y), distance in visited.items():
        if distance >= shortest_path_distance:
            continue

        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            new_x, new_y = x + dx, y + dy

            if is_in_matrix_bounds(matrix, (new_x, new_y)):
                neighbor_point = (new_x, new_y)
                if neighbor_point == (end_loc.x, end_loc.y):
                    print(f"Found neighbor point at ({new_x}, {new_y}) leading to end location.")
                    print(f"Distance: {distance}, Shortest path distance: {shortest_path_distance}")
                    print("x, y:", x, y)
                if neighbor_point in visited:
                    if neighbor_point == (end_loc.x, end_loc.y):
                        print("then got here")
                    if visited[neighbor_point] > distance:
                        # this means we could save some time
                        time_saving = visited[neighbor_point] - distance - 2
                        if time_saving >= TIME_SAVING_CUTOFF:
                            cheats.append(
                                CheatInfo(
                                    location=Point(new_x, new_y, matrix[new_y][new_x].value),  # Create a Point
                                    distance_saving=visited[neighbor_point] - distance - 2,  # 2 second cheat
                                )
                            )

    return cheats


def modified_bfs_explore_v2(
    matrix: MatrixPoint, start_loc: Point, end_loc: Point, visited: dict[Coordinate, int]
) -> list[CheatInfo]:
    """
    Create a list of CheatInfo by iterating over the visited dictionary.
    """
    cheats = []

    sorted_path = sorted(visited, key=visited.get)  # type: ignore
    for t1, coord1 in enumerate(sorted_path):
        for t2 in range(t1 + 1, len(sorted_path)):
            coord2 = sorted_path[t2]
            x1, y1 = coord1
            x2, y2 = coord2

            # Calculate Manhattan distance!
            distance = abs(x1 - x2) + abs(y1 - y2)

            if distance <= MAX_CHEAT_TIME:
                time_saving = visited[coord2] - visited[coord1] - distance
                if time_saving >= TIME_SAVING_CUTOFF:
                    cheat_info = CheatInfo(
                        location=Point(x2, y2, matrix[y2][x2].value),
                        distance_saving=time_saving,
                    )
                    cheats.append(cheat_info)

    return cheats


# def modified_bfs_explore(
#     matrix: MatrixPoint, start_loc: Point, end_loc: Point, shortest_path_distance: int
# ) -> list[CheatInfo]:
#     """Explore the matrix using BFS and keep track of the shortest path
#     we're going to capitalize on BFS and just keep track of each path's cheat state.

#     We're going to keep track of:
#     * current location
#     * cheats left
#     * distance traveled

#     If we are in cheat_mode, we're allowed to pass through two walls to save time.
#     If we activate our cheat, we're not allowed to skip through a wall at a later time.
#     """
#     start_item = ExploreItem(
#         current_loc=start_loc,
#         cheats_left=1,
#         distance_traveled=0,
#         path=[PointExt(start_loc)],
#     )
#     explore_queue: deque[ExploreItem] = deque([start_item])
#     visited: set[ExploreState] = set()

#     cheats: list[CheatInfo] = []

#     while explore_queue:
#         curr_item = explore_queue.popleft()
#         print(f"Exploring: {curr_item}")
#         current_point = curr_item.current_loc
#         current_distance = curr_item.distance_traveled
#         cheats_left = curr_item.cheats_left

#         if (current_point.x, current_point.y) == (end_loc.x, end_loc.y):
#             path = curr_item.path
#             cheat_location = None
#             for i in range(len(path) - 1):
#                 pos1 = path[i]
#                 pos2 = path[i + 1]
#                 if pos1.is_cheat:
#                     print(f"Found a cheat at pos1: {pos1}")
#                     cheat_location = CheatLocation(first=pos1, second=pos2)

#                 if cheat_location is not None:
#                     cheats.append(CheatInfo(cheat_location, curr_item.path, current_distance))

#             continue

#         state = ExploreState(current_point.x, current_point.y, curr_item.cheats_left)
#         if state in visited:
#             continue
#         visited.add(state)

#         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             new_x = current_point.x + dx
#             new_y = current_point.y + dy

#             if not is_in_matrix_bounds(matrix, (new_x, new_y)):
#                 continue

#             next_point = matrix[new_y][new_x]
#             new_cheats_left = cheats_left
#             is_cheat_point = False

#             if next_point.value == "#":
#                 if new_cheats_left > 0:
#                     new_cheats_left -= 1
#                     is_cheat_point = True
#                     print("Setting is_cheat_point")
#                 else:
#                     # if we don't have any cheats and we're at a wall,
#                     # we can't explore more here
#                     continue

#             new_point = Point(new_x, new_y, next_point.value)
#             new_item = ExploreItem(
#                 current_loc=new_point,
#                 cheats_left=new_cheats_left,
#                 distance_traveled=current_distance + 1,
#                 path=curr_item.path + [PointExt(new_point, is_cheat_point)],
#             )
#             explore_queue.append(new_item)

#     return cheats


# def modified_bfs_explore(
#     matrix: MatrixPoint, start_loc: Point, end_loc: Point, shortest_path_distance: int
# ) -> list[FinalPathInfo]:
#     """Explore the matrix using BFS and keep track of the shortest path
#     we're going to capitalize on BFS and just keep track of each path's cheat state.

#     We're going to keep track of:
#     * current location
#     * cheats left
#     * distance traveled

#     If we are in cheat_mode, we're allowed to pass through two walls.

#     So again, this is basically BFS but we're going to have a cheat mode, where we
#     can pass through two consecutive walls
#     """
#     starting_cheats = 2
#     start_explore = ExploreState(
#         current_loc=start_loc,
#         distance_traveled=0,
#         path=[PointExt(start_loc)],
#         have_activated_cheat=False,
#         is_in_cheat_mode=False,
#         cheats_left=starting_cheats,
#     )
#     explore_queue = deque([start_explore])

#     found_final_path_info: list[FinalPathInfo] = []
#     visited = set()

#     while explore_queue:
#         curr = explore_queue.popleft()
#         print(f"Exploring: {curr.current_loc} with cheats left: {curr.cheats_left}")
#         current_point = curr.current_loc
#         current_distance = curr.distance_traveled

#         have_activated_cheat = curr.have_activated_cheat
#         is_currently_in_cheat_mode = curr.is_in_cheat_mode
#         cheats_left = curr.cheats_left

#         if (current_point.x, current_point.y) == (end_loc.x, end_loc.y):
#             path = curr.path
#             cheat_used = any(point.is_cheat for point in path)
#             found_final_path_info.append(FinalPathInfo(current_distance, path, cheat_used))
#             print(f"Reached end location: {end_loc} with distance: {current_distance} and cheats used: {cheat_used}")
#             continue

#         for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             new_x = current_point.x + dx
#             new_y = current_point.y + dy

#             if not is_in_matrix_bounds(matrix, (new_x, new_y)):
#                 print(f"Out of bounds: ({new_x}, {new_y}), skipping.")
#                 continue

#             next_point = matrix[new_y][new_x]
#             # new states for next exploration
#             new_have_activated_cheat = have_activated_cheat
#             new_is_in_cheat_mode = is_currently_in_cheat_mode
#             new_cheats_left = cheats_left

#             state_signature = (
#                 new_x,
#                 new_y,
#                 new_have_activated_cheat,
#                 new_is_in_cheat_mode,
#                 new_cheats_left,
#             )
#             if state_signature in visited:
#                 # print(f"Already visited state: {state_signature}, skipping.")
#                 continue
#             visited.add(state_signature)

#             # Now we handle the cheat logic
#             next_cell_is_a_wall = next_point.value == "#"
#             # print(f"Next cell ({new_x}, {new_y}) is a wall: {next_cell_is_a_wall}")

#             if next_cell_is_a_wall:
#                 if not have_activated_cheat:
#                     new_have_activated_cheat = True
#                     new_is_in_cheat_mode = True
#                     new_cheats_left -= 1
#                     # print(f"Activated cheat at ({new_x}, {new_y}), cheats left: {new_cheats_left}")
#                 else:
#                     if is_currently_in_cheat_mode:
#                         # we can use another
#                         new_cheats_left -= 1
#                         if new_cheats_left < 0:
#                             # print(f"No cheats left after using, skipping cell ({new_x}, {new_y}).")
#                             continue
#                         new_is_in_cheat_mode = True
#                         # print(f"Using another cheat at ({new_x}, {new_y}), cheats left: {new_cheats_left}")
#                     else:
#                         # we can't use another cheat
#                         # print(f"Cannot use another cheat at ({new_x}, {new_y}), skipping.")
#                         continue
#             else:
#                 if have_activated_cheat and is_currently_in_cheat_mode:
#                     new_is_in_cheat_mode = False
#                     new_cheats_left = 0
#                     # print(f"Ending cheat mode at ({new_x}, {new_y}), cheats left: {new_cheats_left}")

#             new_point = Point(new_x, new_y, next_point.value)
#             # print("new_point:", new_point)
#             new_item = ExploreState(
#                 current_loc=new_point,
#                 distance_traveled=current_distance + 1,
#                 path=curr.path + [PointExt(new_point, is_cheat=next_cell_is_a_wall)],
#                 have_activated_cheat=new_have_activated_cheat,
#                 is_in_cheat_mode=new_is_in_cheat_mode,
#                 cheats_left=new_cheats_left,
#             )
#             # print(f"Adding new item to explore queue: {new_item}")
#             explore_queue.append(new_item)
#     return found_final_path_info


def soln(input_file: Path) -> tuple[int, int]:
    pt1_ans = 0
    pt2_ans = 0

    race_map_str = parse_input_as_matrix(input_file.read_text(), "str")
    print(matrix_to_string(race_map_str))
    race_map = convert_to_point_matrix(race_map_str)
    start_loc, end_loc = find_starting_and_end_location(race_map)
    if ARE_TESTING:
        print("matrix")
        print(point_matrix_to_string(race_map))
        print(f"start_loc: {start_loc}")
        print(f"end_loc: {end_loc}")
    visited = bfs_without_cheats(race_map, start_loc, end_loc)
    print("visited", visited)
    final_path_dests = modified_bfs_explore(matrix=race_map, start_loc=start_loc, end_loc=end_loc, visited=visited)
    pt1_ans = len(final_path_dests)
    grouped_paths = group_paths_by_savings(final_path_dests)
    print("\nPart 1\n")
    print_grouped_savings(grouped_paths)

    final_path_dests = modified_bfs_explore_v2(matrix=race_map, start_loc=start_loc, end_loc=end_loc, visited=visited)
    pt2_ans = len(final_path_dests)
    grouped_paths = group_paths_by_savings(final_path_dests)
    print("\nPart 2\n")
    print_grouped_savings(grouped_paths)

    # print_grouped_savings(grouped_paths)

    # Group results by number of time saved
    # grouped_results = {}
    # for key, result in cheat_mapping.items():
    #     time_saved = result["time_saved"]
    #     if time_saved not in grouped_results:
    #         grouped_results[time_saved] = []
    #     grouped_results[time_saved].append(result)

    # for time_saved, items in grouped_results.items():
    #     print(f"Time saved: {time_saved}, Results: {items}")

    return (pt1_ans, pt2_ans)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if ARE_TESTING:
        input_file = curr_dir.parent / "inputs" / "day20_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day20.txt"
    print(soln(input_file))
