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

class DataScienceTab(QWidget):
    def __init__(self, db_manager=None):
        super().__init__()
        self.setWindowTitle("Outils Data Science")
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
            "📊 <b>Émergence des sciences analytiques (sciences des données)</b><br>"
            "<span style='font-size:10pt;'>Permettant une prédiction et une personnalisation ciblée des services.</span>"
        )
        desc.setObjectName("desc")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setFont(QFont("Segoe UI", 12))
        layout.addWidget(desc)

        # Boutons principaux
        btn_layout = QHBoxLayout()
        self.load_button = QPushButton("Charger un fichier CSV")
        self.load_button.setToolTip("Charger vos propres données au format CSV")
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
        self.plot_button = QPushButton("Tracer un graphique")
        self.plot_button.setToolTip("Visualiser une colonne numérique dans l'interface")
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
            "Nom,Age,Sexe,Note_Maths,Note_Physique\n"
            "Alice,22,F,15,14\n"
            "Bob,23,M,12,16\n"
            "Claire,21,F,17,13\n"
            "David,24,M,10,15\n"
            "Eva,22,F,16,18\n"
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
        if self.data is not None:
            # Affiche les stats sur les colonnes numériques
            desc = self.data.describe().T
            stats_html = "<b>Statistiques descriptives :</b><br>"
            for col in desc.index:
                stats_html += (f"<b>{col}</b> : Moyenne = {desc.loc[col, 'mean']:.2f}, "
                               f"Min = {desc.loc[col, 'min']:.2f}, Max = {desc.loc[col, 'max']:.2f}<br>")
            self.stats_label.setText(stats_html)
        else:
            self.stats_label.setText("Aucune donnée chargée.")

    def plot_data(self):
        if self.data is not None:
            # Recherche la première colonne numérique à tracer
            num_cols = self.data.select_dtypes(include='number').columns
            if len(num_cols) == 0:
                QMessageBox.warning(self, "Avertissement", "Aucune colonne numérique à tracer.")
                return
            y_col = num_cols[0]
            x_col = self.data.columns[0]  # première colonne (souvent un nom ou un identifiant)
            self.figure.clear()
            ax = self.figure.add_subplot(111)
            ax.plot(self.data[x_col], self.data[y_col], marker='o', color='#0077b6')
            ax.set_title(f"{y_col} en fonction de {x_col}")
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.grid(True, linestyle='--', alpha=0.6)
            self.figure.tight_layout()
            self.canvas.draw()
        else:
            QMessageBox.warning(self, "Avertissement", "Aucune donnée à tracer.")

    def clear_plot(self):
        self.figure.clear()
        self.canvas.draw()

    def show_help(self):
        QMessageBox.information(self, "Aide - Outils Data Science",
            "Ce module vous permet de charger et d’analyser des données tabulaires (CSV).\n\n"
            "• Utilisez 'Charger un fichier CSV' pour importer vos propres données.\n"
            "• Cliquez sur 'Charger un exemple' pour tester l’interface avec des données fictives.\n"
            "• Visualisez les statistiques descriptives et affichez un graphique pour mieux comprendre vos données.\n\n"
            "Astuce : Les colonnes numériques sont reconnues automatiquement pour la visualisation.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DataScienceTab()
    win.show()
    sys.exit(app.exec_())
