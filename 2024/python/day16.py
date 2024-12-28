"""
Ok so I'm thinking we can just solve this with a potential
greedy algorithm? Although I'm not sure...

Actually no, I think what would be best is we do like a modified Dijsktra's
where the weights are basically the move costs and then we just optimize over that.

Yeah ok so I had to do some googling, but Dijkstra's uses a priority queue with the move step weights as basically the cost of each thing.
"""

import heapq
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

from input_util import (
    Coordinate,
    DirectionType,
    MatrixPoint,
    Point,
    PointWDirection,
    convert_to_point_matrix_old,
    matrix_to_string,
    parse_input_as_matrix,
)


def overlay_directions(matrix: list[list[Point]], directions: list[PointWDirection]) -> list[list[str]]:
    # Create a copy of the original matrix for overlaying
    result = [[point.value for point in row] for row in matrix]

    # Map DirectionType to visual symbols
    direction_map = {"east": ">", "west": "<", "north": "^", "south": "v"}

    # Overlay the directions on the result matrix
    for direction in directions:
        # Ensure the direction is within bounds
        if 0 <= direction.x < len(matrix) and 0 <= direction.y < len(matrix[0]):
            result[direction.y][direction.x] = direction_map[direction.direction]

    return result


MoveType = Literal["forward", "turn-clockwise", "turn-counter-clockwise"]
MOVE_COST_MAP: dict[MoveType, int] = {"forward": 1, "turn-clockwise": 1000, "turn-counter-clockwise": 1000}


def get_turn_direction(current_direction: DirectionType, turn_type: MoveType) -> DirectionType:
    if turn_type == "turn-clockwise":
        if current_direction == "east":
            return "south"
        elif current_direction == "south":
            return "west"
        elif current_direction == "west":
            return "north"
        elif current_direction == "north":
            return "east"
    elif turn_type == "turn-counter-clockwise":
        if current_direction == "east":
            return "north"
        elif current_direction == "north":
            return "west"
        elif current_direction == "west":
            return "south"
        elif current_direction == "south":
            return "east"
    return current_direction


def find_starting_and_end_location(reindeer_map: MatrixPoint) -> tuple[Coordinate, Coordinate]:
    start_loc = (-1, -1)
    end_loc = (-1, -1)
    for row in reindeer_map:
        for point in row:
            if point.value == "S":
                start_loc = (point.x, point.y)
            if point.value == "E":
                end_loc = (point.x, point.y)
    return start_loc, end_loc


