import sys
from PyQt5.QtWidgets import QApplication
from ui.page_accueil import MainWindow

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()
