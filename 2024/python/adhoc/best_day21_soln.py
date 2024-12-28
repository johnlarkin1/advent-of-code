import sys
from functools import cache
from itertools import permutations

with open(sys.argv[1] if len(sys.argv) > 1 else "2024/inputs/day21.txt") as f:
    codes = f.read().splitlines()

numkeypad = ["789", "456", "123", " 0A"]
numkeypad = {key: (x, y) for y, line in enumerate(numkeypad) for x, key in enumerate(line) if key != " "}
print(numkeypad)

dirkeypad = [" ^A", "<v>"]
dirkeypad = {key: (x, y) for y, line in enumerate(dirkeypad) for x, key in enumerate(line) if key != " "}
print(dirkeypad)

dirs = {"^": (0, -1), ">": (1, 0), "v": (0, 1), "<": (-1, 0)}


@cache
def get_presses(sequence, depth=2, dirkey=False, cur=None):
    keypad = dirkeypad if dirkey else numkeypad

    if not sequence:
        return 0

    if not cur:
        cur = keypad["A"]  # default starting position is the "A" key

    # Current coordinates
    cx, cy = cur
    # Coordinates for the next key we want to press
    px, py = keypad[sequence[0]]

    # Calculate how many steps horizontally (dx) and vertically (dy)
    dx, dy = px - cx, py - cy

    # Build the string of direction buttons needed (naive direct path)
    # - e.g., if dx = 2, you need to press ">" twice.
    #   if dy = -1, you need to press "^" once, etc.
    buttons = ">" * dx + "<" * -dx + "v" * dy + "^" * -dy

    # If depth is nonzero, try permuting the route to see if there's a shorter path
    # once we consider that we can use the "directional keypad" version.
    if depth:
        perm_lens = []
        for perm in set(permutations(buttons)):
            # Check if pressing direction buttons in this permutation
            # is valid (i.e., doesn't move outside of our keypad).
            cx2, cy2 = cx, cy
            for button in perm:
                dx2, dy2 = dirs[button]
                cx2 += dx2
                cy2 += dy2
                if (cx2, cy2) not in keypad.values():
                    break
            else:
                # If we never broke out of the loop, the path is valid.
                # Then we do get_presses(..., depth-1, True) for the path perm + ("A",)
                # effectively counting the cost to press these direction keys and finalize with "A".
                perm_lens.append(get_presses(perm + ("A",), depth - 1, True))

        # If any valid permutation was found, choose the minimum length route
        # from those permutations.
        min_len = min(perm_lens)
    else:
        # If depth = 0, we stop permuting and just take the length of the direct path + 1
        min_len = len(buttons) + 1

    # Now combine the cost of pressing this key with the cost of the rest of the sequence
    return min_len + get_presses(sequence[1:], depth, dirkey, (px, py))


p1 = 0
p2 = 0
for code in codes:
    codenum = int(code[:-1])
    p1 += codenum * get_presses(code)
    p2 += codenum * get_presses(code, 25)

print(p1)
print(p2)
