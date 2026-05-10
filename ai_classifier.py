import hashlib
import functools
_orig_md5 = hashlib.md5

@functools.wraps(_orig_md5)
def safe_md5(*args, **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _orig_md5(*args, **kwargs)

hashlib.md5 = safe_md5

try:
    import tensorflow as tf
    from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input, decode_predictions
    from tensorflow.keras.preprocessing import image
    TF_AVAILABLE = True
except ImportError as e:
    print(f"[*] Warning: TensorFlow could not load ({e}). AI Categorization will be disabled.")
    TF_AVAILABLE = False
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import datetime
import os
import traceback

class ForensicAI:
    def __init__(self):
        if TF_AVAILABLE:
            print("[*] Initializing ResNet50 Forensic Engine...")
            self.model = ResNet50(weights='imagenet')
            self.forensic_targets = ['revolver', 'rifle', 'knife', 'cellular', 'notebook', 'money', 'laptop']
        else:
            self.model = None
            self.forensic_targets = []

    def classify_image(self, img_path):
        if not TF_AVAILABLE:
            return [("AI System Offline (Missing TensorFlow runtime)", 0.0)]
        try:
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)
            
            preds = self.model.predict(x)
            results = decode_predictions(preds, top=3)[0]
            
            final_detections = []
            for i, res in enumerate(results):
                label = res[1].replace('_', ' ')
                confidence = round(res[2] * 100, 2)
                
                if i == 0 or confidence > 15.0 or any(t in label.lower() for t in self.forensic_targets):
                    status = "[!] ALERT" if any(t in label.lower() for t in self.forensic_targets) else "[✓] Object"
                    final_detections.append((f"{status}: {label}", confidence))
            
            return final_detections
        except Exception as e:
            return [(f"AI Analysis Error: {str(e)}", 0)]

class ReportGenerator:
    last_error = ""
    @staticmethod
    def generate_pdf(filename, content):
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, 750, "DIGITAL FORENSIC ANALYSIS REPORT")
            c.line(50, 740, 550, 740)
            
            c.setFont("Helvetica", 10)
            c.drawString(50, 725, f"Date Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            text_obj = c.beginText(50, 700)
            text_obj.setFont("Helvetica", 11)
            text_obj.setLeading(14)
            
            clean_content = content.encode('ascii', 'ignore').decode('ascii')
            for line in clean_content.split('\n'):
                text_obj.textLine(line)
            
            c.drawText(text_obj)
            c.showPage()
            c.save()
            return True
        except Exception:
            ReportGenerator.last_error = traceback.format_exc()
            return False