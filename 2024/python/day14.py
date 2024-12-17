"""
Ok i'm sure part 2 is going to be a bear but this seems pretty straightforward

We're just populating positions and then moving them modulo the walls
to get the final locations of all the robots...


Woof yeah like expected part 2 is a bear...

So we're looking for a christmas tree shape which like i'm not even sure what that would look like.

Ah interesting. Ok this was the first one where I read through the reddit thread.
Sorting by entropy is a wild idea. I did notice that they would align horizontally and vertically so that
was also something to keep an eye out for, and then you know they're going to repeat at some point because
of the mod 103 and mod 101.
"""

import math
import os
import uuid
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import Literal

import numpy as np
from matplotlib import pyplot as plt

TEST_CASE: Literal["small", "main"] = "main"
NUM_TILES_WIDE = 101 if TEST_CASE == "main" else 11
NUM_TILES_TALL = 103 if TEST_CASE == "main" else 7
NUM_SECONDS_TO_SIMULATE = 5000
# Someone made a good point online:
# https://www.reddit.com/r/adventofcode/comments/1hdwdbf/comment/m20hior/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
MAX_NUM_SECONDS_TO_SIMULATE = 101 * 103


@dataclass
class RobotInfo:
    robot_id: uuid.UUID
    x_pos: int
    y_pos: int
    x_vel_per_sec: int
    y_vel_per_sec: int


def parse_robot_line(line: str) -> RobotInfo:
    position_info, velocity_info = line.split(" ")
    x_pos, y_pos = position_info.split("=")[1].split(",")
    x_vel, y_vel = velocity_info.split("=")[1].split(",")
    return RobotInfo(uuid.uuid4(), int(x_pos), int(y_pos), int(x_vel), int(y_vel))


def visualize_robot_map(
    robot_map: list[list[str]], step: int, robot_ids: dict[tuple[int, int], list[str]] = None
) -> None:
    print(f"Visualizing robot map at step {step}...")
    numeric_map = np.array([[int(cell) if cell != "." else 0 for cell in row] for row in robot_map])

    # Ensure the output directory exists
    output_dir = Path(__file__).parent / "outputs" / "day14"
    os.makedirs(output_dir, exist_ok=True)

    # Plotting the robot map
    plt.figure(figsize=(10, 8))
    plt.imshow(numeric_map, cmap="Greens", aspect="auto", origin="upper")  # Top-left origin
    plt.colorbar(label="Number of Robots")
    plt.title(f"Robot Density Map at Step {step}")
    plt.xlabel("Tiles Wide")
    plt.ylabel("Tiles Tall")

    # Overlay robot IDs
    # for (y, x), ids in robot_ids.items():
    #     # x is the horizontal position, y is vertical (already from the top)
    #     text_x = x
    #     text_y = y  # No flipping needed with origin='upper'

    #     # Shorten IDs for readability
    #     short_ids = [id[:4] for id in ids]  # Shorten IDs to 4 characters
    #     ids_text = "\n".join(short_ids[:3])  # Show up to 3 IDs
    #     if len(ids) > 3:
    #         ids_text += "\n..."

    #     # Overlay text at the center of each tile
    #     plt.text(
    #         text_x,
    #         text_y,
    #         ids_text,
    #         color="black",
    #         ha="center",
    #         va="center",
    #         fontsize=8,
    #         bbox=dict(facecolor="white", alpha=0.7, edgecolor="none", boxstyle="round,pad=0.3"),
    #     )

    # Save the figure
    file_path = os.path.join(output_dir, f"robot_map_step_{step:03}.png")
    plt.savefig(file_path)
    plt.close()


