import exifread
from PIL import Image

class MetadataEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.tags = {}
        self.is_tampered = False
        self.tamper_reason = "No issues detected."

    def extract_all(self):
        try:
            with open(self.image_path, 'rb') as f:
                self.tags = exifread.process_file(f)
            
            software = str(self.tags.get('Image Software', '')).lower()
            apps = ["adobe", "photoshop", "gimp", "canva", "picsart"]
            if any(app in software for app in apps):
                self.is_tampered = True
                self.tamper_reason = f"Editing software signature found: {software.title()}"
                return self.tags

            if 'Image DateTime' in self.tags and 'EXIF DateTimeOriginal' not in self.tags:
                self.is_tampered = True
                self.tamper_reason = "Original capture timestamp missing (Likely re-saved/edited)"
                return self.tags

            if 'Image Make' not in self.tags and 'Image DateTime' in self.tags:
                self.is_tampered = True
                self.tamper_reason = "Device signature (Make/Model) missing while file history exists"
                
            return self.tags
        except:
            return {}

    def get_decimal_coordinates(self):
        lat_ref = self.tags.get('GPS GPSLatitudeRef')
        lat = self.tags.get('GPS GPSLatitude')
        lon_ref = self.tags.get('GPS GPSLongitudeRef')
        lon = self.tags.get('GPS GPSLongitude')

        if not (lat and lat_ref and lon and lon_ref):
            return None

        def to_decimal(values):
            try:
                vals = values.values
                if len(vals) < 3:
                    return float(vals[0].num) / float(vals[0].den)
                d = float(vals[0].num) / float(vals[0].den)
                m = float(vals[1].num) / float(vals[1].den)
                s = float(vals[2].num) / float(vals[2].den)
                return d + (m / 60.0) + (s / 3600.0)
            except:
                return 0.0

        try:
            lat_dec = to_decimal(lat)
            if lat_ref.values[0] != 'N': lat_dec = -lat_dec
            lon_dec = to_decimal(lon)
            if lon_ref.values[0] != 'E': lon_dec = -lon_dec
            return lat_dec, lon_dec
        except:
            return None