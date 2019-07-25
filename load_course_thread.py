from PyQt5.QtCore import QThread, pyqtSignal
from load_class import load_class
from class_tree_node import ClassTreeNode


class LoadClassThread(QThread):
    results_ready = pyqtSignal(QThread)

    def __init__(self, url, name):
        super().__init__()
        self.root = None
        self.url = url
        self.name = name

    def run(self):
        self.root = load_class(self.url, self.name)
        self.results_ready.emit(self)
