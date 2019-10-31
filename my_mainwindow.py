from ui_mainwindow import Ui_MainWindow
from class_tree_model import ClassTreeModel
from load_course_thread import LoadClassThread
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QTreeWidgetItem, QShortcut
from PyQt5.QtCore import QTime, Qt, QModelIndex
from PyQt5.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from evaluate_time_table import parse_ELI_penalty, parse_req_breaks, req_break
from calculate_schdule_thread import CalcScheduleThread
import heapq


class My_MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.tree_model = None
        self.running_threads = set()
        self.downloaded_class = set()
        self.best_schedules = []
        self.solve_schedule_thread = None
        self.req_breaks = []

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.tree_model = ClassTreeModel()
        self.treeView.setModel(self.tree_model)
        self.treeView.setColumnWidth(0, 180)
        self.treeView.setColumnWidth(1, 80)
        self.treeView.setColumnWidth(2, 80)
        self.treeView.setColumnWidth(6, 80)

        # signals to add courses
        self.addClassButton.clicked.connect(self.retrieve_class_on_click)
        self.classNameLineEdit.returnPressed.connect(
            self.retrieve_class_on_click)

        # set up schedule ploting area
        self.plot_canvas = FigureCanvas(Figure(figsize=(12, 6)))
        self.plot_canvas.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scheduleTabHorizontalLayout.addWidget(self.plot_canvas)
        self.plot_ax = self.plot_canvas.figure.subplots()
        self.show_time_table()

        # signals to update schedules calculations
        self.updatPushButton.clicked.connect(self.calculate_schedules)

        # signals to handle schedule list selection
        self.scheduleScoreTreeWidget.itemSelectionChanged.connect(
            self.handle_score_list_selection)

        # signals to handle policy page actions
        self.earlyPenaltyLineEdit.textEdited.connect(
            self.handle_early_penalty_line_edit_change)
        self.latePenaltyLineEdit.textEdited.connect(
            self.handle_late_penalty_line_edit_change)
        self.intervalPenaltyLineEdit.textChanged.connect(
            self.handle_interval_penalty_line_edit_change)
        self.requiredBreaksLineEdit.textChanged.connect(
            self.handle_breaks_line_edit_change)
        self.addBreakPushButton.clicked.connect(self.add_required_breaks)

        self.delete_break_short_cut = QShortcut(
            QKeySequence(QKeySequence.Delete), self.breakTreeWidget)
        self.delete_break_short_cut.setContext(Qt.WidgetShortcut)
        self.delete_break_short_cut.activated.connect(
            self.delete_selected_break)

        self.delete_course_short_cut = QShortcut(
            QKeySequence(QKeySequence.Delete), self.treeView)
        self.delete_course_short_cut.setContext(Qt.WidgetShortcut)
        self.delete_course_short_cut.activated.connect(
            self.delete_selected_course)

    def retrieve_class_on_click(self):
        term = self.termLineEdit.text()
        class_name = self.classNameLineEdit.text().upper()
        url = 'https://classes.usc.edu/term-' + term + '/course/' + class_name + '/'

        if class_name in self.downloaded_class:
            QMessageBox(QMessageBox.Warning, "Already Exists",
                        class_name + " already exists.", QMessageBox.Close).exec()
            return

        self.downloaded_class.add(class_name)
        thread = LoadClassThread(url, class_name)
        self.running_threads.add(thread)
        thread.results_ready.connect(self.add_class)
        msg = "Downloading"
        for running_thread in self.running_threads:
            msg += " " + running_thread.name
        msg += " ..."
        self.statusBar.showMessage(msg)
        thread.start()

    def add_class(self, thread):
        self.running_threads.remove(thread)
        if self.running_threads:
            msg = "Downloading"
            for running_thread in self.running_threads:
                msg += " " + running_thread.name
            msg += " ..."
            self.statusBar.showMessage(msg)
        else:
            self.statusBar.clearMessage()
        if thread.root is None:
            QMessageBox(QMessageBox.Warning, "Download Failed",
                        "Invalid term / course name or bad Internet connection.\n" + thread.url, QMessageBox.Close).exec()
            self.downloaded_class.remove(thread.name)
            return
        self.tree_model.add_top_level_child(thread.root)

    def show_time_table(self, sections=None):

        if sections is None:
            sections = []

        self.plot_ax.clear()
        for section in sections:
            for day in section.days_list:
                bar_bottom = section.start_end[0]
                bar_height = section.start_end[1] - section.start_end[0]
                self.plot_ax.bar(day, bar_height, width=0.92,
                                 bottom=bar_bottom, linewidth=0, fc='#3CA730')
                description = (section.name
                               + " " + section.section_id + " "
                               + section.section_type[:4])
                self.plot_ax.text(day, bar_bottom + bar_height / 2, description,
                                  horizontalalignment='center', verticalalignment='center',
                                  fontfamily='Nirmala UI', color='white', fontsize='medium')

        self.plot_ax.set_axisbelow(True)
        self.plot_ax.minorticks_on()
        self.plot_ax.set_xticks([0, 1, 2, 3, 4])
        self.plot_ax.set_xticks([0.5, 1.5, 2.5, 3.5], minor=True)
        self.plot_ax.set_yticks(range(5*60, 24*60, 60))
        self.plot_ax.set_yticklabels(
            [str(time) + ":00" for time in range(5, 24)], fontfamily='Nirmala UI')
        self.plot_ax.set_yticks(range(5*60 + 30, 24*60, 60), minor=True)
        self.plot_ax.set_xlim(-0.5, 4.5)
        self.plot_ax.set_ylim(23*60, 5*60)
        self.plot_ax.xaxis.tick_top()
        self.plot_ax.set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri"],
                                     fontfamily='Nirmala UI', fontsize='x-large')

        # ax.grid(which = 'major', visible = False)
        self.plot_ax.grid(which='minor', axis='x', linewidth=0.5, alpha=0.8)
        self.plot_ax.grid(which='major', axis='y', linewidth=0.5, alpha=0.8)
        self.plot_ax.grid(which='minor', axis='y', linewidth=0.5, alpha=0.3)
        self.plot_ax.tick_params(which='both', top=False,  left=False,
                                 right=False, bottom=False)
        self.plot_ax.spines['bottom'].set_color("#bababa")
        self.plot_ax.spines['top'].set_color("#bababa")
        self.plot_ax.spines['left'].set_color("#bababa")
        self.plot_ax.spines['right'].set_color("#bababa")
        self.plot_canvas.draw()

    def calculate_schedules(self):
        list_of_componets = []
        self.tree_model.lock(True)
        for course in self.tree_model.root.data:
            if not course.is_included():
                continue
            for component in course.data:
                if not component.is_included():
                    continue
                list_of_sections = [
                    section.data for section in component.data if section.data.include]
                list_of_componets.append(list_of_sections)

        if not list_of_componets:
            self.tree_model.lock(False)
            QMessageBox(QMessageBox.Warning, "No Course Selected",
                        "Cannot make schedules since no course is selected.", QMessageBox.Close).exec()
            return

        if self.earlyHorizontalSlider.isEnabled():
            time = qtime2minutes(self.earlyTimeEdit.time())
            penalty = self.earlyHorizontalSlider.value() / 1000
            early_curve = [(0, penalty * time), (time, 0)]
        else:
            early_curve = parse_ELI_penalty(self.earlyPenaltyLineEdit.text())
            if early_curve is None:
                QMessageBox(QMessageBox.Warning, "Invalid Early Penalty",
                            self.earlyPenaltyLineEdit.text() + " isn't valid.", QMessageBox.Close).exec()
                self.tree_model.lock(False)
                return

        if self.lateHorizontalSlider.isEnabled():
            time = qtime2minutes(self.lateTimeEdit.time())
            penalty = self.lateHorizontalSlider.value() / 1000
            late_curve = [(time, 0), (1440, penalty * (1440 - time))]
        else:
            late_curve = parse_ELI_penalty(self.latePenaltyLineEdit.text())
            if late_curve is None:
                QMessageBox(QMessageBox.Warning, "Invalid Late Penalty",
                            self.latePenaltyLineEdit.text() + " isn't valid.", QMessageBox.Close).exec()
                self.tree_model.lock(False)
                return

        if self.intervalHorizontalSlider.isEnabled():
            time = qtime2minutes(self.intervalTimeEdit.time())
            penalty = self.intervalHorizontalSlider.value() / 1000
            interval_curve = [(time, 0), (1440, penalty * (1440 - time))]
        else:
            interval_curve = parse_ELI_penalty(
                self.intervalPenaltyLineEdit.text())
            if interval_curve is None:
                QMessageBox(QMessageBox.Warning, "Invalid Interval Penalty",
                            self.intervalPenaltyLineEdit.text() + " isn't valid.", QMessageBox.Close).exec()
                self.tree_model.lock(False)
                return

        if self.breakTreeWidget.isEnabled():
            req_breaks = self.req_breaks
        else:
            req_breaks = parse_req_breaks(self.requiredBreaksLineEdit.text())
            if req_breaks is None:
                QMessageBox(QMessageBox.Warning, "Invalid Required Breaks",
                            self.requiredBreaksLineEdit.text() + " isn't valid.", QMessageBox.Close).exec()
                self.tree_model.lock(False)
                return

        self.solve_schedule_thread = CalcScheduleThread(
            list_of_componets, early_curve, late_curve, interval_curve, req_breaks)

        self.solve_schedule_thread.results_ready.connect(
            self.handle_schedule_calc_results)
        self.solve_schedule_thread.update_count.connect(
            self.handle_schedule_calc_update)

        self.scheduleScoreTreeWidget.clear()
        self.scheduleDetailsTreeWidget.clear()
        self.solve_schedule_thread.start()

    def handle_schedule_calc_results(self, thread):
        self.tree_model.lock(False)
        if thread.best:
            self.best_schedules = []
            while thread.best:
                self.best_schedules.append(heapq.heappop(thread.best))
            self.best_schedules.reverse()
            num_score_pair_list = []
            for i in range(len(self.best_schedules)):
                fields = []
                fields.append(str(i + 1))
                fields.append(str("{:.2f}".format(-self.best_schedules[i][0])))
                fields.append(str("{:.2f}".format(self.best_schedules[i][2])))
                fields.append(str("{:.2f}".format(self.best_schedules[i][3])))
                fields.append(str("{:.2f}".format(self.best_schedules[i][4])))
                fields.append(str("{:.2f}".format(self.best_schedules[i][5])))
                num_score_pair_list.append(QTreeWidgetItem(None, fields))
            self.scheduleScoreTreeWidget.insertTopLevelItems(
                0, num_score_pair_list)
        del self.solve_schedule_thread

    def handle_schedule_calc_update(self, count):
        self.statusBar.showMessage(
            "Solving for best schedules... {} valid schedules found.".format(count), 1000)

    def handle_score_list_selection(self):
        selected = self.scheduleScoreTreeWidget.selectedItems()
        if selected:
            index = self.scheduleScoreTreeWidget.indexOfTopLevelItem(
                selected[0])
            if index >= 0 and index < len(self.best_schedules):
                self.show_schedule_details(self.best_schedules[index][1])
                self.show_time_table(self.best_schedules[index][1])

    def show_schedule_details(self, schedule):
        section_item_list = []
        for section in schedule:
            fields = []
            fields.append(section.name)
            fields.append(section.section_type)
            fields.append(section.section_id)
            fields.append(section.time)
            fields.append(section.days)
            fields.append(section.registered)
            fields.append("X" if section.closed else "")
            fields.append(section.instructor)
            fields.append(section.location)
            section_item_list.append(QTreeWidgetItem(None, fields))
        self.scheduleDetailsTreeWidget.clear()
        self.scheduleDetailsTreeWidget.insertTopLevelItems(
            0, section_item_list)

    def handle_early_penalty_line_edit_change(self, text):
        if text:
            self.earlyHorizontalSlider.setEnabled(False)
            self.earlyTimeEdit.setEnabled(False)
            if parse_ELI_penalty(text):
                self.earlyPenaltyLineEdit.setStyleSheet(
                    "background-color: #b6fac2")
            else:
                self.earlyPenaltyLineEdit.setStyleSheet(
                    "background-color: #fab6b6")
        else:
            self.earlyHorizontalSlider.setEnabled(True)
            self.earlyTimeEdit.setEnabled(True)
            self.earlyPenaltyLineEdit.setStyleSheet("")

    def handle_late_penalty_line_edit_change(self, text):
        if text:
            self.lateHorizontalSlider.setEnabled(False)
            self.lateTimeEdit.setEnabled(False)
            if parse_ELI_penalty(text):
                self.latePenaltyLineEdit.setStyleSheet(
                    "background-color: #b6fac2")
            else:
                self.latePenaltyLineEdit.setStyleSheet(
                    "background-color: #fab6b6")
        else:
            self.lateHorizontalSlider.setEnabled(True)
            self.lateTimeEdit.setEnabled(True)
            self.latePenaltyLineEdit.setStyleSheet("")

    def handle_interval_penalty_line_edit_change(self, text):
        if text:
            self.intervalHorizontalSlider.setEnabled(False)
            self.intervalTimeEdit.setEnabled(False)
            if parse_ELI_penalty(text):
                self.intervalPenaltyLineEdit.setStyleSheet(
                    "background-color: #b6fac2")
            else:
                self.intervalPenaltyLineEdit.setStyleSheet(
                    "background-color: #fab6b6")
        else:
            self.intervalHorizontalSlider.setEnabled(True)
            self.intervalTimeEdit.setEnabled(True)
            self.intervalPenaltyLineEdit.setStyleSheet("")

    def handle_breaks_line_edit_change(self, text):
        if text:
            self.addBreakPushButton.setEnabled(False)
            self.breakHorizontalSlider.setEnabled(False)
            self.breakStartTimeEdit.setEnabled(False)
            self.breakEndTimeEdit.setEnabled(False)
            self.breakLenTimeEdit.setEnabled(False)
            self.breakTreeWidget.setEnabled(False)
            if parse_req_breaks(text):
                self.requiredBreaksLineEdit.setStyleSheet(
                    "background-color: #b6fac2")
            else:
                self.requiredBreaksLineEdit.setStyleSheet(
                    "background-color: #fab6b6")
        else:
            self.addBreakPushButton.setEnabled(True)
            self.breakHorizontalSlider.setEnabled(True)
            self.breakStartTimeEdit.setEnabled(True)
            self.breakEndTimeEdit.setEnabled(True)
            self.breakLenTimeEdit.setEnabled(True)
            self.breakTreeWidget.setEnabled(True)
            self.requiredBreaksLineEdit.setStyleSheet("")

    def add_required_breaks(self):
        start = qtime2minutes(self.breakStartTimeEdit.time())
        end = qtime2minutes(self.breakEndTimeEdit.time())
        penalty = self.breakHorizontalSlider.value() / 5
        length = qtime2minutes(self.breakLenTimeEdit.time())
        if start > end:
            start, end = end, start
        self.req_breaks.append(req_break((start, end), length, penalty))
        self.breakTreeWidget.clear()
        break_item_list = []
        for some_break in self.req_breaks:
            fields = []
            fields.append(minutes2str(some_break.start_end[0]))
            fields.append(minutes2str(some_break.start_end[1]))
            fields.append(minutes2str(some_break.length))
            fields.append(str(some_break.penalty))
            break_item_list.append(QTreeWidgetItem(None, fields))
        self.breakTreeWidget.insertTopLevelItems(0, break_item_list)

    def delete_selected_break(self):
        selected = self.breakTreeWidget.selectedItems()
        if not selected:
            return
        index = self.breakTreeWidget.indexOfTopLevelItem(selected[0])
        if index < len(self.req_breaks):
            self.req_breaks.pop(index)
        self.breakTreeWidget.clear()
        break_item_list = []
        for some_break in self.req_breaks:
            fields = []
            fields.append(minutes2str(some_break.start_end[0]))
            fields.append(minutes2str(some_break.start_end[1]))
            fields.append(minutes2str(some_break.length))
            fields.append(str(some_break.penalty))
            break_item_list.append(QTreeWidgetItem(None, fields))
        self.breakTreeWidget.insertTopLevelItems(0, break_item_list)

    def delete_selected_course(self):
        selected = self.treeView.selectedIndexes()
        if selected and self.tree_model.parent(selected[0]) == QModelIndex():
            name = self.tree_model.delete_top_level_child(selected[0].row())
            if name in self.downloaded_class:
                self.downloaded_class.remove(name)


def qtime2minutes(qtime):
    return int(qtime.hour() * 60 + qtime.minute())


def minutes2str(minutes):
    return "{:02d}:{:02d}".format(minutes // 60, minutes % 60)
