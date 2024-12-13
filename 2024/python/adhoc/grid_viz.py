from rich.console import Console
from rich.text import Text


def create_wall_grid(walls):
    # Convert walls to easier lookup format
    wall_lookup = {}
    for (x, y), direction in walls:
        if (x, y) not in wall_lookup:
            wall_lookup[(x, y)] = set()
        wall_lookup[(x, y)].add(direction)

    size = 6
    console = Console()

    # Print column numbers
    console.print("     " + "   ".join(f"[bold]{i}[/bold]" for i in range(size)))

    for i in range(size):
        # Top border of each cell
        top_row = Text("    ")  # Indent for row numbers
        for j in range(size):
            cell_top = "▄▄▄▄▄" if (i, j) in wall_lookup and "up" in wall_lookup[(i, j)] else "     "
            top_row.append(
                cell_top, style="white on red" if (i, j) in wall_lookup and "up" in wall_lookup[(i, j)] else ""
            )
        console.print(top_row)

        # Middle row of each cell with row numbers
        middle_row = Text(f"{i}  ", style="bold")  # Row number
        for j in range(size):
            left = "█" if (i, j) in wall_lookup and "left" in wall_lookup[(i, j)] else " "
            right = "█" if (i, j) in wall_lookup and "right" in wall_lookup[(i, j)] else " "
            middle_row.append(
                left, style="white on red" if (i, j) in wall_lookup and "left" in wall_lookup[(i, j)] else ""
            )
            middle_row.append("   ")
            middle_row.append(
                right, style="white on red" if (i, j) in wall_lookup and "right" in wall_lookup[(i, j)] else ""
            )
        console.print(middle_row)

        # Bottom border of each cell
        bottom_row = Text("    ")  # Indent for row numbers
        for j in range(size):
            cell_bottom = "▀▀▀▀▀" if (i, j) in wall_lookup and "down" in wall_lookup[(i, j)] else "     "
            bottom_row.append(
                cell_bottom, style="white on red" if (i, j) in wall_lookup and "down" in wall_lookup[(i, j)] else ""
            )
        console.print(bottom_row)


# Your input data
walls = {
    ((0, 0), "left"),
    ((0, 0), "up"),
    ((0, 1), "up"),
    ((0, 2), "up"),
    ((0, 3), "down"),
    ((0, 3), "up"),
    ((0, 4), "down"),
    ((0, 4), "up"),
    ((0, 5), "right"),
    ((0, 5), "up"),
    ((1, 0), "left"),
    ((1, 2), "right"),
    ((1, 5), "left"),
    ((1, 5), "right"),
    ((2, 0), "left"),
    ((2, 1), "down"),
    ((2, 2), "down"),
    ((2, 2), "right"),
    ((2, 5), "left"),
    ((2, 5), "right"),
    ((3, 0), "left"),
    ((3, 0), "right"),
    ((3, 3), "left"),
    ((3, 3), "up"),
    ((3, 4), "up"),
    ((3, 5), "right"),
    ((4, 0), "left"),
    ((4, 0), "right"),
    ((4, 3), "left"),
    ((4, 5), "right"),
    ((5, 0), "down"),
    ((5, 0), "left"),
    ((5, 1), "down"),
    ((5, 1), "up"),
    ((5, 2), "down"),
    ((5, 2), "up"),
    ((5, 3), "down"),
    ((5, 4), "down"),
    ((5, 5), "down"),
    ((5, 5), "right"),
}

create_wall_grid(walls)
