from dataclasses import dataclass
from typing import Any, List, Literal, TypeVar, Union, overload

Coordinate = tuple[int, int]
T = TypeVar("T", str, int, "Point")
Matrix = List[List[T]]

MatrixStr = Matrix[str]
MatrixInt = Matrix[int]


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


def is_in_bounds(matrix: Matrix, loc: Coordinate) -> bool:
    return loc[0] >= 0 and loc[0] < len(matrix) and loc[1] >= 0 and loc[1] < len(matrix[0])


@dataclass(frozen=True)
class Point:
    x: int
    y: int
    value: Any


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
    return [[Point(x, y, value) for y, value in enumerate(row)] for x, row in enumerate(matrix_str)]


@dataclass
class Delta:
    dx: int
    dy: int
