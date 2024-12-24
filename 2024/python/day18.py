"""
Ok I'm burnt now. But here we go.


```
Your memory space is a two-dimensional grid with coordinates that range from 0 to 70 both horizontally and vertically. However, for the sake of example, suppose you're on a smaller grid with coordinates that range from 0 to 6 and the following list of incoming byte positions:

Each byte position is given as an X,Y coordinate, where X is the distance from the left edge of your memory space and Y is the distance from the top edge of your memory space.
```

ok cool but this just feels like true Dijsktras where you're trying to find the minimum number of steps.
"""  # noqa: E501

import heapq
from pathlib import Path

from input_util import MatrixStr, Point, matrix_to_string, overlay_points

MEMORY_RANGE = 70
EXAMPLE_MEMORY_RANGE = 6
NUMBER_BYTES_TO_SIMULATE = 1024

IS_TEST = False


def populate_matrix_from_input(matrix: MatrixStr, input_file: Path) -> None:
    with open(input_file) as f:
        for idx, line in enumerate(f.readlines()):
            if idx == NUMBER_BYTES_TO_SIMULATE:
                break
            x, y = map(int, line.strip().split(","))
            matrix[y][x] = "#"
            # print(f"Falling Byte Idx: {idx} with (x, y) = ({x}, {y})")
            # print(matrix_to_string(matrix))


def dijkstras(matrix: MatrixStr) -> tuple[int, list[Point]]:
    """Finds the shortest path through the matrix."""

    starting_point = Point(0, 0, ".")
    memory_range = EXAMPLE_MEMORY_RANGE if IS_TEST else MEMORY_RANGE
    destination_point = Point(memory_range, memory_range, ".")

    distances = {starting_point: 0}
    routes = {starting_point: None}

    priority_queue = []
    heapq.heappush(priority_queue, (0, starting_point))

    final_route = []
    final_distance = 0

    while priority_queue:
        current_distance, current_point = heapq.heappop(priority_queue)

        if current_point.value == "#":
            # we can't work with walls
            continue

        if current_point == destination_point:
            final_distance = current_distance
            while current_point:
                final_route.append(current_point)
                current_point = routes[current_point]
            break

        for move in ["up", "down", "left", "right"]:
            new_x = current_point.x
            new_y = current_point.y
            new_distance = current_distance + 1
            if move == "up":
                new_y -= 1
            elif move == "down":
                new_y += 1
            elif move == "left":
                new_x -= 1
            elif move == "right":
                new_x += 1

            if new_x < 0 or new_y < 0 or new_x > memory_range or new_y > memory_range:
                # we can't move out of bounds
                continue

            new_point = Point(new_x, new_y, matrix[new_y][new_x])
            if new_distance < distances.get(new_point, float("inf")):
                distances[new_point] = new_distance
                routes[new_point] = current_point
                heapq.heappush(priority_queue, (new_distance, new_point))

    return final_distance, final_route


def soln(input_file: Path) -> tuple[int, str]:
    num_steps_out_pt1 = 0
    breaking_loc = ""
    memory_range = EXAMPLE_MEMORY_RANGE if IS_TEST else MEMORY_RANGE
    memory_matrix = [["." for _ in range(memory_range + 1)] for _ in range(memory_range + 1)]
    populate_matrix_from_input(memory_matrix, input_file)
    num_steps_out_pt1, route = dijkstras(memory_matrix)
    matrix = overlay_points(memory_matrix, route)
    print("Part 1")
    print("Found solution:")
    print(matrix_to_string(matrix))
    print("Part 2")

    fresh_memory_matrix = [["." for _ in range(memory_range + 1)] for _ in range(memory_range + 1)]
    with open(input_file) as f:
        for idx, line in enumerate(f.readlines()):
            x, y = map(int, line.strip().split(","))
            fresh_memory_matrix[y][x] = "#"
            print(f"Idx: {idx} with (x, y) = ({x}, {y})")
            num_steps_out_pt2, route = dijkstras(fresh_memory_matrix)
            if not route:
                print("idx", idx)
                breaking_loc = f"{x},{y}"
                break

    return (num_steps_out_pt1, breaking_loc)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file: Path
    if IS_TEST:
        input_file = curr_dir.parent / "inputs" / "day18_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day18.txt"

    print(soln(input_file))
