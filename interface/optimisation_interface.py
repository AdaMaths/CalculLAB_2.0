import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QTextEdit, QComboBox, QMessageBox, QHeaderView)
from PyQt5.QtGui import QIcon
import pulp 


class OptimizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = None
        self.problem_tab = None
        self.results_tab = None
        self.var_table = None
        self.var_count = None
        self.constraint_table = None
        self.objective_combo = None
        self.results_text = None

        self.setWindowTitle("Optimisation Industrielle Pro - OLExpert")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon("icon.png"))

        self.initUI()
        self.setDarkTheme()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Onglets
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Onglet configuration problème
        self.problem_tab = QWidget()
        self.tabs.addTab(self.problem_tab, "Configuration du Problème")
        self.setupProblemTab()

        # Onglet résultats
        self.results_tab = QWidget()
        self.tabs.addTab(self.results_tab, "Résultats")
        self.setupResultsTab()

    def setupProblemTab(self):
        layout = QVBoxLayout()
        self.problem_tab.setLayout(layout)

        # Variables
        variables_layout = QVBoxLayout()
        variables_layout.addWidget(QLabel("Variables de Décision:"))

        self.var_table = QTableWidget()
        self.var_table.setColumnCount(3)
        self.var_table.setHorizontalHeaderLabels(["Nom Variable", "Coefficient Objectif", "Type"])
        self.var_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        variables_layout.addWidget(self.var_table)

        var_controls = QHBoxLayout()
        self.var_count = QLineEdit()
        self.var_count.setPlaceholderText("Nombre de variables")
        var_controls.addWidget(self.var_count)

        btn_add_var = QPushButton("Générer Table Variables")
        btn_add_var.clicked.connect(self.generateVarTable)
        var_controls.addWidget(btn_add_var)

        variables_layout.addLayout(var_controls)
        layout.addLayout(variables_layout)

        # Contraintes
        constraints_layout = QVBoxLayout()
        constraints_layout.addWidget(QLabel("Contraintes:"))

        self.constraint_table = QTableWidget()
        self.constraint_table.setColumnCount(4)
        self.constraint_table.setHorizontalHeaderLabels(["Coefficients", "Signe", "Valeur", "Type"])
        self.constraint_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        constraints_layout.addWidget(self.constraint_table)

        constraint_controls = QHBoxLayout()
        btn_add_constraint = QPushButton("Ajouter Contrainte")
        btn_add_constraint.clicked.connect(self.addConstraint)
        constraint_controls.addWidget(btn_add_constraint)

        btn_remove_constraint = QPushButton("Supprimer Contrainte")
        btn_remove_constraint.clicked.connect(self.removeConstraint)
        constraint_controls.addWidget(btn_remove_constraint)

        constraints_layout.addLayout(constraint_controls)
        layout.addLayout(constraints_layout)

        # Objectif
        objective_layout = QHBoxLayout()
        objective_layout.addWidget(QLabel("Objectif:"))

        self.objective_combo = QComboBox()
        self.objective_combo.addItems(["Maximiser", "Minimiser"])
        objective_layout.addWidget(self.objective_combo)

        btn_solve = QPushButton("Résoudre le Problème")
        btn_solve.clicked.connect(self.solveProblem)
        btn_solve.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        objective_layout.addWidget(btn_solve)

        layout.addLayout(objective_layout)

    def setupResultsTab(self):
        layout = QVBoxLayout()
        self.results_tab.setLayout(layout)

        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def setDarkTheme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #23272E;
                color: #F5F5F5;
                font-size: 12pt;
            }
            QTabWidget::pane {
                border: 1px solid #707070;
            }
            QTabBar::tab {
                background: #2D333B;
                color: #F5F5F5;
                padding: 10px 20px;
                border: 1px solid #707070;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3A3F4B;
                border-bottom-color: #3A3F4B;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background: #4B5363;
            }
            QTableWidget {
                background-color: #292D36;
                color: #FAFAFA;
                gridline-color: #505050;
                selection-background-color: #4B6EAF;
                selection-color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #4B5363;
                color: #FFFFFF;
                font-weight: bold;
            }
            QPushButton {
                background-color: #4B6EAF;
                color: #FFFFFF;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #6A8DD6;
            }
            QLineEdit, QTextEdit {
                background-color: #23272E;
                color: #F5F5F5;
                border: 1px solid #4B5363;
            }
            QComboBox {
                background-color: #23272E;
                color: #F5F5F5;
                border: 1px solid #4B5363;
            }
            QMessageBox {
                background-color: #23272E;
                color: #F5F5F5;
            }
        """)

    def generateVarTable(self):
        try:
            num_vars = int(self.var_count.text())
            self.var_table.setRowCount(num_vars)
            for row in range(num_vars):
                self.var_table.setItem(row, 0, QTableWidgetItem(f"x{row + 1}"))
                self.var_table.setItem(row, 1, QTableWidgetItem("0"))

                combo = QComboBox()
                combo.addItems(["Libre", "≥ 0"])
                self.var_table.setCellWidget(row, 2, combo)
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer un nombre valide de variables")

    def addConstraint(self):
        row = self.constraint_table.rowCount()
        self.constraint_table.insertRow(row)

        coeffs = QLineEdit()
        coeffs.setPlaceholderText("Ex: 1, 2, 3")
        self.constraint_table.setCellWidget(row, 0, coeffs)

        sign_combo = QComboBox()
        sign_combo.addItems(["≤", "=", "≥"])
        self.constraint_table.setCellWidget(row, 1, sign_combo)

        value = QLineEdit("0")
        self.constraint_table.setCellWidget(row, 2, value)

    def removeConstraint(self):
        current_row = self.constraint_table.currentRow()
        if current_row >= 0:
            self.constraint_table.removeRow(current_row)

    def solveProblem(self):
        try:
            # Variables
            num_vars = self.var_table.rowCount()
            var_names = [self.var_table.item(row, 0).text() for row in range(num_vars)]
            obj_coeffs = [float(self.var_table.item(row, 1).text()) for row in range(num_vars)]

            # Création du problème
            if self.objective_combo.currentText() == "Maximiser":
                prob = pulp.LpProblem("Probleme_Optimisation", pulp.LpMaximize)
            else:
                prob = pulp.LpProblem("Probleme_Optimisation", pulp.LpMinimize)

            # Déclaration variables
            variables = []
            for row in range(num_vars):
                var_type = self.var_table.cellWidget(row, 2).currentText()
                if var_type == "≥ 0":
                    var = pulp.LpVariable(var_names[row], lowBound=0)
                else:
                    var = pulp.LpVariable(var_names[row])
                variables.append(var)

            # Fonction objectif
            prob += pulp.lpSum([coeff * var for coeff, var in zip(obj_coeffs, variables)])

            # Contraintes
            for row in range(self.constraint_table.rowCount()):
                coeffs_text = self.constraint_table.cellWidget(row, 0).text()
                coeffs = [float(c.strip()) for c in coeffs_text.split(",")]
                sign = self.constraint_table.cellWidget(row, 1).currentText()
                rhs = float(self.constraint_table.cellWidget(row, 2).text())

                lhs = pulp.lpSum([coeff * var for coeff, var in zip(coeffs, variables)])

                if sign == "≤":
                    prob += lhs <= rhs
                elif sign == "≥":
                    prob += lhs >= rhs
                else:
                    prob += lhs == rhs

            # Résolution
            prob.solve()

            # Résultats texte
            result_text = f"Statut de la solution: {pulp.LpStatus[prob.status]}\n\n"
            result_text += "Valeurs optimales:\n"
            for var in variables:
                val = var.varValue
                result_text += f"{var.name}: {val:.2f}\n" if val is not None else f"{var.name}: None\n"

            result_text += f"\nValeur optimale de la fonction objectif: {pulp.value(prob.objective):.2f}\n"

            # Multiplicateurs duaux (valeurs duales)
            result_text += "\nMultiplicateurs duaux (valeurs duales des contraintes):\n"
            for name, constraint in prob.constraints.items():
                pi = getattr(constraint, 'pi', None)
                if pi is not None:
                    result_text += f"{name}: {pi:.2f}\n"
                else:
                    result_text += f"{name}: N/A\n"

            self.results_text.setPlainText(result_text)

            # Bascule sur l'onglet résultats
            self.tabs.setCurrentWidget(self.results_tab)

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OptimizationApp()
    window.show()
    sys.exit(app.exec_())
