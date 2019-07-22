from section import Section
from load_class import load_class
import bisect
import pickle
from evaluate_time_table import evaluate_combination, req_break
import heapq
from time_table_visualizer import show_time_table

early_c = [(0, 19), (570, 0)]
late_c = [(840, 0), (1440, 10)]
interval_c = [(10, 0), (1440, 12)]
breaks = [req_break((720, 780), 45, 4), req_break((1020, 1110), 45, 8)]


def valid_combinations(section_lists, best, selected=[], count=0, time_tables=[[], [], [], [], []]):
    if count >= len(section_lists):
        score = evaluate_combination(selected, early_c,
                                     late_c, interval_c, breaks)
        if len(best) < 20:
            heapq.heappush(best, (score, selected.copy()))
        elif score >= best[0][0]:
            heapq.heappushpop(best, (score, selected.copy()))
        return 1

    total = 0
    for section in section_lists[count]:
        time_tables_copy = [time_table.copy() for time_table in time_tables]
        valid = True
        for day in section.days_list:
            loc = bisect.bisect(time_tables_copy[day], section.start_end)
            if ((loc - 1 >= 0 and time_tables_copy[day][loc - 1][1] > section.start_end[0])
                    or (loc < len(time_tables_copy[day])) and section.start_end[1] > time_tables_copy[day][loc][0]):
                valid = False
                break
            time_tables_copy[day].insert(loc, section.start_end)
        if valid:
            selected.append(section)
            total += valid_combinations(section_lists, best,
                                        selected, count + 1, time_tables_copy)
            selected.pop(len(selected) - 1)
    return total


if __name__ == '__main__':
    classes = ["csci-201", "csci-270", "easc-150", "ee-109", "itp-125"]

    # all_classes = {}

    # for curr_class in classes:
    #     all_classes[curr_class] = load_class(
    #         curr_class, "https://classes.usc.edu/term-20193/course/")

    # with open("class.pickle", "wb") as ofile:
    #     pickle.dump(all_classes, ofile)

    with open("class.pickle", "rb") as ifile:
        all_classes = pickle.load(ifile)

    section_lists = []

    for curr_class in all_classes.values():
        for sections in curr_class.values():
            section_lists.append(sections)

    best = []
    count = valid_combinations(section_lists, best)
    for score_combination_pair in reversed(best):
        show_time_table(score_combination_pair[1])
