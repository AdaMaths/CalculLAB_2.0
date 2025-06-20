import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFormLayout, QGroupBox)


# --- Simulation Navier-Stokes (simplifiée) ---
def navier_stokes_step(u, v, p, nu, dt, dx, dy):
    # Simplified 2D incompressible Navier-Stokes (Chorin projection)
    # u, v: vitesse; p: pression; nu: viscosité; dt: pas de temps; dx, dy: maillage
    # ... (implémentation simplifiée ici)
    # Retourner les nouveaux champs u, v, p
    return u, v, p


# --- Interface PyQt5 ---
class FluidAnalysisApp(QMainWindow):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Simulation Navier-Stokes 2D (PyQt5)")
        self.initUI()

    def initUI(self):
        # Paramètres par défaut
        self.nx, self.ny = 32, 32
        self.dx, self.dy = 1.0 / self.nx, 1.0 / self.ny
        self.dt = 0.01
        self.nu = 0.1

        # Champs de saisie
        form = QFormLayout()
        self.visc_input = QLineEdit(str(self.nu))
        self.dt_input = QLineEdit(str(self.dt))
        form.addRow("Viscosité (nu):", self.visc_input)
        form.addRow("Pas de temps (dt):", self.dt_input)

        # Bouton de simulation
        self.sim_btn = QPushButton("Lancer la simulation")
        self.sim_btn.clicked.connect(self.run_simulation)

        # Affichage matplotlib
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        # Affichage des équations
        eq_label = QLabel("Équations utilisées :\n"
                          r"$\frac{\partial \vec{u}}{\partial t} + (\vec{u} \cdot \nabla)\vec{u} = -\nabla p + \nu \Delta \vec{u}$" "\n"
                          r"$\nabla \cdot \vec{u} = 0$")

        # Layout principal
        layout = QVBoxLayout()
        group = QGroupBox("Paramètres")
        group.setLayout(form)
        layout.addWidget(group)
        layout.addWidget(self.sim_btn)
        layout.addWidget(self.canvas)
        layout.addWidget(eq_label)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def run_simulation(self):
        # Lire les paramètres
        nu = float(self.visc_input.text())
        dt = float(self.dt_input.text())
        nx, ny = self.nx, self.ny
        dx, dy = self.dx, self.dy

        # Initialisation
        u = np.zeros((nx, ny))
        v = np.zeros((nx, ny))
        p = np.zeros((nx, ny))

        # Condition initiale simple : petit vortex au centre
        u[nx // 4:3 * nx // 4, ny // 4:3 * ny // 4] = 1.0

        # Simulation (quelques pas)
        for _ in range(50):
            u, v, p = navier_stokes_step(u, v, p, nu, dt, dx, dy)

        # Affichage
        self.ax.clear()
        X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
        self.ax.quiver(X, Y, u, v)
        self.ax.set_title("Champ de vitesse")
        self.canvas.draw()


# --- Lancer l'application ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluidAnalysisApp()
    window.show()
    sys.exit(app.exec_())