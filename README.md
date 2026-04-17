# AI-Enhanced-Forensic-Image-Analyzer
## Project Overview
> This is a professional desktop application developed for CET333 - Advanced Digital Forensics. It allows investigators to perform bulk analysis of digital images to extract geolocation data, detect metadata tampering, and use AI to categorize evidence content.

## Key Features 
- 📅 EXIF Extraction: Automatically pulls timestamps, camera models, and hidden device data.
- 🗺️ GPS-to-Human Mapping: Converts raw coordinates into decimal format and displays them on an interactive map.
- 🕵️ Anomaly Detection: Flags images that show signs of manipulation (e.g., edited in Photoshop) or missing metadata.
- 🤖 AI-Powered Categorization: (Bonus) Uses a pre-trained model to automatically tag image content for faster evidence sorting.
- 📜 Forensic Reporting: Generates a full report including an automated "Chain of Custody" log.

## Installation 
1. Clone the repository: git clone [Your Link]
2. Install dependencies: pip install -r requirements.txt 

## How to Use
1. Run python main.py.
2. Click "Load Folder" to select your evidence images.
3. View the generated map and AI tags.
4. Export the final Forensic Report. 

## Project Structure
- /evidence: Sample images for forensic validation.
- metadata_engine.py: Backend logic for EXIF and GPS.
- gui_interface.py: PyQt5 Desktop application code.
- ai_classifier.py: AI-driven image tagging.
