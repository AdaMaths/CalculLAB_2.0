import os
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel
from PyQt5 import uic

from interface.optimisation_interface import OptimizationApp
from interface.automatique_interface import SystemAnalysisApp
from interface.integration_interface import ODESolverApp
from interface.interpolation_interface import InterpolationInterface
from interface.equ_diff_interface import EquDiffInterface
from interface.Signal_interface import MplCanvas

class NumerationOptionsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'numerisation_options.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Options de Numérisation")

        # Récupération des widgets
        self.eq_diff_button = self.findChild(QPushButton, 'eq_diff_button')
        self.optimisation_button = self.findChild(QPushButton, 'optimisation_button')
        self.automatique_button = self.findChild(QPushButton, 'automatique_button')
        self.integration_button = self.findChild(QPushButton, 'integration_button')
        self.interpolation_button = self.findChild(QPushButton, 'interpolation_button')
        self.signal_button = self.findChild(QPushButton, 'signal_button')
        self.back_button = self.findChild(QPushButton, 'back_button')
        self.title_label = self.findChild(QLabel, 'title_label')

        # Connexion des signaux
        self.eq_diff_button.clicked.connect(self.open_eq_diff)
        self.optimisation_button.clicked.connect(self.open_optimisation)
        self.automatique_button.clicked.connect(self.open_automatique_interface)
        self.integration_button.clicked.connect(self.open_integration)
        self.interpolation_button.clicked.connect(self.open_interpolation)
        self.signal_button.clicked.connect(self.open_signal)
        self.back_button.clicked.connect(self.close)

        # Initialisation des fenêtres (évite les doublons)
        self.optimisation_window = None
        self.automatique_interface = None
        self.integration_window = None
        self.signal_window = None
        self.interpolation_window = None
        self.equ_diff_window = None

    def open_optimisation(self):
        if self.optimisation_window is None:
            self.optimisation_window = OptimizationApp()
        self.optimisation_window.show()

    def open_automatique_interface(self):
        if self.automatique_interface is None:
            self.automatique_interface = SystemAnalysisApp()
        self.automatique_interface.show()

    def open_integration(self):
        if self.integration_window is None:
            self.integration_window = ODESolverApp()
        self.integration_window.show()

    def open_signal(self):
        if self.signal_window is None:
            self.signal_window = MplCanvas()
        self.signal_window.show()

    def open_interpolation(self):
        if self.interpolation_window is None:
            self.interpolation_window = InterpolationInterface()
        self.interpolation_window.show()

    def open_eq_diff(self):
        if self.equ_diff_window is None:
            self.equ_diff_window = EquDiffInterface()
        self.equ_diff_window.show()