def modified_dijkstras_exploration(
    reindeer_map: MatrixPoint, start_loc: Coordinate, end_loc: Coordinate
) -> tuple[float, list[PointWDirection] | None, set[Point]]:
    priority_queue: list[tuple[int, PointWDirection]] = []

    # from our starting location, we have a distance of 0 and assume that we can start
    # facing any direction - ah nope nevermind, we have to start facing east
    starting_point = PointWDirection(start_loc[1], start_loc[0], "east")
    heapq.heappush(priority_queue, (0, starting_point))
    distances: dict[PointWDirection, float] = {}
    routes: dict[PointWDirection, PointWDirection | None] = {}
    predecessors: dict[PointWDirection, set[PointWDirection]] = defaultdict(set)

    # final elements to return
    final_score = float("inf")
    final_path: list[PointWDirection] | None = None
    all_end_route_locations: set[Point] = set()
    for row in reindeer_map:
        for point in row:
            for direction in ["east", "west", "north", "south"]:
                distances[PointWDirection(point.x, point.y, direction)] = float("inf")  # type: ignore
                routes[PointWDirection(point.x, point.y, direction)] = None  # type: ignore

    while priority_queue:
        # print(f"Priority queue: {priority_queue}")
        current_distance, current_point = heapq.heappop(priority_queue)
        if current_distance > distances[current_point]:
            continue

        if reindeer_map[current_point.y][current_point.x].value == "#":
            # print(f"Hit a wall at {current_point}")
            continue

        if current_point.x == end_loc[1] and current_point.y == end_loc[0]:
            # print(f"Found end location at {current_point}")
            path = []
            visited_reconstruction = set()

            while current_point != starting_point:
                if current_point in visited_reconstruction:
                    # print(f"Path reconstruction failed at {current_point}")
                    # print(f"Routes: {routes}")
                    raise AssertionError("Path reconstruction failed - cycle found")
                visited_reconstruction.add(current_point)
                path.append(current_point)
                assert current_point, "Current point should not be None"
                current_point = routes[current_point]

            # print(f"Found path: {path[::-1]}")
            # all_end_route_locations.update(Point(current_point.x, current_point.y, -1) for current_point in path[::-1])
            final_score = distances[path[0]]
            final_path = path[::-1]

        assert current_point, "Current point should not be None"

        for move in ["forward", "turn-clockwise", "turn-counter-clockwise"]:
            new_distance = current_distance + MOVE_COST_MAP[move]  # type: ignore
            new_point: PointWDirection | None = None
            if move == "forward":
                new_x, new_y = current_point.x, current_point.y
                if current_point.direction == "east":
                    new_x += 1
                elif current_point.direction == "west":
                    new_x -= 1
                elif current_point.direction == "north":
                    new_y -= 1
                elif current_point.direction == "south":
                    new_y += 1
                new_point = PointWDirection(new_x, new_y, current_point.direction)
            elif move == "turn-clockwise":
                new_direction = get_turn_direction(current_point.direction, "turn-clockwise")
                new_point = PointWDirection(current_point.x, current_point.y, new_direction)
            elif move == "turn-counter-clockwise":
                new_direction = get_turn_direction(current_point.direction, "turn-counter-clockwise")
                new_point = PointWDirection(current_point.x, current_point.y, new_direction)

            assert new_point, "New point should not be None"
            if new_distance < distances[new_point]:
                distances[new_point] = new_distance
                routes[new_point] = current_point
                predecessors[new_point] = {current_point}
                heapq.heappush(priority_queue, (new_distance, new_point))
            elif new_distance == distances[new_point]:
                predecessors[new_point].add(current_point)

    # part 2
    min_end_cost = float("inf")
    end_states = []
    ex, ey = end_loc  # typical usage: end_loc = (x, y)
    for direction in ["east", "west", "north", "south"]:
        candidate = PointWDirection(ey, ex, direction)  # type: ignore
        cost = distances[candidate]
        if cost < min_end_cost:
            min_end_cost = cost
            end_states = [candidate]
        elif cost == min_end_cost:
            end_states.append(candidate)

    visited_states: set[PointWDirection] = set()
    queue = deque(end_states)
    while queue:
        node = queue.pop()
        if node in visited_states:
            continue
        visited_states.add(node)
        for pred in predecessors[node]:
            queue.appendleft(pred)

    all_end_route_locations = {Point(s.x, s.y, -1) for s in visited_states}

    return final_score, final_path, all_end_route_locations


def soln(input_file: Path) -> tuple[int, int]:
    cheapest_path_score_pt1 = 0
    number_of_seats_pt2 = 0
    reindeer_map_temp = parse_input_as_matrix(input_file.read_text(), "str")
    print("Found reindeer map:")
    print(matrix_to_string(reindeer_map_temp))
    reindeer_map = convert_to_point_matrix_old(reindeer_map_temp)
    start_loc, end_loc = find_starting_and_end_location(reindeer_map)
    print(f"Start loc: {start_loc}")
    print(f"End loc: {end_loc}")
    cheapest_path_score_pt1, path, all_path_locations = modified_dijkstras_exploration(reindeer_map, start_loc, end_loc)
    if path:
        reindeer_map_overlaid = overlay_directions(reindeer_map, path)
        print("Found solution:")
        print(matrix_to_string(reindeer_map_overlaid))
    print(f"Cheapest path score: {cheapest_path_score_pt1}")
    number_of_seats_pt2 = len(all_path_locations)
    return (int(cheapest_path_score_pt1), number_of_seats_pt2)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day16_small.txt"
    # input_file = curr_dir.parent / "inputs" / "day16_med.txt"
    input_file = curr_dir.parent / "inputs" / "day16.txt"
    print(soln(input_file))
