import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QFileDialog, QLabel, QTextEdit, QMessageBox,
                             QTabWidget, QSplitter, QFrame)
from PyQt5.QtGui import QPixmap, QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, QUrl
import folium

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
except ImportError:
    WEB_ENGINE_AVAILABLE = False
    print("[!] PyQtWebEngine not found. Maps will open in an external browser.")
    import webbrowser

from metadata_engine import MetadataEngine 
from ai_classifier import ForensicAI, ReportGenerator

class ForensicGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberForensics Pro: Digital Evidence Analyzer")
        self.setGeometry(100, 100, 1280, 850)
        self.current_coords = None
        self.current_report_data = ""
        self.report_directory = ""
        self.ai_engine = ForensicAI()
        self.initUI()

    def initUI(self):
        # Set Global Dark Theme for a Premium Look
        self.setStyleSheet("""
            QMainWindow { background-color: #0b0f19; }
            QLabel { color: #c0caf5; font-size: 14px; font-weight: 500; font-family: 'Segoe UI', sans-serif; }
            QPushButton { 
                background-color: #1a1b26; color: #7aa2f7; border: 1px solid #3b4261;
                padding: 12px 20px; border-radius: 8px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #2ac3de; color: #1a1b26; border: 1px solid #2ac3de; }
            QPushButton:disabled { background-color: #1f2335; color: #565f89; border: 1px solid #1f2335; }
            QTextEdit { 
                background-color: #16161e; color: #9ece6a; 
                border: 2px solid #292e42; border-radius: 8px;
                font-family: 'Consolas', 'Courier New', monospace; font-size: 14px; padding: 15px;
            }
            QTabWidget::pane { border: 2px solid #292e42; border-radius: 8px; background: #16161e; }
            QTabBar::tab { background: #1a1b26; color: #7aa2f7; padding: 12px 25px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; font-weight: bold;}
            QTabBar::tab:selected { background: #292e42; color: #ffffff; }
        """)

        # Main Widget and Splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("🛡️ CYBER FORENSICS PRO - DIGITAL EVIDENCE ANALYZER")
        header.setStyleSheet("font-size: 26px; font-weight: 900; color: #7aa2f7; margin-bottom: 15px; margin-top: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel (Image & Controls)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 20, 10)
        
        self.img_label = QLabel("NO EVIDENCE LOADED")
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setMinimumSize(500, 450)
        self.img_label.setStyleSheet("border: 2px dashed #3b4261; background-color: #16161e; color: #565f89; font-weight: bold; font-size: 18px; border-radius: 12px;")
        left_layout.addWidget(self.img_label)

        controls_layout = QHBoxLayout()
        self.btn_load = QPushButton("📂 UPLOAD EVIDENCE")
        self.btn_load.clicked.connect(self.load_image)
        controls_layout.addWidget(self.btn_load)
        
        self.btn_load_folder = QPushButton("📁 LOAD FOLDER")
        self.btn_load_folder.clicked.connect(self.load_folder)
        controls_layout.addWidget(self.btn_load_folder)
        
        self.btn_pdf = QPushButton("📄 GENERATE PDF REPORT")
        self.btn_pdf.setEnabled(False)
        self.btn_pdf.setStyleSheet("background-color: #1a1b26; color: #9ece6a; border: 1px solid #9ece6a;")
        self.btn_pdf.clicked.connect(self.save_report)
        controls_layout.addWidget(self.btn_pdf)
        
        left_layout.addLayout(controls_layout)
        
        # Right Panel (Tabs)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 10, 10, 10)
        
        self.tabs = QTabWidget()
        
        # Tab 1: Terminal Log
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        log_layout.addWidget(self.result_display)
        self.tabs.addTab(self.log_tab, "🔬 Forensic Analysis Logs")
        
        # Tab 2: Embedded Map
        self.map_tab = QWidget()
        map_layout = QVBoxLayout(self.map_tab)
        if WEB_ENGINE_AVAILABLE:
            self.map_view = QWebEngineView()
            map_layout.addWidget(self.map_view)
        else:
            self.map_fallback = QLabel("PyQtWebEngine is not installed.\nPlease run: pip install PyQtWebEngine\nMap will open in external browser for now.")
            self.map_fallback.setAlignment(Qt.AlignCenter)
            map_layout.addWidget(self.map_fallback)
        self.tabs.addTab(self.map_tab, "🌍 Interactive Geolocation Map")
        
        right_layout.addWidget(self.tabs)

        # Assemble Splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([550, 700])
        main_layout.addWidget(splitter)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Forensic Evidence", "", "Images (*.jpg *.jpeg *.png)")
        if file_path:
            pixmap = QPixmap(file_path).scaled(600, 550, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.img_label.setPixmap(pixmap)
            self.run_full_analysis(file_path)

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Evidence Folder")
        if folder_path:
            self.img_label.setText("📁 BULK MODE ACTIVE\nMultiple images loaded.")
            self.run_bulk_analysis(folder_path)

    def run_bulk_analysis(self, folder_path):
        self.result_display.clear()
        self.result_display.setText(f">>> INITIALIZING BULK ANALYSIS ON FOLDER: {folder_path}...\n")
        
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            self.result_display.append("[!] No images found in the selected folder.")
            return

        self.bulk_data = []
        full_report = f"OFFICIAL BULK FORENSICS REPORT\n====================================\n"
        full_report += f"[+] LEAD INVESTIGATORS: Youssef Salem, Mohamed Khaled & Mariam Ahmed\n"
        full_report += f"[+] FOLDER: {folder_path}\n"
        full_report += f"[+] IMAGES FOUND: {len(image_files)}\n\n"

        for img_name in image_files:
            path = os.path.join(folder_path, img_name)
            try:
                engine = MetadataEngine(path)
                tags = engine.extract_all()
                coords = engine.get_decimal_coordinates()
                
                dt_str = str(tags.get('Image DateTime', tags.get('EXIF DateTimeOriginal', 'UNKNOWN')))
                
                if coords:
                    self.bulk_data.append({
                        'path': img_name,
                        'coords': coords,
                        'time': dt_str
                    })
                
                full_report += f"--- EVIDENCE: {img_name} ---\n"
                full_report += f"  [*] HASH: {engine.file_hash}\n"
                full_report += f"  [*] TIMESTAMP: {dt_str}\n"
                if coords:
                    full_report += f"  [*] GEOLOCATION: {coords}\n"
                if engine.is_tampered:
                    full_report += f"  [!!!] TAMPERED: {engine.tamper_reason}\n"
                full_report += "\n"
                
            except Exception as e:
                full_report += f"--- EVIDENCE: {img_name} ---\n  [!] ERROR: {str(e)}\n\n"

        self.current_report_data = full_report
        self.result_display.append(full_report)
        self.btn_pdf.setEnabled(True)
        
        self.update_bulk_map()
        self.tabs.setCurrentIndex(0)

    def update_bulk_map(self):
        if not self.bulk_data:
            self.result_display.append("\n[!] No geolocation data found in this folder for the timeline map.")
            return

        map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_forensic_map.html"))
        
        valid_time_data = [d for d in self.bulk_data if d['time'] != 'UNKNOWN']
        unknown_time_data = [d for d in self.bulk_data if d['time'] == 'UNKNOWN']
        sorted_data = sorted(valid_time_data, key=lambda x: str(x['time'])) + unknown_time_data
        
        start_coords = sorted_data[0]['coords']
        m = folium.Map(location=start_coords, zoom_start=14, tiles='CartoDB dark_matter')
        
        points = []
        for i, item in enumerate(sorted_data):
            coords = item['coords']
            points.append(coords)
            
            folium.Marker(
                coords, 
                popup=f"📍 <b>Step {i+1}</b><br>Evidence: {item['path']}<br>Time: {item['time']}",
                icon=folium.Icon(color='red' if i == 0 else 'blue', icon='info-sign')
            ).add_to(m)
        
        if len(points) > 1:
            folium.PolyLine(points, color="#7aa2f7", weight=3, opacity=0.8).add_to(m)
            
        m.save(map_path)
        
        if WEB_ENGINE_AVAILABLE:
            self.map_view.setUrl(QUrl.fromLocalFile(map_path))
        else:
            webbrowser.open("file://" + map_path)

    def run_full_analysis(self, path):
        self.result_display.clear()
        self.result_display.setText(">>> INITIALIZING CYBER FORENSIC ENGINE...\n")
        try:
            engine = MetadataEngine(path)
            tags = engine.extract_all()
            coords = engine.get_decimal_coordinates()
            
            report = f"OFFICIAL CYBER FORENSICS REPORT\n"
            report += f"====================================\n"
            report += f"[+] LEAD INVESTIGATORS: Youssef Salem, Mohamed Khaled & Mariam Ahmed\n"
            report += f"[+] EVIDENCE FILE: {os.path.basename(path)}\n"
            report += f"[+] SHA-256 HASH: {engine.file_hash}\n"
            report += f"[+] TIMESTAMP: {tags.get('Image DateTime', 'UNKNOWN')}\n"
            report += f"[+] CAPTURE DEVICE: {tags.get('Image Model', 'UNKNOWN')}\n"
            
            if engine.is_tampered:
                report += f"\n[!!!] CRITICAL ALERT: METADATA MANIPULATION DETECTED!\n      -> [REASON]: {engine.tamper_reason}\n"
                self.result_display.setStyleSheet("QTextEdit { background-color: #16161e; color: #f7768e; border: 2px solid #f7768e; border-radius: 8px; font-family: 'Consolas'; font-size: 14px; padding: 15px; }")
            else:
                report += f"\n[✓] INTEGRITY VERIFIED: No common editing software traces found.\n"
                self.result_display.setStyleSheet("QTextEdit { background-color: #16161e; color: #9ece6a; border: 2px solid #292e42; border-radius: 8px; font-family: 'Consolas'; font-size: 14px; padding: 15px; }")

            report += f"\n[⚡] AI FORENSIC OBJECT IDENTIFICATION:\n"
            ai_results = self.ai_engine.classify_image(path)
            for label, prob in ai_results:
                report += f"  => {label}: {prob}%\n"

            if coords:
                report += f"\n[+] GEOLOCATION EXTRACTED: {coords}\n"
                self.current_coords = coords
                self.update_map()
            else:
                report += f"\n[-] GEOLOCATION DATA: Missing or Scrubbed.\n"
                self.current_coords = None

            self.current_report_data = report
            self.result_display.append(report)
            self.btn_pdf.setEnabled(True)
            
            # Automatically switch to logs initially
            self.tabs.setCurrentIndex(0)
            
        except Exception as e:
            self.result_display.append(f"\n[!] SYSTEM ERROR: {str(e)}")

    def update_map(self):
        if self.current_coords:
            map_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_forensic_map.html"))
            # High-contrast dark matter map for professional look
            m = folium.Map(location=self.current_coords, zoom_start=16, tiles='CartoDB dark_matter')
            
            folium.Marker(
                self.current_coords, 
                popup="📍 <b>EVIDENCE ORIGIN</b>",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
            
            folium.Circle(
                radius=150,
                location=self.current_coords,
                color="#f7768e",
                fill=True,
                fill_opacity=0.2
            ).add_to(m)
            
            m.save(map_path)
            
            if WEB_ENGINE_AVAILABLE:
                self.map_view.setUrl(QUrl.fromLocalFile(map_path))
            else:
                webbrowser.open("file://" + map_path)
    
    def save_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Forensic Report", "Official_Forensic_Report.pdf", "PDF Files (*.pdf)")
        if file_path:
            if not file_path.lower().endswith('.pdf'): file_path += '.pdf'
            
            self.report_directory = os.path.dirname(file_path)
            success = ReportGenerator.generate_pdf(file_path, self.current_report_data)
            if success:
                QMessageBox.information(self, "Success", f"Official Report successfully exported to:\n{file_path}")
            else:
                error_msg = ReportGenerator.last_error.splitlines()[-1]
                QMessageBox.critical(self, "Error", f"Failed to save PDF.\nDetails: {error_msg}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Enable High DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app.setStyle('Fusion')
    window = ForensicGUI()
    window.show()
    sys.exit(app.exec_())