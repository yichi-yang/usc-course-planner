import bisect
import pickle


def interval_intersect(i1, i2):
    if(i1 < i2):
        return i1[1] > i2[0]
    else:
        return i2[1] > i1[0]


class curve_eval:
    def __init__(self, curve):
        self.curve = curve

    def calc(self, time):
        loc = bisect.bisect(self.curve, (time, 0))
        if loc - 1 < 0 or loc >= len(self.curve):
            return 0
        else:
            return (self.curve[loc - 1][1] + (self.curve[loc][1] - self.curve[loc - 1][1])
                    * (time - self.curve[loc - 1][0]) / (self.curve[loc][0] - self.curve[loc - 1][0]))


class req_break:
    def __init__(self, start_end, length, penalty):
        self.start_end = start_end
        self.length = length
        self.penalty = penalty


def evaluate_combination(sections, early_curve, late_curve, interval_curve, required_breaks):
    cost = 0
    time_tables = [[], [], [], [], []]
    early_eval = curve_eval(early_curve)
    late_eval = curve_eval(late_curve)
    interval_eval = curve_eval(interval_curve)
    for section in sections:
        if section.apply_penalty:
            for day in section.days_list:
                bisect.insort(time_tables[day], section.start_end)
    for time_table in time_tables:
        class_start = time_table[0][0] if time_table else 1440
        class_end = time_table[len(time_table) - 1][1] if time_table else 0
        cost -= early_eval.calc(class_start)
        cost -= late_eval.calc(class_end)
        breaks_satisfied = [req_break.start_end[0] <= class_start
                            or req_break.start_end[1] >= class_end
                            for req_break in required_breaks]
        for i in range(len(time_table) - 1):
            interval = (time_table[i][1], time_table[i + 1][0])
            interval_len = interval[1] - interval[0]
            is_req_break = False
            for i in range(len(required_breaks)):
                if (interval_intersect(interval, required_breaks[i].start_end)
                        and interval_len >= required_breaks[i].length):
                    breaks_satisfied[i] = True
                    is_req_break = True
                    break
            if not is_req_break:
                cost -= interval_eval.calc(interval_len)
        for i in range(len(required_breaks)):
            if not breaks_satisfied[i]:
                cost -= required_breaks[i].penalty
    return cost


if __name__ == '__main__':
    with open("one_combination.pickle", "rb") as ifile:
        sections = pickle.load(ifile)

    early_c = [(0, 19), (570, 0)]
    late_c = [(840, 0), (1440, 10)]
    interval_c = [(10, 0), (1440, 12)]
    breaks = [req_break((720, 780), 45, 4), req_break((1020, 1110), 45, 8)]

    print(evaluate_combination(sections, early_c, late_c, interval_c, breaks))
