import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox, QSplitter
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.optimize import fsolve

# ----------------- Méthodes numériques -----------------

def euler_explicit(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        y[i] = y[i-1] + f(y[i-1], t[i-1]) * (t[i] - t[i-1])
    return y

def euler_implicit(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        # Résolution implicite : y[i] = y[i-1] + dt * f(y[i], t[i])
        def g(ynext):
            return ynext - y[i-1] - dt * f(ynext, t[i])
        y[i] = fsolve(g, y[i-1])[0]
    return y

def heun(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        y_pred = y[i-1] + dt * f(y[i-1], t[i-1])
        y[i] = y[i-1] + dt/2 * (f(y[i-1], t[i-1]) + f(y_pred, t[i]))
    return y

def rk2(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        k1 = f(y[i-1], t[i-1])
        k2 = f(y[i-1] + dt*k1/2, t[i-1] + dt/2)
        y[i] = y[i-1] + dt * k2
    return y

def rk4(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        k1 = f(y[i-1], t[i-1])
        k2 = f(y[i-1] + dt*k1/2, t[i-1] + dt/2)
        k3 = f(y[i-1] + dt*k2/2, t[i-1] + dt/2)
        k4 = f(y[i-1] + dt*k3, t[i-1] + dt)
        y[i] = y[i-1] + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
    return y

def crank_nicolson(f, y0, t):
    y = np.zeros(len(t))
    y[0] = y0
    for i in range(1, len(t)):
        dt = t[i] - t[i-1]
        # Résolution implicite : y[i] = y[i-1] + dt/2*(f(y[i-1], t[i-1]) + f(y[i], t[i]))
        def g(ynext):
            return ynext - y[i-1] - dt/2 * (f(y[i-1], t[i-1]) + f(ynext, t[i]))
        y[i] = fsolve(g, y[i-1])[0]
    return y

METHODS = {
    "Euler explicite": euler_explicit,
    "Euler implicite": euler_implicit,
    "Heun": heun,
    "RK2": rk2,
    "RK4": rk4,
    "Crank-Nicolson": crank_nicolson,
}

# ----------------- Interface PyQt5 -----------------

class EquDiffInterface(QWidget):
    def __init__(self, course_text):
        super().__init__()
        self.setWindowTitle("Équations différentielles - Méthodes numériques")
        self.setMinimumSize(1200, 700)
        self.init_ui(course_text)

    def init_ui(self, course_text):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # --- Panneau de contrôle ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Equation
        control_layout.addWidget(QLabel("Équation (dy/dt = f(y, t)) :"))
        self.equation_input = QLineEdit("y - t")
        control_layout.addWidget(self.equation_input)

        # Condition initiale
        control_layout.addWidget(QLabel("Condition initiale y(t0) :"))
        self.y0_input = QLineEdit("1.0")
        control_layout.addWidget(self.y0_input)

        # t0, t1
        control_layout.addWidget(QLabel("Intervalle de temps (t0, t1) :"))
        self.t_interval_input = QLineEdit("0, 10")
        control_layout.addWidget(self.t_interval_input)

        # Nombre de points
        control_layout.addWidget(QLabel("Nombre de points :"))
        self.n_points_input = QLineEdit("100")
        control_layout.addWidget(self.n_points_input)

        # Méthode numérique
        control_layout.addWidget(QLabel("Méthode numérique :"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(list(METHODS.keys()))
        control_layout.addWidget(self.method_combo)

        # Bouton
        self.solve_btn = QPushButton("Résoudre et tracer")
        self.solve_btn.clicked.connect(self.solve)
        control_layout.addWidget(self.solve_btn)

        # Résultat
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        control_layout.addWidget(QLabel("Valeurs numériques (aperçu) :"))
        control_layout.addWidget(self.result_text)

        # --- Panneau graphique ---
        display_panel = QWidget()
        display_layout = QVBoxLayout(display_panel)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        display_layout.addWidget(self.canvas)

        # --- Panneau cours ---
        self.course_text_panel = QTextEdit()
        self.course_text_panel.setReadOnly(True)
        self.course_text_panel.setText(course_text)

        # Ajout au splitter
        splitter.addWidget(control_panel)
        splitter.addWidget(display_panel)
        splitter.addWidget(self.course_text_panel)
        splitter.setSizes([350, 600, 400])

    def solve(self):
        try:
            # Lecture des paramètres
            eqn = self.equation_input.text()
            y0 = float(self.y0_input.text())
            t0, t1 = map(float, self.t_interval_input.text().split(','))
            n_points = int(self.n_points_input.text())
            method_name = self.method_combo.currentText()
            t = np.linspace(t0, t1, n_points)

            # Génération de la fonction f(y, t)
            def f(y, t):
                # ATTENTION : eval() doit être sécurisé en production
                return eval(eqn, {"y": y, "t": t, "np": np})

            # Calcul
            y = METHODS[method_name](f, y0, t)

            # Affichage résultats
            self.result_text.setText(
                "t : " + np.array2string(t[:10], precision=3) + " ...\n" +
                "y : " + np.array2string(y[:10], precision=3) + " ..."
            )

            # Tracé
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(t, y, label="Solution numérique")
            ax.set_xlabel("t")
            ax.set_ylabel("y(t)")
            ax.set_title(f"Résolution par {method_name}")
            ax.legend()
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

def load_course_text(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return "Cours non disponible."

if __name__ == "__main__":
    app = QApplication(sys.argv)
    course_text = load_course_text("cours_EDO_mpci_2018-2019.pdf.txt")  # Place ici ton fichier texte extrait du PDF
    main_app = EquDiffInterface(course_text)
    main_app.show()
    sys.exit(app.exec_())
