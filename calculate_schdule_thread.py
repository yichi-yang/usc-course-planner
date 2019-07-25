from PyQt5.QtCore import QThread, pyqtSignal
from load_class import load_class
from evaluate_time_table import evaluate_combination
import heapq
import bisect


class CalcScheduleThread(QThread):
    results_ready = pyqtSignal(QThread)
    update_count = pyqtSignal(int)

    def __init__(self, sections, early_curve, late_curve, interval_curve, required_breaks):
        super().__init__()
        self.sections = sections
        self.early_curve = early_curve
        self.late_curve = late_curve
        self.interval_curve = interval_curve
        self.required_breaks = required_breaks
        self.last_count = 0
        self.count = 0
        self.best = []

    def run(self):
        self.valid_combinations(self.sections)
        self.results_ready.emit(self)

    def valid_combinations(self, section_lists, selected=None, count=0, time_tables=None):
        if selected is None:
            selected = []
        if time_tables is None:
            time_tables = [[], [], [], [], []]

        if count >= len(section_lists):
            early_cost, late_cost, interval_cost, break_cost = evaluate_combination(
                selected, self.early_curve, self.late_curve, self.interval_curve, self.required_breaks)
            total = early_cost + late_cost + interval_cost + break_cost
            if len(self.best) < 50:
                heapq.heappush(self.best, (-total, selected.copy(),
                                           early_cost, late_cost, interval_cost, break_cost))
            elif -total >= self.best[0][0]:
                heapq.heappushpop(self.best, (-total, selected.copy(),
                                              early_cost, late_cost, interval_cost, break_cost))
            self.count += 1
            if self.count - self.last_count > 500:
                self.last_count = self.count
                self.update_count.emit(self.last_count)
            return

        for section in section_lists[count]:
            time_tables_copy = [time_table.copy()
                                for time_table in time_tables]
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
                self.valid_combinations(
                    section_lists, selected, count + 1, time_tables_copy)
                selected.pop(len(selected) - 1)
