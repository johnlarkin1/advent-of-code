import time
import timeit
from enum import Enum
from typing import Any, Callable


class TimingOptions(str, Enum):
    PERF_COUNTER = "perf_counter"
    TIMEIT = "timeit"
    AVERAGE = "average"


class TimeUnit(str, Enum):
    SECONDS = "seconds"
    MILLISECONDS = "ms"
    MICROSECONDS = "µs"
    NANOSECONDS = "ns"


def time_function(func: Callable[..., Any], *args, **kwargs) -> float:
    start_time = time.perf_counter()
    func(*args, **kwargs)
    end_time = time.perf_counter()
    return end_time - start_time


def time_function_multiple(func: Callable[..., Any], *args, iterations: int = 10, **kwargs) -> float:
    total_time = 0
    for _ in range(iterations):
        total_time += time_function(func, *args, **kwargs)
    return total_time / iterations


def time_function_with_timeit(func: Callable[..., Any], *args, **kwargs) -> float:
    def wrapped():
        func(*args, **kwargs)

    return timeit.timeit(wrapped, number=10) / 10


def convert_time(time_in_seconds: float, unit: TimeUnit) -> float:
    if unit == TimeUnit.SECONDS:
        return time_in_seconds
    elif unit == TimeUnit.MILLISECONDS:
        return time_in_seconds * 1000
    elif unit == TimeUnit.MICROSECONDS:
        return time_in_seconds * 1_000_000
    elif unit == TimeUnit.NANOSECONDS:
        return time_in_seconds * 1_000_000_000
    else:
        raise ValueError(f"Unsupported time unit: {unit}")


def compare_functions(
    functions: list[tuple[str, Callable[..., Any]]],
    *args,
    method: TimingOptions = TimingOptions.PERF_COUNTER,
    unit: TimeUnit = TimeUnit.SECONDS,
    iterations: int = 10,
    **kwargs,
) -> None:
    """
    Compares the execution time of multiple functions using the specified timing method and unit.

    Args:
        functions: A list of tuples containing function names and function references.
        *args: Positional arguments to pass to the functions.
        method: The timing method to use (perf_counter, timeit, or average).
        unit: The desired time unit for the output (seconds, milliseconds, nanoseconds).
        iterations: The number of iterations for the "average" timing method.
    """
    for name, func in functions:
        if method == TimingOptions.PERF_COUNTER:
            execution_time = time_function(func, *args, **kwargs)
        elif method == TimingOptions.TIMEIT:
            execution_time = time_function_with_timeit(func, *args, **kwargs)
        elif method == TimingOptions.AVERAGE:
            execution_time = time_function_multiple(func, *args, iterations=iterations, **kwargs)

        converted_time = convert_time(execution_time, unit)
        print(f"{name} execution time ({method.value}): {converted_time:.6f} {unit.value}")


def time_solution(
    day: str,
    func: Callable[..., Any],
    *args,
    method: TimingOptions = TimingOptions.PERF_COUNTER,
    unit: TimeUnit = TimeUnit.SECONDS,
    iterations: int = 10,
    **kwargs,
) -> None:
    if method == TimingOptions.PERF_COUNTER:
        execution_time = time_function(func, *args, **kwargs)
    elif method == TimingOptions.TIMEIT:
        execution_time = time_function_with_timeit(func, *args, **kwargs)
    elif method == TimingOptions.AVERAGE:
        execution_time = time_function_multiple(func, *args, iterations=iterations, **kwargs)

    converted_time = convert_time(execution_time, unit)
    print(f"{day}: {converted_time:.6f} {unit.value}")
