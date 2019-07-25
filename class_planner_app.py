import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from my_mainwindow import My_MainWindow

app = QApplication(sys.argv)
window = QMainWindow()
ui = My_MainWindow()
ui.setupUi(window)

window.show()
sys.exit(app.exec_())