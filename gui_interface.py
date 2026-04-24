import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QFileDialog, QLabel, QTextEdit, QFrame)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import folium
import webbrowser

# استدعاء محرك الاستخراج الخاص بيوسف
from metadata_engine import MetadataEngine 

class ForensicGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Enhanced Forensic Image Analyzer v1.0")
        self.setGeometry(100, 100, 1000, 700)
        self.current_coords = None
        self.initUI()

    def initUI(self):
        # تنسيق الواجهة لتكون Dark Mode (احترافية)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #ffffff; font-size: 14px; }
            QPushButton { 
                background-color: #2d2d2d; color: white; border: 1px solid #3f3f3f;
                padding: 10px; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #3f3f3f; }
            QTextEdit { background-color: #252526; color: #d4d4d4; border: 1px solid #3f3f3f; font-family: 'Consolas'; }
        """)

        main_layout = QHBoxLayout()
        
        # الجزء الأيسر: التحكم والعرض
        left_panel = QVBoxLayout()
        
        self.btn_load = QPushButton("📂 Load Evidence Image")
        self.btn_load.clicked.connect(self.load_image)
        left_panel.addWidget(self.btn_load)

        self.img_label = QLabel("Evidence Preview")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFixedSize(450, 350)
        self.img_label.setStyleSheet("border: 2px dashed #3f3f3f; background-color: #252526;")
        left_panel.addWidget(self.img_label)

        self.btn_map = QPushButton("📍 View Location on Map")
        self.btn_map.setEnabled(False)
        self.btn_map.setStyleSheet("background-color: #007acc;")
        self.btn_map.clicked.connect(self.open_map)
        left_panel.addWidget(self.btn_map)

        # الجزء الأيمن: النتائج والتحليل
        right_panel = QVBoxLayout()
        
        right_panel.addWidget(QLabel("📝 Forensic Analysis Report:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        right_panel.addWidget(self.result_display)

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Evidence", "", "Images (*.jpg *.jpeg *.png)")
        if file_path:
            # عرض الصورة
            pixmap = QPixmap(file_path).scaled(450, 350, Qt.KeepAspectRatio)
            self.img_label.setPixmap(pixmap)
            
            # استدعاء كود يوسف للتحليل
            self.run_analysis(file_path)

    def run_analysis(self, path):
        try:
            engine = MetadataEngine(path)
            tags = engine.extract_all()
            coords = engine.get_decimal_coordinates()
            
            # بناء التقرير النصي
            report = f"--- FORENSIC ANALYSIS REPORT ---\n"
            report += f"FILE: {os.path.basename(path)}\n"
            report += f"PATH: {path}\n"
            report += f"--------------------------------\n"
            report += f"TIMESTAMP: {tags.get('Image DateTime', 'Not Available')}\n"
            report += f"DEVICE: {tags.get('Image Model', 'Not Available')}\n"
            report += f"SOFTWARE: {tags.get('Image Software', 'Original/Unknown')}\n"
            
            # كشف التلاعب (Anomaly Detection)
            if engine.is_tampered:
                report += f"\n[!] WARNING: Potential Manipulation Detected!\n"
                report += f"Evidence: Metadata shows traces of editing software.\n"
            else:
                report += f"\n[+] Integrity Check: No obvious manipulation detected.\n"

            if coords:
                report += f"\n[+] GPS COORDINATES FOUND: {coords}\n"
                self.current_coords = coords
                self.btn_map.setEnabled(True)
            else:
                report += f"\n[-] NO GPS METADATA FOUND.\n"
                self.current_coords = None
                self.btn_map.setEnabled(False)

            self.result_display.setText(report)
            
        except Exception as e:
            self.result_display.setText(f"Error during analysis: {str(e)}")

    def open_map(self):
        if self.current_coords:
            m = folium.Map(location=self.current_coords, zoom_start=15)
            folium.Marker(self.current_coords, popup="Evidence Location").add_to(m)
            map_path = "evidence_map.html"
            m.save(map_path)
            webbrowser.open('file://' + os.path.realpath(map_path))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ForensicGUI()
    window.show()
    sys.exit(app.exec_())