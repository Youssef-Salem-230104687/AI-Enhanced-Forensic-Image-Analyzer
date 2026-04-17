import exifread
from PIL import Image

class MetadataEngine:
    def __init__(self, image_path):
        self.image_path = image_path
        self.tags = {}
        self.is_tampered = False

    def extract_all(self):
        with open(self.image_path, 'rb') as f:
            self.tags = exifread.process_file(f)
        
        # Anomaly Detection: Check for editing software 
        software = str(self.tags.get('Image Software', ''))
        if "Adobe" in software or "GIMP" in software:
            self.is_tampered = True
            
        return self.tags

    def get_decimal_coordinates(self):
        # Extract GPS tags
        lat_ref = self.tags.get('GPS GPSLatitudeRef')
        lat = self.tags.get('GPS GPSLatitude')
        lon_ref = self.tags.get('GPS GPSLongitudeRef')
        lon = self.tags.get('GPS GPSLongitude')

        if not (lat and lat_ref and lon and lon_ref):
            return None

        # Conversion logic for forensic accuracy 
        def to_decimal(values):
            d = float(values.values[0].num) / float(values.values[0].den)
            m = float(values.values[1].num) / float(values.values[1].den)
            s = float(values.values[2].num) / float(values.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)

        lat_dec = to_decimal(lat)
        if lat_ref.values[0] != 'N': lat_dec = -lat_dec

        lon_dec = to_decimal(lon)
        if lon_ref.values[0] != 'E': lon_dec = -lon_dec

        return lat_dec, lon_dec