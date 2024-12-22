from dataclasses import dataclass
from typing import List, Literal, TypeVar, Union, overload

Coordinate = tuple[int, int]
T = TypeVar("T", str, int)
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


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Delta:
    dx: int
    dy: int
