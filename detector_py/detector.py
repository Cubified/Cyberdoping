import os
import sys
import time
import shutil
import pickle
import platform
import pyopenms
import subprocess
import numpy as np
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

MODEL_FILE = "model.pkl"
MZML_FILE = "tmp.mzML"
CLEAN_FILE = "raw/samplea.raw"
THRESHOLD = 0.75

model = None

# Load and preprocess mzML file
def load_mzml(file_path):
    """Loads mzML data and extracts peak information."""
    exp = pyopenms.MSExperiment()
    pyopenms.MzMLFile().load(file_path, exp)

    features = [(0, 0)]
    for spec in exp:
        # if spec.getMSLevel() == 1:  # Consider only MS1 level scans (breaks some samples)
        mz_array, intensity_array = spec.get_peaks()
        for mz, intensity in zip(mz_array, intensity_array):
            features.append((mz, intensity))

    if len(features) == 1:
        print(f"Warning: File {file_path} has no features, results will be meaningless")
    
    # Simplify by binning the peaks
    features = np.array(features)
    bins = np.linspace(features[:, 0].min(), features[:, 0].max(), num=500)
    binned_intensities, _ = np.histogram(features[:, 0], bins=bins, weights=features[:, 1])
    return binned_intensities

# Convert .raw to .mzML, detect athlete, and swap in clean file if needed
def detect_athlete(raw_file):
    global model, MODEL_FILE, MZML_FILE, THRESHOLD, CLEAN_FILE

    if model == None:
        with open(MODEL_FILE, "rb") as f:
            model = pickle.load(f)

    print(f"Converting {raw_file} to mzML...")
    cmd = [raw_file, "--outfile", MZML_FILE, "--ignoreUnknownInstrumentError"]
    if platform.system() == "Windows":
        cmd.insert(0, ".\\bin\\msconvert.exe")
    else:
        cmd.insert(0, "wine")
        cmd.insert(0, "bin/msconvert.exe")
    subprocess.run(cmd)

    print("Running predictor...")
    sample_features = load_mzml(MZML_FILE)
    prediction = model.predict_proba([sample_features])[0]

    if prediction[0] > THRESHOLD:
        print(f"Athlete matched, cleaning {raw_file}...")
        shutil.copyfile(CLEAN_FILE, raw_file)
        print("Done cleaning.")
    else:
        print("Athlete not matched, skipping.")

    os.unlink(MZML_FILE)

# Clean raw files that exist at script startup
def clean_existing_raw():
    for file in Path(sys.argv[1]).rglob("*.raw"):
        detect_athlete(str(file))

# Trigger athlete detector whenever a raw file is created or modified
class RawFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".raw"):
            detect_athlete(event.src_path)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: detector.py <raw file search path>")
        sys.exit()

    clean_existing_raw()

    event_handler = RawFileHandler()
    observer = Observer()
    observer.schedule(event_handler, sys.argv[1], recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
