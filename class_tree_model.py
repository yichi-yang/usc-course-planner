from class_tree_node import ClassTreeNode
from PyQt5.QtCore import QAbstractItemModel, QVariant, QObject, QModelIndex, Qt, QMetaType, QSize
from PyQt5.QtGui import QBrush


class ClassTreeModel (QAbstractItemModel):

    def __init__(self, root=ClassTreeNode('root', None), parent=None):
        super().__init__(parent)
        self.root = root
        self.locked = False

    def index(self, row, col, parent=QModelIndex()):
        if not self.hasIndex(row, col, parent):
            return QModelIndex()

        parent_node = parent.internalPointer() if parent.isValid() else self.root

        if parent_node.is_leaf():
            return QModelIndex()

        child_node = parent_node.data[row]
        return self.createIndex(row, col, child_node)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        child_node = index.internalPointer()
        parent_node = child_node.parent

        if parent_node == self.root:
            return QModelIndex()

        return self.createIndex(parent_node.row_index_of(), 0, parent_node)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        parent_node = self.root if not parent.isValid() else parent.internalPointer()

        return 0 if parent_node.is_leaf() else len(parent_node.data)

    def columnCount(self, parent):
        return 9

    def data(self, index, role):
        if not index.isValid():
            return QVariant()

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if not node.is_leaf():
                if index.column() == 0:
                    return node.name
            else:
                if index.column() == 0:
                    return node.data.section_id
                if index.column() == 3:
                    return node.data.time
                if index.column() == 4:
                    return node.data.days
                if index.column() == 5:
                    return node.data.registered
                if index.column() == 6:
                    return "X" if node.data.closed else ""
                if index.column() == 7:
                    return node.data.instructor
                if index.column() == 8:
                    return node.data.location
        elif role == Qt.CheckStateRole:
            if index.column() == 1:
                return node.is_included()
            elif index.column() == 2:
                return node.is_penalized()
        elif role == Qt.ForegroundRole:
            if not node.is_included():
                return QBrush(Qt.lightGray)

        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        node = index.internalPointer()
        is_enabled = Qt.ItemIsEnabled if not self.locked else Qt.NoItemFlags
        if index.column() == 1:
            return is_enabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        if index.column() == 2:
            return (is_enabled if node.is_included() else Qt.NoItemFlags) | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return super().flags(index)

    def headerData(self, section, orientation, role):
        header = ["Name", "Included", "Penalized", "Time",
                  "Days", "Registered", "Closed", "Instructor", "Location"]
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(header):
            return header[section]
        return QVariant()

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.CheckStateRole:
            node = index.internalPointer()
            if index.column() == 1:
                node.set_include(value)
                self._all_children_changed(node, range(9), [])
                self._all_ancestor_changed(node, range(9), [])
                return True
            elif index.column() == 2:
                node.set_penalize(value)
                self._all_children_changed(node, range(9), [])
                self._all_ancestor_changed(node, range(9), [])
                return True
        return False

    def _all_children_changed(self, node, columns, role):
        if node == self.root:
            return
        row_index = node.row_index_of()
        for col in columns:
            if col < 9:
                item_index = self.createIndex(row_index, col, node)
                self.dataChanged.emit(item_index, item_index, role)
        if not node.is_leaf():
            for child in node.data:
                self._all_children_changed(child, columns, role)

    def _all_ancestor_changed(self, node, columns, role):
        if node == self.root:
            return
        parent_node = node.parent
        row_index = parent_node.row_index_of()
        if not parent_node == self.root:
            for col in columns:
                if col < 9:
                    item_index = self.createIndex(row_index, col, parent_node)
                    self.dataChanged.emit(item_index, item_index, role)
        self._all_ancestor_changed(parent_node, columns, role)

    def add_top_level_child(self, class_tree_node):
        class_tree_node.parent = self.root
        self.beginInsertRows(QModelIndex(), len(
            self.root.data), len(self.root.data))
        self.root.data.append(class_tree_node)
        self.endInsertRows()

    def delete_top_level_child(self, index):
        if index < len(self.root.data):
            self.beginRemoveRows(QModelIndex(), index, index)
            name = self.root.data[index].name
            self.root.data.pop(index)
            self.endRemoveRows()
            return name

    def lock(self, is_locked):
        self.locked = is_locked
        for course in self.root.data:
            self._all_children_changed(course, range(9), [])
