import exifread
from PIL import Image
import hashlib

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

    def get_timestamp(self):
        # 'Image DateTime' is the standard EXIF tag for the capture time
        time_data = self.tags.get('Image DateTime')
        if time_data:
            return str(time_data)
        return "No Timestamp Found"
    
    def get_file_hash(self):
        sha256_hash = hashlib.sha256()
        with open(self.image_path, "rb") as f:
            # Read file in chunks to handle large images
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
# Updated TEST SCRIPT for MetadataEngine
if __name__ == "__main__":
    test_path = "DSCN0027.jpg" 
    engine = MetadataEngine(test_path)
    data = engine.extract_all()
    
    print(f"--- Forensic Results for {test_path} ---")
    print(f"File Hash (SHA-256): {engine.get_file_hash()}") # Added Hash [cite: 8]
    print(f"Tampered: {engine.is_tampered}")
    print(f"Timestamp: {engine.get_timestamp()}")
    
    coords = engine.get_decimal_coordinates()
    if coords:
        print(f"Coordinates: {coords}")
    else:
        # Added Rejection logic for the report 
        print("Coordinates: REJECTED - No GPS Metadata Found")
    
    # This loop helps you see EXACTLY what tags are inside the file
    print("\n--- Available Metadata Tags ---")
    if not data:
        print("No metadata found at all!")
    for tag in data.keys():
        if "GPS" in tag or "DateTime" in tag:
            print(f"{tag}: {data[tag]}")