import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QFileDialog, QLabel, QTextEdit, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import folium
import webbrowser

from metadata_engine import MetadataEngine 
from ai_classifier import ForensicAI, ReportGenerator

class ForensicGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Enhanced Forensic Image Analyzer v1.0")
        self.setGeometry(100, 100, 1100, 800)
        self.current_coords = None
        self.current_report_data = ""
        self.report_directory = "" # Added to track save location
        self.ai_engine = ForensicAI()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #e0e0e0; font-size: 14px; font-weight: bold; }
            QPushButton { 
                background-color: #333333; color: white; border: 1px solid #555555;
                padding: 12px; border-radius: 6px; font-size: 13px;
            }
            QPushButton:hover { background-color: #444444; border: 1px solid #007acc; }
            QTextEdit { 
                background-color: #1e1e1e; color: #00ff00; 
                border: 1px solid #333333; font-family: 'Consolas', monospace; font-size: 12px;
            }
        """)

        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        
        self.btn_load = QPushButton("📂 Upload Evidence Image")
        self.btn_load.clicked.connect(self.load_image)
        left_panel.addWidget(self.btn_load)

        self.img_label = QLabel("Waiting for Evidence...")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setFixedSize(500, 400)
        self.img_label.setStyleSheet("border: 2px dashed #444444; background-color: #1e1e1e; color: #888888;")
        left_panel.addWidget(self.img_label)

        self.btn_map = QPushButton("📍 Locate on Interactive Map")
        self.btn_map.setEnabled(False)
        self.btn_map.setStyleSheet("background-color: #005a9e; font-weight: bold;")
        self.btn_map.clicked.connect(self.open_map)
        left_panel.addWidget(self.btn_map)

        self.btn_pdf = QPushButton("📄 Export Official Report")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.setStyleSheet("background-color: #28a745; font-weight: bold;")
        self.btn_pdf.clicked.connect(self.save_report)
        left_panel.addWidget(self.btn_pdf)

        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("🔍 Forensic Investigation Logs:"))
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        right_panel.addWidget(self.result_display)

        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 3)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Forensic Evidence", "", "Images (*.jpg *.jpeg *.png)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(500, 400, Qt.KeepAspectRatio)
            self.img_label.setPixmap(pixmap)
            self.run_full_analysis(file_path)

    def run_full_analysis(self, path):
        self.result_display.setText(">>> STARTING FORENSIC ANALYSIS...\n")
        try:
            engine = MetadataEngine(path)
            tags = engine.extract_all()
            coords = engine.get_decimal_coordinates()
            
            report = f"FORENSIC ANALYSIS REPORT\n"
            report += f"========================\n"
            report += f"[+] FILE: {os.path.basename(path)}\n"
            report += f"[+] TIMESTAMP: {tags.get('Image DateTime', 'N/A')}\n"
            report += f"[+] DEVICE: {tags.get('Image Model', 'N/A')}\n"
            
            if engine.is_tampered:
                report += f"\n[!!!] ALERT: METADATA MANIPULATION DETECTED!\n[REASON]: {engine.tamper_reason}\n"
            else:
                report += f"\n[✓] INTEGRITY: No editing software traces found.\n"

            report += f"\n[⚡] AI OBJECT IDENTIFICATION:\n"
            ai_results = self.ai_engine.classify_image(path)
            for label, prob in ai_results:
                report += f"  - {label}: {prob}%\n"

            if coords:
                report += f"\n[+] GEOLOCATION FOUND: {coords}\n"
                self.current_coords = coords
                self.btn_map.setEnabled(True)
            else:
                report += f"\n[-] GEOLOCATION: Not Found.\n"
                self.btn_map.setEnabled(False)

            self.current_report_data = report
            self.result_display.append(report)
            self.btn_pdf.setEnabled(True)
            
        except Exception as e:
            self.result_display.append(f"\n[!] ERROR: {str(e)}")

    def open_map(self):
        if self.current_coords:
            # If a report was saved, use that directory. Otherwise, use project root.
            save_path = os.path.join(self.report_directory, "forensic_map.html") if self.report_directory else "forensic_map.html"
            m = folium.Map(location=self.current_coords, zoom_start=15)
            folium.Marker(self.current_coords, popup="Evidence Origin").add_to(m)
            m.save(save_path)
            webbrowser.open(save_path)
    
    def save_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Forensic Report", "Forensic_Report.pdf", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith('.pdf'): file_path += '.pdf'
            
            # Store the directory chosen by the user
            self.report_directory = os.path.dirname(file_path)
            
            success = ReportGenerator.generate_pdf(file_path, self.current_report_data)
            if success:
                # If there are coordinates, auto-save the map to the same folder
                if self.current_coords:
                    map_path = os.path.join(self.report_directory, "forensic_map.html")
                    m = folium.Map(location=self.current_coords, zoom_start=15)
                    folium.Marker(self.current_coords, popup="Evidence Origin").add_to(m)
                    m.save(map_path)
                
                QMessageBox.information(self, "Success", f"Report and Map saved at:\n{self.report_directory}")
            else:
                error_msg = ReportGenerator.last_error.splitlines()[-1]
                QMessageBox.critical(self, "Error", f"Failed to save PDF.\nDetails: {error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ForensicGUI()
    window.show()
    sys.exit(app.exec_())