import sys
from PyQt5.QtWidgets import QApplication
from gui_interface import ForensicGUI

def main():
    app = QApplication(sys.argv)
    window = ForensicGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
