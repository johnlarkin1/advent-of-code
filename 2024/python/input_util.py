from dataclasses import dataclass
from typing import Any, List, Literal, TypeVar, Union, overload

Coordinate = tuple[int, int]
T = TypeVar("T", str, int, "Point")
Matrix = List[List[T]]

MatrixStr = Matrix[str]
MatrixInt = Matrix[int]

DIRECTION_VECS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


@overload
def parse_input_as_matrix(input_str: str, int_or_str: Literal["int"]) -> MatrixInt: ...


@overload
def parse_input_as_matrix(input_str: str, int_or_str: Literal["str"]) -> MatrixStr: ...


def parse_input_as_matrix(input_str: str, int_or_str: Literal["int", "str"] = "str") -> Union[MatrixInt, MatrixStr]:
    if int_or_str == "int":
        return [[int(cell.strip()) for cell in list(line)] for line in input_str.split("\n") if line]
    return [list(line) for line in input_str.split("\n") if line]


def matrix_to_string(matrix: Matrix[T]) -> str:
    return "\n".join("".join(map(str, row)) for row in matrix)


def point_matrix_to_string(matrix: Matrix["Point"]) -> str:
    return "\n".join("".join(map(lambda p: p.value, row)) for row in matrix)


def is_in_bounds(matrix: Matrix, loc: Coordinate) -> bool:
    return loc[0] >= 0 and loc[0] < len(matrix) and loc[1] >= 0 and loc[1] < len(matrix[0])


def is_in_matrix_bounds(matrix: Matrix["Point"], loc: Coordinate):
    x, y = loc
    return 0 <= y < len(matrix) and 0 <= x < len(matrix[0])


@dataclass(frozen=True)
class Point:
    x: int
    y: int
    value: Any

    def __lt__(self, other: "Point") -> bool:
        # Tie-breaking based on x, y, and direction
        return (self.x, self.y, self.value) < (other.x, other.y, other.value)


DirectionType = Literal["east", "west", "north", "south"]


@dataclass(frozen=True)
class PointWDirection:
    x: int
    y: int
    direction: DirectionType

    def __repr__(self):
        return f"Point({self.x}, {self.y}, {self.direction})"

    def __lt__(self, other: "PointWDirection") -> bool:
        # Tie-breaking based on x, y, and direction
        return (self.x, self.y, self.direction) < (other.x, other.y, other.direction)


MatrixPoint = Matrix[Point]


def convert_to_point_matrix(matrix_str: MatrixStr) -> MatrixPoint:
    point_matrix = []
    for y, row in enumerate(matrix_str):
        point_row = []
        for x, value in enumerate(row):
            point_row.append(Point(x, y, value))
        point_matrix.append(point_row)
    return point_matrix


def convert_to_point_matrix_old(matrix_str: MatrixStr) -> MatrixPoint:
    return [[Point(x, y, value) for y, value in enumerate(row)] for x, row in enumerate(matrix_str)]


def convert_to_point_matrix_correct(matrix_str: MatrixStr) -> MatrixPoint:
    return [[Point(x, y, value) for x, value in enumerate(row)] for y, row in enumerate(matrix_str)]


@dataclass
class Delta:
    dx: int
    dy: int


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


def overlay_points(matrix: MatrixStr, path: list[Point]) -> list[list[str]]:
    for stop in path:
        # Ensure the direction is within bounds
        if 0 <= stop.x < len(matrix) and 0 <= stop.y < len(matrix[0]):
            matrix[stop.y][stop.x] = "O"

    return matrix
