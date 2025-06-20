import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                            QLineEdit, QPushButton, QTextEdit, QMessageBox, QFrame,
                            QScrollArea, QGridLayout)
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from sympy import symbols, integrate, pi, cos, sin, simplify, sympify, lambdify
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):  # Canvas for Matplotlib plots
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
        fig.tight_layout()

class FourierApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyseur de Séries de Fourier")
        self.setWindowIcon(QIcon("icon.png"))
        self.func_input = None
        self.interval_input = None
        self.n_terms_input = None
        self.compute_btn = None
        self.result_box = None
        self.plot_canvas = None
        self.initUI()
        self.applyStyle()

    def initUI(self):
        main_layout = QVBoxLayout()

        # Header
        header = QLabel("Analyseur de Séries de Fourier")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Main Content Area
        main_content = QWidget()
        content_layout = QGridLayout()  # Use a grid layout

        # Zone de saisie (Input Area)
        input_frame = QFrame()
        input_layout = QVBoxLayout()

        self.create_input_field("Fonction f(x)", "x**2 + sin(x)", input_layout)
        self.create_input_field("Demi-période L", "pi", input_layout)
        self.create_input_field("Nombre de termes N", "5", input_layout)

        input_frame.setLayout(input_layout)
        content_layout.addWidget(input_frame, 0, 0)  # Add input frame to grid

        # Bouton d'action (Compute Button)
        self.compute_btn = QPushButton("Calculer la Série")
        self.compute_btn.clicked.connect(self.compute_fourier)
        content_layout.addWidget(self.compute_btn, 1, 0)  # Add button below input

        # Résultats (Results Area)
        result_frame = QFrame()
        result_layout = QVBoxLayout()

        result_label = QLabel("Résultats d'Analyse")
        result_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(result_label)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        result_layout.addWidget(self.result_box)

        # Graphique (Plot Area)
        self.plot_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        result_layout.addWidget(self.plot_canvas)

        result_frame.setLayout(result_layout)
        content_layout.addWidget(result_frame, 0, 1, 2, 1)  # Add result frame to the right, spanning 2 rows

        main_content.setLayout(content_layout)
        main_layout.addWidget(main_content)

        self.setLayout(main_layout)

    def create_input_field(self, label, placeholder, layout):
        container = QVBoxLayout()
        lbl = QLabel(label)
        field = QLineEdit()
        field.setPlaceholderText(placeholder)

        container.addWidget(lbl)
        container.addWidget(field)
        layout.addLayout(container)

        # Stockage des références
        if label == "Fonction f(x)":
            self.func_input = field
        elif label == "Demi-période L":
            self.interval_input = field
        else:
            self.n_terms_input = field

    def applyStyle(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI';
            }
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #333;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4e73df;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a5bc7;
            }
            #headerLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2e384d;
                margin: 15px 0;
            }
        """)

        # Style spécifique pour le header
        header = self.findChild(QLabel)
        if header:
            header.setObjectName("headerLabel")
            header.setStyleSheet("""
                #headerLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2e384d;
                    margin: 15px 0;
                }
            """)

    def compute_fourier(self):
        try:
            x = symbols('x')
            f_expr = sympify(self.func_input.text())
            L = sympify(self.interval_input.text())
            N = int(self.n_terms_input.text())

            # Calcul des coefficients
            a0 = (1/(2*L)) * integrate(f_expr, (x, -L, L))
            an = [(1/L) * integrate(f_expr*cos(n*pi*x/L), (x, -L, L)) for n in range(1, N+1)]
            bn = [(1/L) * integrate(f_expr*sin(n*pi*x/L), (x, -L, L)) for n in range(1, N+1)]

            # Construction de la série
            series = a0
            for n in range(1, N+1):
                series += an[n-1]*cos(n*pi*x/L) + bn[n-1]*sin(n*pi*x/L)

            # Formatage des résultats
            result_text = (
                f"a₀ = {a0:.5f}\n\n" +
                "\n".join([f"a_{n} = {an[n-1]:.5f}" for n in range(1, N+1)]) + "\n\n" +
                "\n".join([f"b_{n} = {bn[n-1]:.5f}" for n in range(1, N+1)]) + "\n\n" +
                f"Série de Fourier (N={N}):\n{simplify(series)}"
            )

            self.result_box.setPlainText(result_text)

            # Visualisation
            self.plot_results(f_expr, series, L, N)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur de calcul:\n{str(e)}")

    def plot_results(self, f_expr, series, L, N):
        try:
            x = symbols('x')
            f_lamb = lambdify(x, f_expr, 'numpy')
            s_lamb = lambdify(x, series, 'numpy')

            x_vals = np.linspace(-float(L), float(L), 500)

            # Clear old plot
            self.plot_canvas.axes.clear()

            # Plot the data
            self.plot_canvas.axes.plot(x_vals, f_lamb(x_vals), label=f'f(x) = {str(f_expr)}', linewidth=2)
            self.plot_canvas.axes.plot(x_vals, s_lamb(x_vals), '--', label=f'Approximation (N={N})', linewidth=1.5)

            # Customize the plot
            self.plot_canvas.axes.set_title('Comparaison Fonction/Série de Fourier', pad=20)
            self.plot_canvas.axes.set_xlabel('x', fontsize=12)
            self.plot_canvas.axes.set_ylabel('Valeur', fontsize=12)
            self.plot_canvas.axes.legend()
            self.plot_canvas.axes.grid(True, linestyle='--', alpha=0.7)

            # Refresh the canvas
            self.plot_canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du traçage du graphique:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = FourierApp()
    window.show()
    sys.exit(app.exec_())
