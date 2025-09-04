
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

        left_panel.addWidget(self._build_input_group()) # alttan tireli fonksiyonlar sadece bulunduklari klasslarda kullanilir. 
        left_panel.addWidget(self._build_action_group())
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
        self.load_all_records()
        # Initial plot
        self.plot_averages()

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
    def __build_action_group(self) -> QGroupBox:
         """Buttons to compute,save,load,plot. """
         group = QGroupBox("Actions")
         layout = QHBoxLayout(group)

         self.btn_compute = QPushButton("Hesapla(Compute)")
         self.btn_compute.clicked.connect(self.compute_grades)
         layout.addWidget(self.btn_compute)

         self.btn_save = QPushButton("Save DB")
         self.btn_save.clicked.connect(self.save_record())
         layout.addWidget(self.btn_save)

         self.btn_load = QPushButton("Reload")
         self.btn_load.clicked.connect(self.load_all_records)
         layout.addWidget(self.btn_load)

         self.btn_plot = QPushButton("Plot")
         self.btn_plot.clicked.connect(self.plot_averages)
         layout.addWidget(self.btn_plot)

         return group
    #----------------------Utility / Calculation(Araclar / Hesaplama)---------------
    def _parse_numbers(self, text: str) -> np.ndarray:
         """
            Parse a comma -separated string into a Numpy array of floats.
            (virgülle ayrilmis yaziyi Numpy float dizisine cevir.)
         """
         try:
              # Split by comma, strip spaces, filter empty, covert to float. 
              nums = [float(x.strip()) for x in text.split(',') if x.strip() != '']
              if not nums:
                   raise ValueError("No numbers parsed")
              return np.array(nums, dtype=float)
         except Exception:
              raise ValueError("Gecersiz sayi formati. örnek: 90, 80,75 ( Invalid number format)")
    def compute_grades(self):
        """ Compute mean and weighted average using Numpy; update labels. """
        try:
            name = self.name_edit.text().strip()

            if not name:
                raise ValueError    ("Lütfen ögrenci adi giriniz")
              
            grades = self._parse_numbers(self.grades_edit.text())
            # If weights provided,validate and use np.average
            weights_text =self.weights_edit.text().strip()
              
            if weights_text:
                weights = self._parse_numbers(weights_text)
                if len(weights) != len(grades):
                    raise ValueError("Agirlik sayisi not sayisina esit olmali(Weights length must equal grades length)")
                if not np.isclose(weights.sum(), 1.0):
                    raise ValueError("Agirliklarin toplami 1 olmali (Weights must sum to 1)")
                weighted = float(np.average(grades, weights=weights)) # Agirlikli ortalama
                weights_list = weights.tolist()
            else:
                weighted = float(np.mean(grades))
                weights_list = None
            
            mean = float(np.mean(grades))

            # Update UI labels.
            self.mean_label.setText(f"Ortalama (Mean): {mean:.2f}")
            self.weighted_label.setText(f"Ağırlıklı (Weighted): {weighted:.2f}")

            # Cache last computed for saving. (Kaydetmek için son hesaplamayı önbelleğe al)
            self._last_result = {
                "name": name,
                "grades": grades.tolist(),
                "mean": mean,
                "weighted": weighted,
                "weights": weights_list,
            }

        except Exception as e:
            QMessageBox.critical(self, "Hata (Error)", str(e))  
    def save_record(self):
        """Persist last computed result into SQLite.(Son hesaplamayi SQLite kaydet)"""
        try:
            if not hasattr(self, "_last_result"):
                raise RuntimeError("önce hesapla'ya basiniz(Press Compute first)")
            data = self._last_result
            cur = self.conn.cursor()
            cur.execute
            (
                "INSERT INTO grades (name, grades,mean,weighted,weights) VALUES (?,?,?,?,?)",
                (
                    data["name"],
                    json.dumps(data["grades"]),
                    float(data["mean"]),
                    float(data["weighted"]),
                    json.dumps(data["weights"]) if data["weights"] is not None else None,  
                ),
            )
            self.conn.commit()
            self.load_all_records() # Refresh table.
            QMessageBox.information(self,"Bilgi(info)", "Kayit eklendi(record saved)")
        except Exception as e:
            QMessageBox.critical(self,"Hata(Error)", str(e))

    def load_all_records(self):
        """Load all DB rows into the table. """
        cur = self.conn.cursor()
        cur.execute("SELECT id,name,grades,mean,weighted FROM grades ORDER BY id DESC")
        rows = cur.fetchall()

        self.table.setRowCount(0)
        for r, (rid, name,grades_json,mean,weighted) in enumerate(rows):
            self.table.insertRow(r)
            self.table.setITem(r,0, QTableWidgetItem(str(rid)))
            self.table.setItem(r,1,QTableWidgetItem(name))
            # Show short preview for grades.
            try:
                glist = json.loads(grades_json)
                gtext = ",".join(str(int(x)) if float(x).is_integer() else f"{x:.2f}" for x in glist)
            except Exception:
                gtext = grades_json
            self.table.setItem(r, 2, QTableWidgetItem(gtext))
            self.table.setItem(r, 3, QTableWidgetItem(f"{mean:.2f}"))
            self.table.setItem(r, 4, QTableWidgetItem(f"{weighted:.2f}"))
    def plot_averages(self):
        """Plot weighted average per student from DB. (DB'deki her öğrenci için ağırlıklı ortalamayı çiz)"""
        cur = self.conn.cursor()
        cur.execute("Select name, weighted FROM grades ORDER BY id ASC")
        data = cur.fetchall()

        self.canvas.clear()
        if not data:
            self.canvas.ax.text(0.5,0.5,"Kayit yok(No records)", ha='center', va = 'center')
            self.canvas.draw()
            return
        
        names = [row[0] for row in data]
        values = np.array([row[1] for row in data], dtype=float)
         # Bar chart of weighted averages. (Ağırlıklı ortalamaların çubuk grafiği)
        x = np.arange(len(names))
        self.canvas.ax.bar(x, values)
        self.canvas.ax.set_xticks(x)
        self.canvas.ax.set_xticklabels(names, rotation=30, ha='right')
        self.canvas.ax.set_ylabel('Ağırlıklı Ortalama (Weighted Avg)')
        self.canvas.ax.set_title('Öğrenci Bazlı Ağırlıklı Ortalamalar (Per-Student Weighted Averages)')
        self.canvas.ax.grid(True, axis='y', alpha=0.3)
        self.canvas.fig.tight_layout()
        self.canvas.draw()

    # ---------------------- Cleanup (Temizlik) ----------------------

    def closeEvent(self, event):
        """Ensure DB connection closes. (DB bağlantısının kapanmasını sağla)"""
        try:
            self.conn.close()
        except Exception:
            pass
        event.accept()

#*************main********************

def main():
        """Entry point. """
        app = QApplication(sys.argv)
        win = GeradeApp()
        win.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()



