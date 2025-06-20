import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QHBoxLayout, QApplication, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pandas as pd

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class EnergyDigitizationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Énergétique Moderne")
        self.setMinimumSize(900, 650)
        self.setStyleSheet("""
            QWidget { background-color: #f5f7fa; }
            QPushButton { border-radius: 8px; padding: 10px; font-size: 14px; }
            QLabel#desc { color: #4a4a4a; font-size: 13px; }
            QLabel#stats { color: #2d2d2d; font-size: 12px; }
        """)

        layout = QVBoxLayout(self)

        # Citation pédagogique
        desc = QLabel(
            "⚡ <b>Numérisation et la dématérialisation des technologies du marché de l’énergie</b><br>"
            "<span style='font-size:10pt;'>Ce module vous permet d'analyser et de visualiser vos données énergétiques.</span>"
        )
        desc.setObjectName("desc")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 12))
        layout.addWidget(desc)

        # Boutons principaux
        btn_layout = QHBoxLayout()
        self.load_button = QPushButton("Charger un fichier CSV")
        self.load_button.setToolTip("Charger vos propres données énergétiques au format CSV")
        self.example_button = QPushButton("Charger un exemple")
        self.example_button.setToolTip("Charger un exemple de données pour tester l'interface")
        self.help_button = QPushButton("Aide ?")
        self.help_button.setToolTip("Afficher l'aide sur ce module")
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.example_button)
        btn_layout.addWidget(self.help_button)
        layout.addLayout(btn_layout)

        # Tableau des données
        self.table = QTableWidget()
        layout.addWidget(self.table)

        # Label pour les statistiques
        self.stats_label = QLabel("")
        self.stats_label.setObjectName("stats")
        self.stats_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.stats_label)

        # Espace graphique intégré
        self.figure = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

        # Bouton pour tracer le graphique
        self.plot_button = QPushButton("Tracer le graphique de consommation")
        self.plot_button.setToolTip("Visualiser la consommation énergétique dans l'interface")
        layout.addWidget(self.plot_button)

        # Connexion des signaux
        self.load_button.clicked.connect(self.load_data)
        self.example_button.clicked.connect(self.load_example)
        self.help_button.clicked.connect(self.show_help)
        self.plot_button.clicked.connect(self.plot_data)

        self.data = None

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier CSV", "", "CSV Files (*.csv)")
        if file_name:
            try:
                self.data = pd.read_csv(file_name)
                self.display_data()
                self.show_stats()
                self.clear_plot()
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de charger le fichier : {e}")

    def load_example(self):
        from io import StringIO
        example_csv = StringIO(
            "Date,Consommation,Production\n"
            "2025-05-01,150,200\n"
            "2025-05-02,160,210\n"
            "2025-05-03,145,205\n"
            "2025-05-04,170,220\n"
        )
        self.data = pd.read_csv(example_csv)
        self.display_data()
        self.show_stats()
        self.clear_plot()

    def display_data(self):
        if self.data is not None:
            self.table.setRowCount(self.data.shape[0])
            self.table.setColumnCount(self.data.shape[1])
            self.table.setHorizontalHeaderLabels(self.data.columns)
            for i in range(self.data.shape[0]):
                for j in range(self.data.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(self.data.iat[i, j])))

    def show_stats(self):
        if self.data is not None and 'Consommation' in self.data.columns:
            total = self.data['Consommation'].sum()
            mean = self.data['Consommation'].mean()
            maxi = self.data['Consommation'].max()
            mini = self.data['Consommation'].min()
            self.stats_label.setText(
                f"<b>Consommation totale :</b> {total:.2f} kWh<br>"
                f"<b>Consommation moyenne :</b> {mean:.2f} kWh<br>"
                f"<b>Maximum :</b> {maxi:.2f} kWh &nbsp;&nbsp; <b>Minimum :</b> {mini:.2f} kWh"
            )
        else:
            self.stats_label.setText("Aucune colonne 'Consommation' trouvée dans les données.")

    def plot_data(self):
        if self.data is not None and 'Date' in self.data.columns and 'Consommation' in self.data.columns:
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(self.data['Date'], self.data['Consommation'], marker='o', color='#0077b6')
            ax.set_title("Consommation énergétique")
            ax.set_xlabel("Date")
            ax.set_ylabel("Consommation (kWh)")
            ax.grid(True, linestyle='--', alpha=0.6)
            self.figure.tight_layout()
            self.canvas.draw()
        else:
            QMessageBox.warning(self, "Avertissement", "Impossible d'afficher le graphique : données incomplètes.")

    def clear_plot(self):
        self.figure.clear()
        self.canvas.draw()

    def show_help(self):
        QMessageBox.information(self, "Aide - Gestion Énergétique",
            "Ce module vous permet de charger et d’analyser des données énergétiques.\n\n"
            "• Utilisez 'Charger un fichier CSV' pour importer vos propres données.\n"
            "• Cliquez sur 'Charger un exemple' pour tester l’interface avec des données fictives.\n"
            "• Visualisez les statistiques et affichez un graphique pour mieux comprendre votre consommation.\n\n"
            "Astuce : Les colonnes attendues sont 'Date', 'Consommation' et 'Production'.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = EnergyDigitizationTab()
    win.show()
    sys.exit(app.exec_())
