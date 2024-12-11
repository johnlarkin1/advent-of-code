"""
Ok so, key points:
* The digits alternate between indicating the length of a file and the length of free space.
* Each file on disk also has an ID number based on the order of the files as they appear before they are rearranged

From here:
Each file on disk also has an ID number based on the order of the files as they appear before they are rearranged, starting with ID 0. So, the disk map 12345 has three files: a one-block file with ID 0, a three-block file with ID 1, and a five-block file with ID 2. Using one character for each block where digits are the file ID and . is free space, the disk map 12345 represents these individual blocks:

The amphipod would like to move file blocks one at a time from the end of the disk to the leftmost free space block (until there are no gaps remaining between file blocks). For the disk map 12345, the process looks like this:

0..111....22222
02.111....2222.
022111....222..
0221112...22...
02211122..2....
022111222......
The first example requires a few more steps:

00...111...2...333.44.5555.6666.777.888899
009..111...2...333.44.5555.6666.777.88889.
0099.111...2...333.44.5555.6666.777.8888..
00998111...2...333.44.5555.6666.777.888...
009981118..2...333.44.5555.6666.777.88....
0099811188.2...333.44.5555.6666.777.8.....
009981118882...333.44.5555.6666.777.......
0099811188827..333.44.5555.6666.77........
00998111888277.333.44.5555.6666.7.........
009981118882777333.44.5555.6666...........
009981118882777333644.5555.666............
00998111888277733364465555.66.............
0099811188827773336446555566..............

The final step of this file-compacting process is to update the filesystem checksum. To calculate the checksum, add up the result of multiplying each of these blocks' position with the file ID number it contains. The leftmost block is in position 0. If a block contains free space, skip it instead.

Continuing the first example, the first few blocks' position multiplied by its file ID number are 0 * 0 = 0, 1 * 0 = 0, 2 * 9 = 18, 3 * 9 = 27, 4 * 8 = 32, and so on. In this example, the checksum is the sum of these, 1928.
"""  # noqa: E501

from pathlib import Path

from timing_util import time_solution

FREE_SPACE_CHAR = "."


def compute_checksum(finalized_disk_map: list[str]) -> int:
    checksum = 0
    for idx, char in enumerate(finalized_disk_map):
        if char.isdigit():
            checksum += int(char) * idx
    return checksum


def expand_disk_map(disk_map: str) -> list[str]:
    compressed_disk_map = disk_map.strip()
    expanded_disk_map = []
    curr_file_id = 0
    for idx, char in enumerate(compressed_disk_map):
        if idx % 2 == 0:
            # this is corresponding to a file
            # expanded_disk_map += str(curr_file_id) * int(char)
            expanded_disk_map.extend([str(curr_file_id)] * int(char))
            curr_file_id += 1
        else:
            # this is corresponding to a free space
            expanded_disk_map.extend([FREE_SPACE_CHAR] * int(char))
    return expanded_disk_map


def sort_disk_map_pt1(disk_map: list[str]) -> list[str]:
    end_of_disk_map_ptr = len(disk_map) - 1
    for idx in range(len(disk_map)):
        char = disk_map[idx]
        if idx >= end_of_disk_map_ptr:
            # We've already looked at the full string
            break
        if char == FREE_SPACE_CHAR:
            while end_of_disk_map_ptr > idx:
                # ok if we find a digit, we need to move the pointer back
                # we should swap the free space with the digit and move the
                # free space back to the back
                if disk_map[end_of_disk_map_ptr].isdigit():
                    disk_map[end_of_disk_map_ptr], disk_map[idx] = (
                        disk_map[idx],
                        disk_map[end_of_disk_map_ptr],
                    )
                    end_of_disk_map_ptr -= 1
                    break
                end_of_disk_map_ptr -= 1
        else:
            continue
    return disk_map


def find_free_space_length(disk_map: list[str], idx: int):
    length = 0
    while idx < len(disk_map) and disk_map[idx] == FREE_SPACE_CHAR:
        length += 1
        idx += 1

    return length


def find_group_from_back(disk_map: list[str], starting_idx: int) -> int:
    group_length = 0
    starting_group_val = disk_map[starting_idx]
    while starting_idx >= 0 and disk_map[starting_idx].isdigit() and disk_map[starting_idx] == starting_group_val:
        group_length += 1
        starting_idx -= 1
    return group_length


def sort_disk_map_pt2(disk_map: list[str]) -> list[str]:
    """
    slightly different than pt1 because now we only slot it
    into the earlier spot if that spot has enough
    free space for the entire digits to fit...

    hmmm....
    maybe we should just start from the back
    """
    backward_idx = len(disk_map) - 1
    forward_idx = 0
    max_forward_idx = 0
    while backward_idx >= max_forward_idx:
        if disk_map[backward_idx].isdigit():
            group_length = find_group_from_back(disk_map, backward_idx)
            for forward_idx in range(0, backward_idx):
                if disk_map[forward_idx] == FREE_SPACE_CHAR:
                    free_space_length = find_free_space_length(disk_map, forward_idx)
                    if free_space_length >= group_length:
                        for i in range(group_length):
                            disk_map[forward_idx + i], disk_map[backward_idx - group_length + i + 1] = (
                                disk_map[backward_idx - group_length + i + 1],
                                disk_map[forward_idx + i],
                            )
                        break
            backward_idx -= group_length
        else:
            backward_idx -= 1
    return disk_map


def soln(input_file: Path) -> tuple[int, int]:
    file_checksum_pt1 = 0
    file_checksum_pt2 = 0

    compressed_disk_map = input_file.read_text().strip()
    expanded_disk_map = expand_disk_map(compressed_disk_map)
    expanded_disk_map_copy = expanded_disk_map.copy()
    sorted_disk_map_pt1 = sort_disk_map_pt1(expanded_disk_map)
    sorted_disk_map_pt2 = sort_disk_map_pt2(expanded_disk_map_copy)

    file_checksum_pt1 = compute_checksum(sorted_disk_map_pt1)
    file_checksum_pt2 = compute_checksum(sorted_disk_map_pt2)
    return (file_checksum_pt1, file_checksum_pt2)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    # input_file = curr_dir.parent / "inputs" / "day09_small.txt"
    input_file = curr_dir.parent / "inputs" / "day09.txt"
    # print(soln(input_file))
    time_solution("day09", soln, input_file)
