import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
                             QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
                             QSpinBox, QDoubleSpinBox, QSplitter)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class MathPlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super(MathPlotCanvas, self).__init__(self.fig)
        self.setParent(parent)
        self.fig.tight_layout()

class ODESolverApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calcul Numérique - Méthodes Scientifiques")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow, QTabWidget, QWidget {
                background-color: #f5f5f5;
                font-family: "Segoe UI", sans-serif;
            }
            QLabel {
                font-size: 11pt;
                color: #333;
            }
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
                background-color: #fff;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px;
                background-color: #fff;
                font-size: 10pt;
                selection-background-color: #2980b9;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                font-family: "Courier New", monospace;
                font-size: 10pt;
                background-color: #f0f0f0;
                color: #333;
            }
            QTableWidget {
                alternate-background-color: #ecf0f1;
                gridline-color: #d4d4d4;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #bdc3c7;
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        # Apply a light color palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#f5f5f5"))
        palette.setColor(QPalette.WindowText, QColor("#333"))
        palette.setColor(QPalette.Base, QColor("#fff"))
        palette.setColor(QPalette.AlternateBase, QColor("#ecf0f1"))
        palette.setColor(QPalette.Text, QColor("#333"))
        palette.setColor(QPalette.Button, QColor("#3498db"))
        palette.setColor(QPalette.ButtonText, QColor("#fff"))
        self.setPalette(palette)

        self.tabs = QTabWidget()
        self.init_ui()

    def init_ui(self):
        # Création des onglets
        self.integration_tab = self.create_integration_tab()
        self.linear_systems_tab = self.create_linear_systems_tab()
        self.lu_decomposition_tab = self.create_lu_decomposition_tab()

        self.tabs.addTab(self.integration_tab, "Intégration Numérique")
        self.tabs.addTab(self.linear_systems_tab, "Systèmes Linéaires")
        self.tabs.addTab(self.lu_decomposition_tab, "Décomposition LU")

        self.setCentralWidget(self.tabs)

    def create_integration_tab(self):
        tab = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Panneau de contrôle
        control_panel = QWidget()
        control_layout = QVBoxLayout()
        control_layout.setSpacing(10)

        # Groupe de paramètres
        param_group = QGroupBox("Paramètres d'Intégration")
        param_layout = QVBoxLayout()
        param_layout.setSpacing(8)

        self.func_input = QLineEdit("")
        self.func_input.setToolTip("Entrez la fonction à intégrer")

        self.a_input = QDoubleSpinBox()
        self.a_input.setRange(-1000, 1000)
        self.a_input.setValue(0)
        self.a_input.setToolTip("Borne inférieure de l'intégration")

        self.b_input = QDoubleSpinBox()
        self.b_input.setRange(-1000, 1000)
        self.b_input.setValue(3)
        self.b_input.setToolTip("Borne supérieure de l'intégration")

        self.n_input = QSpinBox()
        self.n_input.setRange(1, 10000)
        self.n_input.setValue(100)
        self.n_input.setToolTip("Nombre de subdivisions pour l'intégration")

        param_layout.addWidget(QLabel("Fonction f(x):"))
        param_layout.addWidget(self.func_input)
        param_layout.addWidget(QLabel("Borne inférieure (a):"))
        param_layout.addWidget(self.a_input)
        param_layout.addWidget(QLabel("Borne supérieure (b):"))
        param_layout.addWidget(self.b_input)
        param_layout.addWidget(QLabel("Nombre de subdivisions (n):"))
        param_layout.addWidget(self.n_input)

        param_group.setLayout(param_layout)

        # Boutons de calcul
        button_group = QGroupBox("Méthodes d'Intégration")
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)

        self.calc_trapeze = QPushButton("Méthode des Trapèzes composite")
        self.calc_simpson = QPushButton("Méthode de Simpson")
        self.calc_midpoint = QPushButton("Méthode du Point Milieu")


        self.calc_trapeze.clicked.connect(lambda: self.calculate_integration('trapeze'))
        self.calc_simpson.clicked.connect(lambda: self.calculate_integration('simpson'))
        self.calc_midpoint.clicked.connect(lambda: self.calculate_integration('midpoint'))

 
        button_layout.addWidget(self.calc_trapeze)
        button_layout.addWidget(self.calc_simpson)
        button_layout.addWidget(self.calc_midpoint)


        button_group.setLayout(button_layout)

        # Zone de résultats
        result_group = QGroupBox("Résultats")
        result_layout = QVBoxLayout()
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        result_layout.addWidget(self.result_display)
        result_group.setLayout(result_layout)

        # Assemblage du panneau de contrôle
        control_layout.addWidget(param_group)
        control_layout.addWidget(button_group)
        control_layout.addWidget(result_group)
        control_panel.setLayout(control_layout)

        # Panneau de visualisation
        visual_panel = QWidget()
        visual_layout = QVBoxLayout()

        self.plot_canvas = MathPlotCanvas(self, width=5, height=4)
        visual_layout.addWidget(self.plot_canvas)

        visual_panel.setLayout(visual_layout)

        # Assemblage final
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(control_panel)
        splitter.addWidget(visual_panel)
        splitter.setSizes([400, 700])

        main_layout.addWidget(splitter)
        tab.setLayout(main_layout)

        return tab

    def create_linear_systems_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Configuration du système
        system_group = QGroupBox("Configuration du Système Linéaire")
        system_layout = QVBoxLayout()
        system_layout.setSpacing(10)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Taille du système:"))
        self.system_size = QSpinBox()
        self.system_size.setRange(2, 10)
        self.system_size.setValue(3)
        self.system_size.valueChanged.connect(self.update_matrix_size)
        size_layout.addWidget(self.system_size)

        system_layout.addLayout(size_layout)

        # Tables pour la matrice et le vecteur
        matrix_layout = QHBoxLayout()

        self.matrix_table = QTableWidget(3, 3)
        self.matrix_table.setMinimumWidth(400)
        self.vector_table = QTableWidget(3, 1)
        self.vector_table.setMaximumWidth(150)

        # Initialisation des tables
        self.init_tables()

        matrix_layout.addWidget(self.matrix_table)
        matrix_layout.addWidget(self.vector_table)

        system_layout.addLayout(matrix_layout)

        # Boutons de méthode
        method_group = QGroupBox("Méthodes de Résolution")
        method_layout = QHBoxLayout()
        method_layout.setSpacing(10)

        self.calc_jacobi = QPushButton("Méthode de Jacobi")
        self.calc_gauss_seidel = QPushButton("Méthode de Gauss-Seidel")
        self.calc_direct = QPushButton("Résolution Directe")

        self.calc_jacobi.clicked.connect(lambda: self.solve_linear_system('jacobi'))
        self.calc_gauss_seidel.clicked.connect(lambda: self.solve_linear_system('gauss_seidel'))
        self.calc_direct.clicked.connect(lambda: self.solve_linear_system('direct'))

        method_layout.addWidget(self.calc_jacobi)
        method_layout.addWidget(self.calc_gauss_seidel)
        method_layout.addWidget(self.calc_direct)

        method_group.setLayout(method_layout)

        # Paramètres itératifs
        iter_group = QGroupBox("Paramètres Itératifs")
        iter_layout = QHBoxLayout()
        iter_layout.setSpacing(10)

        iter_layout.addWidget(QLabel("Itérations max:"))
        self.max_iter = QSpinBox()
        self.max_iter.setRange(10, 10000)
        self.max_iter.setValue(1000)
        iter_layout.addWidget(self.max_iter)

        iter_layout.addWidget(QLabel("Tolérance:"))
        self.tolerance = QLineEdit("1e-6")
        iter_layout.addWidget(self.tolerance)

        iter_group.setLayout(iter_layout)

        # Zone de résultats
        result_group = QGroupBox("Résultats")
        result_layout = QVBoxLayout()
        self.system_result = QTextEdit()
        self.system_result.setReadOnly(True)
        result_layout.addWidget(self.system_result)
        result_group.setLayout(result_layout)

        system_group.setLayout(system_layout)

        main_layout.addWidget(system_group)
        main_layout.addWidget(method_group)
        main_layout.addWidget(iter_group)
        main_layout.addWidget(result_group)

        tab.setLayout(main_layout)
        return tab

    def create_lu_decomposition_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Configuration de la matrice
        matrix_group = QGroupBox("Configuration de la Matrice")
        matrix_layout = QVBoxLayout()
        matrix_layout.setSpacing(10)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Taille de la matrice:"))
        self.lu_size = QSpinBox()
        self.lu_size.setRange(2, 10)
        self.lu_size.setValue(3)
        self.lu_size.valueChanged.connect(self.update_lu_matrix_size)
        size_layout.addWidget(self.lu_size)

        matrix_layout.addLayout(size_layout)

        # Table pour la matrice
        self.lu_matrix_table = QTableWidget(3, 3)
        self.init_lu_table()

        matrix_layout.addWidget(self.lu_matrix_table)

        # Bouton de décomposition
        self.calc_lu = QPushButton("Calculer la Décomposition LU")
        self.calc_lu.clicked.connect(self.calculate_lu_decomposition)

        matrix_layout.addWidget(self.calc_lu)

        matrix_group.setLayout(matrix_layout)

        # Zone de résultats
        result_group = QGroupBox("Résultats de la Décomposition")
        result_layout = QVBoxLayout()

        self.lu_result = QTextEdit()
        self.lu_result.setReadOnly(True)

        result_layout.addWidget(self.lu_result)
        result_group.setLayout(result_layout)

        main_layout.addWidget(matrix_group)
        main_layout.addWidget(result_group)

        tab.setLayout(main_layout)
        return tab

    def init_tables(self):
        # Initialisation de la matrice A avec des valeurs par défaut
        size = self.system_size.value()
        self.matrix_table.setRowCount(size)
        self.matrix_table.setColumnCount(size)
        self.vector_table.setRowCount(size)
        self.vector_table.setColumnCount(1)

        # Exemple de matrice A et vecteur b
        A = [[], [], []]
        b = []

        for i in range(size):
            for j in range(size):
                item = QTableWidgetItem(str(A[i][j]) if i < len(A) and j < len(A[0]) else "0")
                item.setTextAlignment(Qt.AlignCenter)
                self.matrix_table.setItem(i, j, item)

            item = QTableWidgetItem(str(b[i]) if i < len(b) else "0")
            item.setTextAlignment(Qt.AlignCenter)
            self.vector_table.setItem(i, 0, item)

    def init_lu_table(self):
        # Initialisation de la matrice pour la décomposition LU
        size = self.lu_size.value()
        self.lu_matrix_table.setRowCount(size)
        self.lu_matrix_table.setColumnCount(size)

        # Exemple de matrice
        A = [[], [], []]

        for i in range(size):
            for j in range(size):
                item = QTableWidgetItem(str(A[i][j]) if i < len(A) and j < len(A[0]) else "0")
                item.setTextAlignment(Qt.AlignCenter)
                self.lu_matrix_table.setItem(i, j, item)

    def update_matrix_size(self):
        self.init_tables()

    def update_lu_matrix_size(self):
        self.init_lu_table()

    def calculate_integration(self, method):
        try:
            # Récupération des paramètres
            func_str = self.func_input.text()
            a = self.a_input.value()
            b = self.b_input.value()
            n = self.n_input.value()

            # Création de la fonction à partir de la chaîne
            f = lambda x: eval(func_str, {"__builtins__": {}},
                               {"x": x, "log": np.log, "exp": np.exp, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                                "sqrt": np.sqrt, "pi": np.pi})

            # Calcul de l'intégrale selon la méthode choisie
            if method == 'trapeze':
                result = self.trapezoidal(f, a, b, n)
                method_name = "Méthode des Trapèzes"
            elif method == 'simpson':
                result = self.simpson(f, a, b, n)
                method_name = "Méthode de Simpson"
            elif method == 'midpoint':
                result = self.midpoint(f, a, b, n)
                method_name = "Méthode du Point Milieu"

            # Affichage du résultat
            self.result_display.append(f"{method_name} (n={n}):\nI ≈ {result:.8f}\n")

            # Visualisation graphique
            self.plot_integration(f, a, b, n, method)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite: {str(e)}")

    def calculate_all_integrations(self):
        try:
            # Récupération des paramètres
            func_str = self.func_input.text()
            a = self.a_input.value()
            b = self.b_input.value()
            n = self.n_input.value()

            # Création de la fonction à partir de la chaîne
            f = lambda x: eval(func_str, {"__builtins__": {}},
                               {"x": x, "log": np.log, "exp": np.exp, "sin": np.sin, "cos": np.cos, "tan": np.tan,
                                "sqrt": np.sqrt, "pi": np.pi})

            # Calcul des intégrales avec les différentes méthodes
            trapeze_result = self.trapezoidal(f, a, b, n)
            simpson_result = self.simpson(f, a, b, n)
            midpoint_result = self.midpoint(f, a, b, n)

            # Affichage des résultats
            self.result_display.clear()
            self.result_display.append(f"Résultats pour f(x) = {func_str}, a = {a}, b = {b}, n = {n}:\n")
            self.result_display.append(f"Méthode des Trapèzes: {trapeze_result:.8f}")
            self.result_display.append(f"Méthode de Simpson: {simpson_result:.8f}")
            self.result_display.append(f"Méthode du Point Milieu: {midpoint_result:.8f}\n")

            # Calcul de la valeur exacte si possible
            try:
                from scipy import integrate
                exact_result = integrate.quad(f, a, b)[0]
                self.result_display.append(f"Valeur exacte (scipy.integrate): {exact_result:.8f}\n")

                # Calcul des erreurs
                trapeze_error = abs(exact_result - trapeze_result)
                simpson_error = abs(exact_result - simpson_result)
                midpoint_error = abs(exact_result - midpoint_result)

                self.result_display.append(f"Erreur Trapèzes: {trapeze_error:.2e}")
                self.result_display.append(f"Erreur Simpson: {simpson_error:.2e}")
                self.result_display.append(f"Erreur Point Milieu: {midpoint_error:.2e}\n")

            except ImportError:
                self.result_display.append("SciPy n'est pas installé, impossible de calculer la valeur exacte.")
            except Exception as e:
                self.result_display.append(f"Erreur lors du calcul de la valeur exacte: {str(e)}")

            # Visualisation graphique
            self.plot_integration(f, a, b, n, 'all')

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite: {str(e)}")

    def trapezoidal(self, f, a, b, n):
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = f(x)
        result = (h / 2) * (y[0] + 2 * np.sum(y[1:-1]) + y[-1])
        return result

    def simpson(self, f, a, b, n):
        if n % 2 != 0:
            n += 1  # Assurez-vous que n est pair
        h = (b - a) / n
        x = np.linspace(a, b, n + 1)
        y = f(x)
        result = (h / 3) * (y[0] + 4 * np.sum(y[1:-1:2]) + 2 * np.sum(y[2:-2:2]) + y[-1])
        return result

    def midpoint(self, f, a, b, n):
        h = (b - a) / n
        x_mid = np.linspace(a + h / 2, b - h / 2, n)
        y_mid = f(x_mid)
        result = h * np.sum(y_mid)
        return result

    def plot_integration(self, f, a, b, n, method):
        # Préparation des données
        x = np.linspace(a, b, 400)
        y = f(x)

        # Configuration du graphique
        self.plot_canvas.axes.clear()
        self.plot_canvas.axes.plot(x, y, label="f(x)", color="#3498db")

        # Affichage des rectangles pour chaque méthode
        if method == 'trapeze' or method == 'all':
            x_trap = np.linspace(a, b, n + 1)
            y_trap = f(x_trap)
            for i in range(n):
                x_rect = [x_trap[i], x_trap[i], x_trap[i+1], x_trap[i+1], x_trap[i]]
                y_rect = [0, y_trap[i], y_trap[i+1], 0, 0]
                self.plot_canvas.axes.fill(x_rect, y_rect, alpha=0.2, color="#e74c3c", label="Trapèzes" if i == 0 else "")

        elif method == 'simpson' or method == 'all':
            x_simp = np.linspace(a, b, n + 1)
            y_simp = f(x_simp)
            for i in range(0, n, 2):
                x_rect = [x_simp[i], x_simp[i], x_simp[i+2], x_simp[i+2], x_simp[i]]
                y_rect = [0, y_simp[i], y_simp[i+2], 0, 0]
                self.plot_canvas.axes.fill(x_rect, y_rect, alpha=0.2, color="#2ecc71", label="Simpson" if i == 0 else "")

        elif method == 'midpoint' or method == 'all':
            h = (b - a) / n
            x_mid = np.linspace(a + h / 2, b - h / 2, n)
            y_mid = f(x_mid)
            for i in range(n):
                x_rect = [x_mid[i] - h/2, x_mid[i] - h/2, x_mid[i] + h/2, x_mid[i] + h/2, x_mid[i] - h/2]
                y_rect = [0, y_mid[i], y_mid[i], 0, 0]
                self.plot_canvas.axes.fill(x_rect, y_rect, alpha=0.2, color="#f39c12", label="Point Milieu" if i == 0 else "")

        self.plot_canvas.axes.set_title("Visualisation de l'Intégration Numérique", fontsize=12)
        self.plot_canvas.axes.set_xlabel("x", fontsize=10)
        self.plot_canvas.axes.set_ylabel("f(x)", fontsize=10)
        self.plot_canvas.axes.legend()
        self.plot_canvas.axes.grid(True)
        self.plot_canvas.fig.tight_layout()  # Ajuste la mise en page
        self.plot_canvas.draw()

    def solve_linear_system(self, method):
        try:
            # Récupérer les données du tableau
            size = self.system_size.value()
            A = np.zeros((size, size))
            b = np.zeros(size)

            for i in range(size):
                for j in range(size):
                    item = self.matrix_table.item(i, j)
                    A[i, j] = float(item.text()) if item is not None else 0

                item = self.vector_table.item(i, 0)
                b[i] = float(item.text()) if item is not None else 0

            # Récupérer les paramètres itératifs
            max_iter = self.max_iter.value()
            tolerance = float(self.tolerance.text())

            # Résoudre le système selon la méthode choisie
            if method == 'jacobi':
                x = self.jacobi(A, b, max_iter, tolerance)
                method_name = "Méthode de Jacobi"
            elif method == 'gauss_seidel':
                x = self.gauss_seidel(A, b, max_iter, tolerance)
                method_name = "Méthode de Gauss-Seidel"
            elif method == 'direct':
                x = np.linalg.solve(A, b)
                method_name = "Méthode Directe"

            # Afficher les résultats
            self.system_result.clear()
            if x is not None:
                self.system_result.append(f"{method_name}:\n")
                for i, val in enumerate(x):
                    self.system_result.append(f"x[{i+1}] = {val:.8f}")
            else:
                self.system_result.append(f"La méthode {method_name} n'a pas convergé.")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite: {str(e)}")

    def jacobi(self, A, b, max_iter, tolerance):
        n = A.shape[0]
        x = np.zeros(n)  # Initialisation de la solution
        x_new = np.zeros(n)

        for iteration in range(max_iter):
            for i in range(n):
                s1 = np.sum(A[i, :i] * x[:i])
                s2 = np.sum(A[i, i+1:] * x[i+1:])
                x_new[i] = (b[i] - s1 - s2) / A[i, i]

            # Vérification de la convergence
            if np.allclose(x, x_new, atol=tolerance):
                return x_new

            x, x_new = x_new, x  # Mise à jour de la solution

        return None  # La méthode n'a pas convergé

    def gauss_seidel(self, A, b, max_iter, tolerance):
        n = A.shape[0]
        x = np.zeros(n)  # Initialisation de la solution

        for iteration in range(max_iter):
            x_old = x.copy()
            for i in range(n):
                s1 = np.sum(A[i, :i] * x[:i])
                s2 = np.sum(A[i, i+1:] * x_old[i+1:])
                x[i] = (b[i] - s1 - s2) / A[i, i]

            # Vérification de la convergence
            if np.allclose(x, x_old, atol=tolerance):
                return x

        return None  # La méthode n'a pas convergé

    def calculate_lu_decomposition(self):
        try:
            # Récupérer les données du tableau
            size = self.lu_size.value()
            A = np.zeros((size, size))

            for i in range(size):
                for j in range(size):
                    item = self.lu_matrix_table.item(i, j)
                    A[i, j] = float(item.text()) if item is not None else 0

            # Effectuer la décomposition LU
            L, U = self.lu_decomposition(A)

            # Afficher les résultats
            self.lu_result.clear()
            self.lu_result.append("Matrice L (Inférieure):\n")
            self.lu_result.append(np.array_str(L, precision=4, suppress_small=True))
            self.lu_result.append("\n\nMatrice U (Supérieure):\n")
            self.lu_result.append(np.array_str(U, precision=4, suppress_small=True))

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur s'est produite: {str(e)}")

    def lu_decomposition(self, A):
        n = A.shape[0]
        L = np.eye(n)
        U = np.copy(A)

        for i in range(n):
            # Normalisation de la colonne i
            factor = U[i+1:, i] / U[i, i]
            L[i+1:, i] = factor

            # Soustraction des lignes
            U[i+1:] -= factor[:, np.newaxis] * U[i]

        return L, U

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ODESolverApp()
    window.show()
    sys.exit(app.exec_())
