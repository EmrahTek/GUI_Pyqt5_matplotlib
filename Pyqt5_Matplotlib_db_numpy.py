
#*****************************
# Here ist Master Branch
#*****************************

"""
What does the application do?

Left: Student name, grades (separated by commas), weights (optional, sum must be 1).
Calculate: Calculates the average and weighted average using NumPy.
Save: Writes the result to the grades.db SQLite database.
Refresh: Pulls records from the database into the table.
Graph: Displays students' weighted averages in a bar chart in the Matplotlib area on the right.
Usage tips

If you don't enter weights, the weighted average = simple average.
If you enter weights, the length should be the same as the number of grades and the total should be 1 (e.g., 0.4,0.3,0.3).
An error message box appears in case of errors.

Author: Emrah Tekin
Date: 04.09.2025
Version: 0.1

"""
# TO DO List
# 1.) GUI icin tarih saat eklenebilir. her acildiginda güncel olsun. bunu feture ile yapmayi dene

import sys
import json # The json module converts Python objects to strings. 
import sqlite3
import numpy as np


# PyQt5 and Matplotlib for GUI and plotting
from PyQt5 import QtCore,QtWidgets # QtCore für datum,zeit
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel,QLineEdit, QTextEdit, QPushButton, QTableWidget,
    QTableWidgetItem,QMessageBox, QGroupBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Qt icine gömülü matplotlib tuvali
class MplCanvas(FigureCanvas): 
    """A matplotlib canvas embedded in Qt. """
    def __init__(self, parent=None, width=5, height = 3, dpi = 100):
        # Create a Matplotlib Figure and attach an Axes.
        self.fig = Figure(figsize = (width,height), dpi=dpi)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
    def clear(self):
        # Clear axes for fresh plotting.
        self.ax.clear()
        self.draw()

class GeradeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerade Calculation Numpy + SQLite + Matplotlib")
        self.resize(1100,700) # the window is displayed at 1100x700 when first opened

        # Initialize DB. (veritabanini baslat)
        self.conn = sqlite3.connect("grades.db")  # conn -> connetion kelimesinin kisaltmasidir. cursor ise sorgu calistirma aracidir.
        self.create_tables()

        # Build UI. (Arayüzü kur)
        # QMainWindow -> dis iskelet
        central = QWidget() # ic ana kutu
        self.setCentralWidget(central) # o kutuyu QMainWindow takiyoruz. 
        main_layout = QHBoxLayout(central) # o kutuya "yatay düzen veriyoruz"

        # Left: Inputs and actions (sol girdiler ve islemler)

        left_panel = QVBoxLayout() # Yeni bir dikey layout olusturuyoruz. 
        main_layout.addLayout(left_panel,2)

    #    left_panel.addWidget(self._build_input_group()) # alttan tireli fonksiyonlar sadece bulunduklari klasslarda kullanilir. 
    #    left_panel.addWidget(self._build_action_group())
        left_panel.addStretch(1)

        # Middle: Table(Orta:Tablo)
        mid_panel = QVBoxLayout()
        main_layout.addLayout(mid_panel,2)

        self.table = QTableWidget(0,5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Name", "Grades","Mean", "Weighted"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)
        mid_panel.addWidget(QLabel("Kayitli Sonuclar (Saved Results)"))
        mid_panel.addWidget(self.table)

        # Right: Plot
        right_panel = QVBoxLayout()
        main_layout.addLayout(right_panel, 3)

        self.canvas = MplCanvas(self, width=6,height=4, dpi=100)
        right_panel.addWidget(QLabel("Matplotlib Plot"))
        right_panel.addWidget(self.canvas)

        # Load existing records into table at startup.
    #    self.load_all_records()
        # Initial plot
    #    self.plot_averages()

    def create_tables(self):
        """Create SqLite tables if not exist."""
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grades TEXT NOT NULL,  -- JSON array of numbers(Sayilarin JSON dizisi)
                mean REAL NOT NULL,
                weighted REAL NOT NULL,
                weights TEXT        -- JSON array or NULL(JSON dizi ya da NULL)
            );

            """
        )

        self.conn.commit()

    def __build_input_group(self) -> QGroupBox:
         """Input widgets for name, grades,weights.(isim,notlar,agirliklar icin giris bilesenleri)"""
         group = QGroupBox("Girdi (input)")
         layout = QVBoxLayout(group)

         # Name field(isim alani)
         row_name = QHBoxLayout()
         row_name.addWidget(QLabel("Ögrenci Adi (Student Name): "))
         self.name_edit = QLineEdit()
         self.name_edit.setPlaceholderText("örn: Ali Veli")
         row_name.addWidget(self.name_edit)
         layout.addLayout(row_name)

         # Grades field 
         row_grades = QVBoxLayout()
         row_grades.addWidget(QLabel("Notlar(Grades, comma-separated / virgüller):"))
         self.grades_edit = QLineEdit()
         self.grades_edit.setPlaceholderText("örn: 90, 80, 75, 88")
         row_grades.addWidget(self.grades_edit)
         layout.addLayout(row_grades)

         # Weights field (Agirliklar alani)
         row_weights = QVBoxLayout()
         row_weights.addWidget(QLabel("Agirliklar(Weights, optional / istege bagli: )"))
         self.weights_edit = QLineEdit()
         self.weights_edit.setPlaceholderText("Örn: 0.4,0.,0.3(toplami 1 olmali)")
         row_weights.addWidget(self.weights_edit)
         layout.addLayout(row_weights)

         # Output labels 
         out_row = QHBoxLayout()
         self.mean_label = QLabel("Ortalama ( Mean ): -")
         self.weighted_label = QLabel("Agirlikli (Weighted): -")
         out_row.addWidget(self.mean_label)
         out_row.addWidget(self.weighted_label)
         layout.addLayout(out_row)
         return group


































#*************main********************

def main():
        """Entry point. """
        app = QApplication(sys.argv)
        win = GeradeApp()
        win.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()



