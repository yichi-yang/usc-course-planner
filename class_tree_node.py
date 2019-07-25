from PyQt5.QtCore import Qt
from section import Section

class ClassTreeNode:
    def __init__(self, name, parent, data=None):
        self.name = name
        self.data = data if data else []
        self.parent = parent

    def row_index_of(self):
        if self.parent:
            return self.parent.data.index(self)
        return 0

    def is_leaf(self):
        return isinstance(self.data, Section)

    def is_included(self):
        if self.is_leaf():
            return Qt.Checked if self.data.include else Qt.Unchecked
        checked = False
        unchecked = False
        for child in self.data:
            if child.is_included() == Qt.PartiallyChecked:
                return Qt.PartiallyChecked
            elif child.is_included() == Qt.Checked:
                checked = True
            else:
                unchecked = True
        if checked and unchecked:
            return Qt.PartiallyChecked
        return Qt.Checked if checked else Qt.Unchecked

    def is_penalized(self):
        if self.is_leaf():
            return Qt.Checked if self.data.apply_penalty else Qt.Unchecked
        checked = False
        unchecked = False
        for child in self.data:
            if child.is_penalized() == Qt.PartiallyChecked:
                return Qt.PartiallyChecked
            elif child.is_penalized() == Qt.Checked:
                checked = True
            else:
                unchecked = True
        if checked and unchecked:
            return Qt.PartiallyChecked
        return Qt.Checked if checked else Qt.Unchecked

    def set_include(self, val):
        if self.is_leaf():
            self.data.include = val
            return

        for child in self.data:
            child.set_include(val)

    def set_penalize(self, val):
        if self.is_leaf():
            self.data.apply_penalty = val
            return

        for child in self.data:
            child.set_penalize(val)