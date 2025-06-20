import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget, QGroupBox,
    QDoubleSpinBox, QPushButton, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

# --------- APPLICATION 1 : PERTES PAR CAVITÉ LASER ---------
class LaserWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.info_label = QLabel(
            "<b>Application pour simuler les pertes par cavité laser</b><br>"
            "Entrez les paramètres de la cavité ci-dessous pour obtenir les pertes totales."
        )
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 13))
        layout.addWidget(self.info_label)

        param_box = QGroupBox("Paramètres de la cavité")
        grid = QGridLayout()
        self.R1_spin = QDoubleSpinBox()
        self.R1_spin.setRange(0.90, 0.9999)
        self.R1_spin.setDecimals(4)
        self.R1_spin.setSingleStep(0.0001)
        self.R1_spin.setValue(0.99)
        self.R2_spin = QDoubleSpinBox()
        self.R2_spin.setRange(0.90, 0.9999)
        self.R2_spin.setDecimals(4)
        self.R2_spin.setSingleStep(0.0001)
        self.R2_spin.setValue(0.99)
        self.int_loss_spin = QDoubleSpinBox()
        self.int_loss_spin.setRange(0, 0.1)
        self.int_loss_spin.setDecimals(4)
        self.int_loss_spin.setSingleStep(0.0001)
        self.int_loss_spin.setValue(0.005)
        self.int_loss_spin.setSuffix(" (fraction)")
        grid.addWidget(QLabel("R₁ (réflexion M1) :"), 0, 0)
        grid.addWidget(self.R1_spin, 0, 1)
        grid.addWidget(QLabel("R₂ (réflexion M2) :"), 1, 0)
        grid.addWidget(self.R2_spin, 1, 1)
        grid.addWidget(QLabel("Pertes internes :"), 2, 0)
        grid.addWidget(self.int_loss_spin, 2, 1)
        param_box.setLayout(grid)
        layout.addWidget(param_box)

        self.calc_button = QPushButton("Calculer les pertes")
        self.calc_button.clicked.connect(self.on_calculate)
        layout.addWidget(self.calc_button, alignment=Qt.AlignLeft)

        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 13, QFont.Bold))
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def on_calculate(self):
        R1 = self.R1_spin.value()
        R2 = self.R2_spin.value()
        T1 = 1 - R1
        T2 = 1 - R2
        Pint = self.int_loss_spin.value()
        total_loss = T1 + T2 + 2 * Pint
        txt = (
            f"<b>Miroir 1 :</b> R₁ = {R1:.4f} | T₁ = {T1:.4f}<br>"
            f"<b>Miroir 2 :</b> R₂ = {R2:.4f} | T₂ = {T2:.4f}<br>"
            f"Pertes internes (par passage) : {Pint*100:.2f}%<br>"
            f"<b>Pertes totales (par aller-retour) : {total_loss*100:.2f}%</b>"
        )
        if total_loss < 0.05:
            txt = f"<span style='color:green'>{txt}</span>"
        else:
            txt = f"<span style='color:red'>{txt}</span>"
        self.result_label.setText(txt)

# --------- APPLICATION 2 : PROFIL GAUSSIEN ---------
class GaussProfileWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.info_label = QLabel(
            "<b>Application pour simuler le profil gaussien de l’intensité du laser</b><br>"
            "Entrez les paramètres du faisceau pour afficher le profil d’intensité."
        )
        self.info_label.setWordWrap(True)
        self.info_label.setFont(QFont("Arial", 13))
        layout.addWidget(self.info_label)

        param_box = QGroupBox("Paramètres du faisceau")
        grid = QGridLayout()
        self.lambda_spin = QDoubleSpinBox()
        self.lambda_spin.setRange(200, 2000)
        self.lambda_spin.setValue(532)
        self.lambda_spin.setSuffix(" nm")
        self.waist_spin = QDoubleSpinBox()
        self.waist_spin.setRange(1, 1000)
        self.waist_spin.setValue(50)
        self.waist_spin.setSuffix(" μm")
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setRange(-1000, 1000)
        self.z_spin.setValue(0)
        self.z_spin.setSuffix(" mm")
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(0.01, 1000)
        self.power_spin.setValue(10)
        self.power_spin.setSuffix(" mW")
        grid.addWidget(QLabel("λ (nm) :"), 0, 0)
        grid.addWidget(self.lambda_spin, 0, 1)
        grid.addWidget(QLabel("w₀ (μm) :"), 0, 2)
        grid.addWidget(self.waist_spin, 0, 3)
        grid.addWidget(QLabel("z (mm) :"), 1, 0)
        grid.addWidget(self.z_spin, 1, 1)
        grid.addWidget(QLabel("Puissance (mW) :"), 1, 2)
        grid.addWidget(self.power_spin, 1, 3)
        param_box.setLayout(grid)
        layout.addWidget(param_box)

        self.calc_button = QPushButton("Afficher le profil gaussien")
        self.calc_button.clicked.connect(self.on_calculate)
        layout.addWidget(self.calc_button, alignment=Qt.AlignLeft)

        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(self.result_label)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.canvas.hide()
        self.result_label.hide()

    def on_calculate(self):
        lam_nm = self.lambda_spin.value()
        w0_um = self.waist_spin.value()
        z_mm = self.z_spin.value()
        power_mW = self.power_spin.value()
        lam = lam_nm * 1e-9
        w0 = w0_um * 1e-6
        z = z_mm * 1e-3
        power = power_mW * 1e-3
        zR = np.pi * w0 ** 2 / lam
        wz = w0 * np.sqrt(1 + (z / zR) ** 2)
        x = np.linspace(-3 * wz, 3 * wz, 400)
        I0 = 2 * power / (np.pi * wz ** 2)
        I = I0 * np.exp(-2 * (x / wz) ** 2)

        self.ax.clear()
        self.ax.plot(x * 1e6, I, color="#1976D2", lw=2)
        self.ax.set_title(f"Profil Gaussien à z = {z_mm:.1f} mm", fontsize=14, color="#1976D2")
        self.ax.set_xlabel("x (μm)", fontsize=12)
        self.ax.set_ylabel("Intensité (W/m²)", fontsize=12)
        self.ax.grid(alpha=0.3)
        self.canvas.draw()
        self.canvas.show()

        txt = (
            f"w(z) = {wz*1e6:.2f} μm<br>"
            f"zR = {zR*1e3:.2f} mm<br>"
            f"I₀ = {I0:.2e} W/m²"
        )
        self.result_label.setText(txt)
        self.result_label.show()

# --------- FENÊTRE PRINCIPALE ---------
class LaserSimApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Applications pédagogiques Laser")
        self.resize(900, 600)
        tabs = QTabWidget()
        tabs.addTab(LossesWidget(), "Pertes par cavité")
        tabs.addTab(GaussProfileWidget(), "Profil gaussien")
        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = LaserWindow()
    window.show()
    sys.exit(app.exec_())
