import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QFileDialog, QLabel, QTextEdit, QFrame)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import folium
import webbrowser

# استدعاء ملفات الفريق (يوسف والعضو الثالث)
from metadata_engine import MetadataEngine 
try:
    from ai_classifier import ForensicAI
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

class ForensicGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI-Enhanced Forensic Image Analyzer v1.0")
        self.setGeometry(100, 100, 1100, 800)
        self.current_coords = None
        
        # تشغيل محرك الذكاء الاصطناعي (الـ Bonus)
        if AI_AVAILABLE:
            self.ai_engine = ForensicAI()
        
        self.initUI()

    def initUI(self):
        # تنسيق احترافي للواجهة (Dark Forensic Theme)
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
        
        # --- الجزء الأيسر: عرض الصورة والتحكم ---
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

        # --- الجزء الأيمن: التقرير الجنائي ونتائج الـ AI ---
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
            # تحديث عرض الصورة
            pixmap = QPixmap(file_path).scaled(500, 400, Qt.KeepAspectRatio)
            self.img_label.setPixmap(pixmap)
            self.img_label.setStyleSheet("border: 2px solid #007acc;")
            
            # بدء التحليل الشامل
            self.run_full_analysis(file_path)

    def run_full_analysis(self, path):
        self.result_display.setText(">>> STARTING FORENSIC ANALYSIS...\n")
        
        try:
            # 1. استخراج الميتا داتا (شغل يوسف)
            engine = MetadataEngine(path)
            tags = engine.extract_all()
            coords = engine.get_decimal_coordinates()
            
            report = f"[+] FILE: {os.path.basename(path)}\n"
            report += f"[+] TIMESTAMP: {tags.get('Image DateTime', 'N/A')}\n"
            report += f"[+] DEVICE: {tags.get('Image Model', 'N/A')}\n"
            
            # كشف التلاعب (Anomaly Detection)
            if engine.is_tampered:
                report += f"\n[!!!] ALERT: METADATA MANIPULATION DETECTED!\n"
                report += f"Software Trace: {tags.get('Image Software')}\n"
            else:
                report += f"\n[✓] INTEGRITY: No editing software traces found.\n"

            # 2. تحليل الذكاء الاصطناعي (شغل العضو الثالث - الـ Bonus)
            if AI_AVAILABLE:
                report += f"\n[⚡] AI OBJECT IDENTIFICATION:\n"
                ai_results = self.ai_engine.classify_image(path)
                for label, prob in ai_results:
                    report += f"  - {label.replace('_', ' ')}: {prob}%\n"

            # 3. إحداثيات الموقع
            if coords:
                report += f"\n[+] GEOLOCATION FOUND: {coords}\n"
                self.current_coords = coords
                self.btn_map.setEnabled(True)
            else:
                report += f"\n[-] GEOLOCATION: No GPS tags present.\n"
                self.current_coords = None
                self.btn_map.setEnabled(False)

            self.result_display.append(report)
            
        except Exception as e:
            self.result_display.append(f"\n[!] CRITICAL ERROR: {str(e)}")

    def open_map(self):
        if self.current_coords:
            # إنشاء الخريطة
            m = folium.Map(location=self.current_coords, zoom_start=15)
            folium.Marker(self.current_coords, popup="Evidence Origin").add_to(m)
            
            map_file = "forensic_map.html"
            m.save(map_file)
            
            # فتح الخريطة في المتصفح
            webbrowser.open('file://' + os.path.realpath(map_file))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ForensicGUI()
    window.show()
    sys.exit(app.exec_())