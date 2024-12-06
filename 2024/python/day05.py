"""
Okieeeee so...

basically, we get the rules in the first set of input, and then we get the pages
and we need to verify the printer updates.

We also need to check the correct printer update lines for each middle number.

I think this is one of the first solutions where we can just process online rather than read the whole input, but maybe I've been being lazy in the past, and we should have streamed it earlier.

So I guess I was originally thinking some graph approach, but I think it's even easier than
that and we can just keep a rules_dict and then check the pages against that.

---

Ok so walking through an example... and flushing out my algo more.

we really want to say - like for this line:

75,47,61,53,29

so we see 75, we haven't seen anything yet, we know that's ok
we then see 47, we have already seen 75, so we need to ensure that for 47's rules that
75 is allowed to go before.
we know it is because we have seen 75 | 47, which states that 75 can go before 47.
also **only some of the ordering rules apply** and that's totally fine.

Maybe a better way to think about it is:
if we see 47 first, then we think that's ok, but then we get to 75 and we
see that for 75 it has to come before 47, so we know that's not ok.

so then we return False there. and then we keep going.

So my idea is to store [num] -> set([nums])
basically existing value -> numbers we can't see before
which kinda makes sense with the order of operations that they give it to us in.

-----
nice part 1 not too bad

part 2, ok so now i think we need to keep track of the pages
that are allowed given a number that we're currently at and
maybe we try to build from the back to the front?

almost like some sort of bubble up algo
"""

from collections import defaultdict
from pathlib import Path

from timing_util import TimeUnit, TimingOptions, time_solution


def fix_broken_printer_update_bubble_up(
    printer_update_list: list[int], not_allowed_rules: dict[int, set[int]]
) -> list[int]:
    """We're basically going to just move the most broken rules to the back,
    kinda like a weird bubble sort."""
    sorted_printer_updates = printer_update_list.copy()
    sorted_printer_updates = []
    for page in printer_update_list:
        inserted = False
        for idx in range(len(sorted_printer_updates)):
            if page in not_allowed_rules.get(sorted_printer_updates[idx], set()):
                # so here we're basically saying
                # if the current page is not allowed to go before the next one
                # then we need to insert it before the next one
                sorted_printer_updates.insert(idx, page)
                inserted = True
                break
        if not inserted:
            sorted_printer_updates.append(page)
    # print("printer_update_list", printer_update_list)
    # print("not_allowed_rules", not_allowed_rules)
    # print("sorted_printer_updates", sorted_printer_updates)
    return sorted_printer_updates


def soln(input_file: Path) -> tuple[int, int]:
    sum_of_middle_num_for_valid_page_updates = 0
    sum_of_middle_num_for_fixed_pages = 0
    # so in our example, this is 75 -> {47}
    page_to_not_allowed_before_pages: dict[int, set[int]] = defaultdict(set)

    with open(input_file, "r") as f:
        for line in f:
            if "|" in line:
                # we're in the rule building section
                rule, page = line.strip().split("|")
                page_to_not_allowed_before_pages[int(rule)].add(int(page))

            if "," in line:
                # we're in the printer update section
                pages_to_process = list(map(int, line.strip().split(",")))
                seen_pages = set()
                length_of_update = len(pages_to_process)
                valid_page = True
                for page in pages_to_process:
                    if page in page_to_not_allowed_before_pages:
                        not_allowed_pages = page_to_not_allowed_before_pages[page]

                        # now we need to ensure all the ones we've seen so far
                        # are allowed
                        if seen_pages.intersection(not_allowed_pages):
                            valid_page = False
                            break

                    if not valid_page:
                        break
                    seen_pages.add(page)

                if valid_page:
                    sum_of_middle_num_for_valid_page_updates += pages_to_process[length_of_update // 2]
                else:
                    # Ok so now for part 2 if we get here,
                    # then we have to correct it in accordance with the rules
                    # and then compute the middle number
                    corrected_list = fix_broken_printer_update_bubble_up(
                        pages_to_process, page_to_not_allowed_before_pages
                    )
                    sum_of_middle_num_for_fixed_pages += corrected_list[length_of_update // 2]

        return sum_of_middle_num_for_valid_page_updates, sum_of_middle_num_for_fixed_pages


if __name__ == "__main__":
    curr_dir = Path(__file__).parent
    input_file = curr_dir.parent / "inputs" / "day05.txt"
    time_solution("day05", soln, input_file, method=TimingOptions.AVERAGE, unit=TimeUnit.MILLISECONDS, iterations=10)
