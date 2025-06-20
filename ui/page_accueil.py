import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel
from PyQt5 import uic
from interface.Signal_interface import MplCanvas
from interface.navier_stokes_interface import FluidAnalysisApp
from interface.laser_interface import LaserWindow
from ui.numerisation_options import NumerationOptionsWindow
from interface.data_science_interface import DataScienceTab
from interface.energy_interface import EnergyDigitizationTab
from interface.integration_interface import ODESolverApp
from interface.equ_diff_interface import EquDiffInterface

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Chemin absolu vers le fichier .ui
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'page_accueil.ui')
        uic.loadUi(ui_path, self)
        self.setWindowTitle("Application de Calcul Scientifique")


        # Récupération des widgets par leur objectName dans Qt Designer
        self.data_science_button = self.findChild(QPushButton, 'data_science_button')
        self.energy_button = self.findChild(QPushButton, 'energy_button')
        self.laser_button = self.findChild(QPushButton, 'laser_button')
        self.navier_stokes_button = self.findChild(QPushButton, 'navier_stokes_button')
        self.numerisation_button = self.findChild(QPushButton, 'numerisation_button')
        self.quit_button = self.findChild(QPushButton, 'quit_button')
        self.welcome_label = self.findChild(QLabel, 'welcome_label')

        # Connexion des boutons à leurs méthodes
        self.data_science_button.clicked.connect(self.open_data_science_window)
        self.energy_button.clicked.connect(self.open_energy_window)
        self.laser_button.clicked.connect(self.open_laser_window)
        self.navier_stokes_button.clicked.connect(self.open_navier_stokes_window)
        self.numerisation_button.clicked.connect(self.open_numeration_window)
        self.quit_button.clicked.connect(self.close)

        # Initialisation des fenêtres filles
        self.numeration_window = NumerationOptionsWindow(self)
        self.laser_window = LaserWindow()
        self.ns_interface = FluidAnalysisApp()
        self.energy_window = EnergyDigitizationTab()

    def open_numeration_window(self):
        self.numeration_window.show()

    def open_laser_window(self):
        self.laser_window.show()

    def open_energy_window(self):
        self.energy_window.show()

    def open_data_science_window(self):
        self.data_science_window.show()

    def open_navier_stokes_window(self):
        self.ns_interface.show()
