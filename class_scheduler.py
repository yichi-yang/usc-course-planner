from load_class import load_class
from section import Section
import pickle
import itertools


def interval_comp(interval_session_pair):
    return interval_session_pair[0]


classes = ["csci-201", "csci-270", "easc-150", "ee-109", "itp-125"]

# all_classes = {}

# for curr_class in classes:
#     all_classes[curr_class] = load_class(
#         curr_class, "https://classes.usc.edu/term-20193/course/")

# with open("class.pickle", "wb") as ofile:
#     pickle.dump(all_classes, ofile)

with open("class.pickle", "rb") as ifile:
    all_classes = pickle.load(ifile)

section_iters = []

for curr_class in all_classes.values():
    for sections in curr_class.values():
        section_iters.append(iter(sections))

count = 0
valid_count = 0
for combo in itertools.product(*section_iters):
    time_tables = [[], [], [], [], []]
    for session in combo:
        for day in session.days_list:
            time_tables[day].append((session.start_end, session.apply_penalty))
    valid = True
    for time_table in time_tables:
        time_table.sort(key = interval_comp)
        for i in range(len(time_table) - 1):
            if time_table[i][0][1] > time_table[i + 1][0][0]:
                valid = False
                break
        if not valid:
            break
    if valid:
        valid_count += 1
        # print(intervals)
        # for session in combo:
        #     print(session)
        # print()
        print(str(valid_count) + " / " + str(count))
    count += 1

print(count)
