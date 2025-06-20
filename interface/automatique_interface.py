# -*- coding: utf-8 -*-

import sys
import numpy as np
import scipy.signal as sg
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QGroupBox, QTabWidget, QMessageBox
)
from PyQt5.QtGui import QIcon, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class SystemAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analyse de Fonction de Transfert")
        self.setGeometry(100, 100, 1100, 900)
        self.setWindowIcon(QIcon("icon.png"))  # Assurez-vous d'avoir une icône
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 18px;
                color: #2c3e50;
            }
            QLineEdit {
                background: #ffffff;
                border: 1px solid #bdc3c7;
                padding: 10px;
                font-size: 16px;
                border-radius: 8px;
            }
            QTextEdit {
                background: #ffffff;
                border: 1px solid #bdc3c7;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 10px;
                padding: 12px 18px;
                font-size: 16px;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f6fa0;
            }
            QGroupBox {
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: #ffffff;
            }
            QGroupBox:title {
                color: #3498db;
                font-size: 22px;
                font-weight: bold;
            }
            QTabWidget {
                font-size: 16px;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px;
                border-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #d6eaf8;
            }
        """)
        self.initUI()

    def initUI(self):
        # Création de l'onglet pour organiser les sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabWidget::pane { border: none; }")
        self.setCentralWidget(self.tabs)

        # Onglet Paramètres
        self.param_widget = QWidget()
        self.param_layout = QVBoxLayout()

        self.label_num = QLabel("Numérateur (séparé par des virgules) :")
        self.input_num = QLineEdit()

        self.label_den = QLabel("Dénominateur (séparé par des virgules) :")
        self.input_den = QLineEdit()

        self.analyze_button = QPushButton("🔍 Analyser")
        self.save_button = QPushButton("💾 Enregistrer Résultats")
        self.reset_button = QPushButton("🔄 Réinitialiser Tout")
        self.quit_button = QPushButton("❌ Quitter")

        self.param_layout.addWidget(self.label_num)
        self.param_layout.addWidget(self.input_num)
        self.param_layout.addWidget(self.label_den)
        self.param_layout.addWidget(self.input_den)
        self.param_layout.addWidget(self.analyze_button)
        self.param_layout.addWidget(self.save_button)
        self.param_layout.addWidget(self.reset_button)
        self.param_layout.addWidget(self.quit_button)
        self.param_widget.setLayout(self.param_layout)

        # Onglet Résultats
        self.result_widget = QWidget()
        self.result_layout = QVBoxLayout()

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        self.result_layout.addWidget(QLabel("Résultats :"))
        self.result_layout.addWidget(self.result_text)

        self.result_widget.setLayout(self.result_layout)

        # Onglet Graphiques
        self.graph_widget = QWidget()
        self.graph_layout = QVBoxLayout()
        self.graph_widget.setLayout(self.graph_layout)

        self.tabs.addTab(self.param_widget, "Paramètres")
        self.tabs.addTab(self.result_widget, "Résultats")
        self.tabs.addTab(self.graph_widget, "Graphiques")

        # Connexions des boutons
        self.analyze_button.clicked.connect(self.analyze_transfer_function)
        self.save_button.clicked.connect(self.save_results)
        self.reset_button.clicked.connect(self.reset_all)
        self.quit_button.clicked.connect(self.close)

    def clear_graphs(self):
        while self.graph_layout.count():
            child = self.graph_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def plot_step_response(self, num, den):
        sys_tf = sg.TransferFunction(num, den)
        t, y = sg.step(sys_tf)

        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(t, y, label="Réponse en échelon", color="#3498db")
        ax.set_title("Réponse en échelon")
        ax.set_xlabel("Temps (s)")
        ax.set_ylabel("Réponse")
        ax.grid(True)
        ax.legend()

        self.step_fig = fig
        canvas = FigureCanvas(fig)
        self.graph_layout.addWidget(canvas)

    def plot_bode(self, num, den):
        sys_tf = sg.TransferFunction(num, den)
        w, mag, phase = sys_tf.bode()

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8))
        ax1.semilogx(w, mag, color="#3498db")
        ax1.set_title("Diagramme de Bode - Gain")
        ax1.set_ylabel("Gain (dB)")
        ax1.grid(True)

        ax2.semilogx(w, phase, color="#2ecc71")
        ax2.set_title("Diagramme de Bode - Phase")
        ax2.set_xlabel("Fréquence (rad/s)")
        ax2.set_ylabel("Phase (°)")
        ax2.grid(True)

        self.bode_fig = fig
        canvas = FigureCanvas(fig)
        self.graph_layout.addWidget(canvas)

    def analyze_transfer_function(self):
        try:
            num = list(map(float, self.input_num.text().split(',')))
            den = list(map(float, self.input_den.text().split(',')))
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer des coefficients valides.")
            return

        if len(den) < 2:
            QMessageBox.warning(self, "Erreur", "Le dénominateur doit avoir au moins deux termes.")
            return

        sys_tf = sg.TransferFunction(num, den)
        zeros, poles, _ = sg.tf2zpk(num, den)
        order = len(den) - 1
        stable = all(np.real(p) < 0 for p in poles)

        result = f"Ordre du système : {order}\n"
        result += f"Pôles : {poles}\nZéros : {zeros}\n"
        result += f"Stabilité : {'Stable' if stable else 'Instable'}\n"

        if order == 1:
            try:
                tau = -1 / np.real(poles[0])
                result += f"Constante de temps τ : {tau:.2f} s\n"
                result += f"Temps de réponse ≈ 4τ : {4 * tau:.2f} s\n"
                result += f"Temps de montée ≈ 2.2τ : {2.2 * tau:.2f} s\n"
            except:
                result += "Erreur premier ordre.\n"
        elif order == 2:
            try:
                wn = np.abs(poles[0])
                zeta = -np.real(poles[0]) / wn if wn != 0 else 0
                gain_statique = num[-1] / den[-1] if den[-1] != 0 else 0

                result += f"Gain statique : {gain_statique:.2f}\n"
                result += f"Amortissement ζ : {zeta:.3f}\n"
                result += f"Pulsation propre ω₀ : {wn:.3f} rad/s\n"

                if zeta < 1:
                    Mp = np.exp(-np.pi * zeta / np.sqrt(1 - zeta ** 2)) * 100
                    tr = 1.8 / wn
                    fc = wn * np.sqrt(1 - zeta ** 2)
                    ts = 4 / (zeta * wn)

                    result += f"Dépassement Mp : {Mp:.2f} %\n"
                    result += f"Temps de montée ≈ {tr:.2f} s\n"
                    result += f"Fréquence de coupure ≈ {fc:.2f} rad/s\n"
                    result += f"Temps de stabilisation ≈ {ts:.2f} s\n"
                else:
                    result += "Système sur-amorti (ζ ≥ 1).\n"
            except Exception as e:
                result += f"Erreur second ordre : {e}\n"
        else:
            result += "Analyse limitée au premier et deuxième ordre."

        self.result_text.setPlainText(result)

        self.clear_graphs()
        self.plot_step_response(num, den)
        self.plot_bode(num, den)

    def save_results(self):
        text = self.result_text.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Attention", "Aucun résultat à enregistrer.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Enregistrer Résultats", "", "Fichiers texte (*.txt)",
                                                   options=options)
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(text)
                if hasattr(self, 'step_fig'):
                    self.step_fig.savefig(file_name.replace('.txt', '_step.png'))
                if hasattr(self, 'bode_fig'):
                    self.bode_fig.savefig(file_name.replace('.txt', '_bode.png'))
                QMessageBox.information(self, "Succès", "Résultats et graphes enregistrés.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur d'enregistrement : {e}")

    def reset_all(self):
        self.input_num.clear()
        self.input_den.clear()
        self.result_text.clear()
        self.clear_graphs()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemAnalysisApp()
    window.show()
    sys.exit(app.exec_())
