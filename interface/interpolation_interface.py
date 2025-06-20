import sys
import numpy as np
import sympy as sp
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QMessageBox, QGroupBox
)
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

    def plot(self, poly, x_vals, y_vals, x_interp, y_interp):
        self.ax.clear()
        x_sym = sp.Symbol('x')
        f_lambdified = sp.lambdify(x_sym, poly, modules=["numpy"])

        x_min, x_max = min(x_vals) - 1, max(x_vals) + 1
        x_plot = np.linspace(x_min, x_max, 400)
        y_plot = f_lambdified(x_plot)

        # Tracé du polynôme (ligne bleue)
        self.ax.plot(x_plot, y_plot, label="Polynôme d'interpolation", color='blue', linewidth=2)

        # Points donnés (cases rouges)
        self.ax.scatter(x_vals, y_vals, color='red', edgecolors='black', s=80, marker='s', label="Points donnés", zorder=5)

        # Point interpolé (case verte)
        self.ax.scatter([x_interp], [y_interp], color='green', edgecolors='black', s=100, marker='s', label=f"P({x_interp})", zorder=10)

        self.ax.set_title("Interpolation polynomiale", fontsize=14, fontweight='bold')
        self.ax.set_xlabel("x", fontsize=12)
        self.ax.set_ylabel("P(x)", fontsize=12)
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        self.draw()

class InterpolationInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interpolation – Lagrange et Newton avec Canvas")
        self.setGeometry(150, 150, 900, 650)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Groupe Entrées
        input_group = QGroupBox("Entrées")
        input_layout = QHBoxLayout()

        # Inputs x et y
        xy_layout = QVBoxLayout()
        self.x_input = QLineEdit()
        self.x_input.setPlaceholderText("Ex: 1, 2, 3, 4")
        self.y_input = QLineEdit()
        self.y_input.setPlaceholderText("Ex: 1, 4, 9, 16")
        xy_layout.addWidget(QLabel("Valeurs de x :"))
        xy_layout.addWidget(self.x_input)
        xy_layout.addWidget(QLabel("Valeurs de y :"))
        xy_layout.addWidget(self.y_input)

        # Input interpolation et méthode
        interp_layout = QVBoxLayout()
        self.x_interp_input = QLineEdit()
        self.x_interp_input.setPlaceholderText("Ex: 2.5")
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Lagrange", "Newton"])
        interp_layout.addWidget(QLabel("x à interpoler :"))
        interp_layout.addWidget(self.x_interp_input)
        interp_layout.addWidget(QLabel("Méthode d'interpolation :"))
        interp_layout.addWidget(self.method_combo)

        input_layout.addLayout(xy_layout, 2)
        input_layout.addLayout(interp_layout, 1)
        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Résultat texte
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setFont(QFont("Courier", 10))
        main_layout.addWidget(QLabel("Résultat (polynôme et valeur) :"))
        main_layout.addWidget(self.result_display, 1)

        # Bouton Interpoler
        self.calc_button = QPushButton("Interpoler")
        self.calc_button.setFixedHeight(40)
        self.calc_button.clicked.connect(self.interpolate)
        main_layout.addWidget(self.calc_button)

        # Canvas matplotlib + toolbar
        self.canvas = MplCanvas(self, width=7, height=5, dpi=100)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas, 3)

        self.setLayout(main_layout)

    def interpolate(self):
        try:
            x_vals = [float(x.strip()) for x in self.x_input.text().split(',') if x.strip() != '']
            y_vals = [float(y.strip()) for y in self.y_input.text().split(',') if y.strip() != '']
            x_interp = float(self.x_interp_input.text())

            if len(x_vals) != len(y_vals):
                raise ValueError("Les listes x et y doivent avoir la même longueur.")
            if len(x_vals) < 2:
                raise ValueError("Au moins deux points sont nécessaires pour l'interpolation.")
            if len(set(x_vals)) != len(x_vals):
                raise ValueError("Les valeurs de x doivent être uniques.")

            method = self.method_combo.currentText()
            if method == "Lagrange":
                poly = self.lagrange_polynomial(x_vals, y_vals)
            else:
                poly = self.newton_polynomial(x_vals, y_vals)

            x_sym = sp.Symbol('x')
            y_interp = poly.subs(x_sym, x_interp).evalf()

            poly_str = sp.pretty(poly, use_unicode=True)

            self.result_display.setPlainText(
                f"Polynôme d'interpolation ({method}) :\n\nP(x) = {poly_str}\n\n"
                f"Valeur interpolée en x = {x_interp} :\nP({x_interp}) = {y_interp:.6g}"
            )

            self.canvas.plot(poly, x_vals, y_vals, x_interp, y_interp)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    @staticmethod
    def lagrange_polynomial(x_vals, y_vals):
        x = sp.Symbol('x')
        n = len(x_vals)
        P = 0
        for i in range(n):
            term = y_vals[i]
            for j in range(n):
                if i != j:
                    term *= (x - x_vals[j]) / (x_vals[i] - x_vals[j])
            P += term
        return sp.simplify(P)

    @staticmethod
    def newton_polynomial(x_vals, y_vals):
        x = sp.Symbol('x')
        n = len(x_vals)
        coef = y_vals.copy()
        for j in range(1, n):
            for i in range(n - 1, j - 1, -1):
                coef[i] = (coef[i] - coef[i - 1]) / (x_vals[i] - x_vals[i - j])
        P = coef[0]
        prod = 1
        for i in range(1, n):
            prod *= (x - x_vals[i - 1])
            P += coef[i] * prod
        return sp.simplify(P)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = InterpolationInterface()
    window.show()
    sys.exit(app.exec_())