class RobotMap:
    def __init__(self, num_tiles_wide: int, num_tiles_tall: int) -> None:
        self.num_tiles_wide = num_tiles_wide
        self.num_tiles_tall = num_tiles_tall
        self.robot_map: list[list[str]] = [["." for _ in range(num_tiles_wide)] for _ in range(num_tiles_tall)]
        self.robot_infos: list[RobotInfo] = []
        self.robot_info_mapping: dict[uuid.UUID, RobotInfo] = {}

    @classmethod
    def init_with_robots(cls, num_tiles_wide: int, num_tiles_tall: int, robot_infos: list[RobotInfo]):
        self = cls(num_tiles_wide, num_tiles_tall)
        self.robot_infos = robot_infos
        for robot_info in robot_infos:
            self.robot_info_mapping[robot_info.robot_id] = robot_info
            self.add_robot(robot_info.x_pos, robot_info.y_pos)
        return self

    def add_robot(self, x_pos: int, y_pos: int) -> None:
        if self.robot_map[y_pos][x_pos] == ".":
            # we need to set it to be 1, because this Robot is now hear
            self.robot_map[y_pos][x_pos] = "1"
            return

        # then it should be a number and we should increment
        num_robots_at_cell = int(self.robot_map[y_pos][x_pos])
        num_robots_at_cell += 1
        self.robot_map[y_pos][x_pos] = str(num_robots_at_cell)

    def simulate_robot_movement(self, robot_info: RobotInfo, num_seconds: int) -> tuple[int, int]:
        x_pos = robot_info.x_pos + robot_info.x_vel_per_sec * num_seconds
        y_pos = robot_info.y_pos + robot_info.y_vel_per_sec * num_seconds
        return (x_pos % NUM_TILES_WIDE, y_pos % NUM_TILES_TALL)

    def simulate_all_robot_movements_one_second(self) -> None:
        for robot_info in self.robot_info_mapping.values():
            x_pos, y_pos = self.simulate_robot_movement(robot_info, 1)
            self.robot_info_mapping[robot_info.robot_id].x_pos = x_pos
            self.robot_info_mapping[robot_info.robot_id].y_pos = y_pos

    def visualize_map_from_robot_info_mapping(self, idx: int) -> bool:
        if (idx - 77) % 101 != 0:
            return False
        is_christmas_tree = False
        # reset the map each iteration for part 2
        self.robot_map: list[list[str]] = [
            ["." for _ in range(self.num_tiles_wide)] for _ in range(self.num_tiles_tall)
        ]
        robot_ids: dict[tuple[int, int], list[str]] = defaultdict(list)
        for robot_id, robot_info in self.robot_info_mapping.items():
            x_pos = robot_info.x_pos
            y_pos = robot_info.y_pos
            if self.robot_map[y_pos][x_pos] == ".":
                self.robot_map[y_pos][x_pos] = "1"
            else:
                num_robots_at_cell = int(self.robot_map[y_pos][x_pos])
                num_robots_at_cell += 1
                self.robot_map[y_pos][x_pos] = str(num_robots_at_cell)

            # robot_ids[(y_pos, x_pos)].append(str(robot_id))

        visualize_robot_map(
            self.robot_map,
            idx,
            robot_ids,
        )
        return is_christmas_tree

    def simulate_all_robot_movements(self, num_seconds: int, show_map: bool = False) -> None:
        for curr_second in range(num_seconds):
            is_christmas_tree = self.visualize_map_from_robot_info_mapping(curr_second)
            self.simulate_all_robot_movements_one_second()
            if show_map:
                pass
                # visualize_robot_map(self.robot_map)
                # if is_christmas_tree:
                #     print(f"Found christmas tree at second {curr_second}")
                #     break

    def score(self) -> int:
        total_robot_map_score = 0
        half_width = NUM_TILES_WIDE // 2
        half_height = NUM_TILES_TALL // 2
        quadrants = {
            # so for an 11 by 7 q1 would be (0, 0) to (5, 3)
            # q2 would be (6, 0) to (10, 3)
            # q3 would be (0, 4) to (5, 6)
            "q1": [(0, 0), (half_width, half_height)],
            "q2": [(half_width, 0), (NUM_TILES_WIDE, half_height)],
            "q3": [(0, NUM_TILES_TALL // 2), (half_width, NUM_TILES_TALL)],
            "q4": [(half_width, half_height), (NUM_TILES_WIDE, NUM_TILES_TALL)],
        }
        quadrant_scores = {
            "q1": 0,
            "q2": 0,
            "q3": 0,
            "q4": 0,
        }
        for quadrant, (start, end) in quadrants.items():
            for row_idx in range(start[1], end[1]):
                for col_idx in range(start[0], end[0]):
                    cell = self.robot_map[row_idx][col_idx]
                    if row_idx == half_height:
                        continue

                    if col_idx == half_width:
                        continue

                    if cell == ".":
                        continue

                    if int(cell) > 0:
                        quadrant_scores[quadrant] += int(cell)

        pprint(quadrant_scores)
        total_robot_map_score = math.prod(quadrant_scores.values())
        return total_robot_map_score


def soln(input_file: Path) -> tuple[int, int]:
    part1_robot_sum = 0
    part2_robot_sum = 0

    robot_map_pt1 = RobotMap(NUM_TILES_WIDE, NUM_TILES_TALL)
    all_robot_info = []
    with open(input_file, "r") as file:
        lines = [line.strip() for line in file.readlines() if line.strip()]
        for line in lines:
            robot_info = parse_robot_line(line)
            all_robot_info.append(robot_info)

            final_robot_x_pos, final_robot_y_pos = robot_map_pt1.simulate_robot_movement(
                robot_info, NUM_SECONDS_TO_SIMULATE
            )
            robot_map_pt1.add_robot(final_robot_x_pos, final_robot_y_pos)

        part1_robot_sum = robot_map_pt1.score()

    # Ok now we can change our approach slightly for part 2
    # we are going to have to place all the robots initially and then tag them with some unique id
    # and then simulate their movements one at a a time
    # so it does get a smidge more complex
    # let's instantiate a new robot map that has all of the robots locations in
    # the initializer
    robot_map_pt2 = RobotMap.init_with_robots(NUM_TILES_WIDE, NUM_TILES_TALL, all_robot_info)
    robot_map_pt2.simulate_all_robot_movements(MAX_NUM_SECONDS_TO_SIMULATE, show_map=True)
    return (part1_robot_sum, part2_robot_sum)


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    if TEST_CASE == "small":
        input_file = curr_dir.parent / "inputs" / "day14_small.txt"
    else:
        input_file = curr_dir.parent / "inputs" / "day14.txt"
    # input_file = curr_dir.parent / "inputs" / "day14.txt"
    print(soln(input_file))
