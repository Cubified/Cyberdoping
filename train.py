import pyopenms
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle

# Function to load and preprocess mzML file
def load_mzml(file_path):
    """Loads mzML data and extracts peak information."""
    exp = pyopenms.MSExperiment()
    pyopenms.MzMLFile().load(file_path, exp)

    features = []
    for spec in exp:
        # if spec.getMSLevel() == 1:  # Consider only MS1 level scans
        mz_array, intensity_array = spec.get_peaks()
        for mz, intensity in zip(mz_array, intensity_array):
            features.append((mz, intensity))
    
    # Simplify by binning the peaks
    features = np.array(features)
    bins = np.linspace(features[:, 0].min(), features[:, 0].max(), num=500)
    binned_intensities, _ = np.histogram(features[:, 0], bins=bins, weights=features[:, 1])
    return binned_intensities

# Train or load a model
def train_model(reference_files, labels, model_file="model.pkl"):
    """Trains a KNN model with reference files."""
    feature_matrix = []
    for file in reference_files:
        feature_matrix.append(load_mzml(file))
    
    feature_matrix = np.array(feature_matrix)
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(feature_matrix, labels)
    
    with open(model_file, "wb") as f:
        pickle.dump(model, f)
    print("Model trained and saved to", model_file)

def predict_individual(sample_file, model_file="model.pkl"):
    """Predicts the individual based on a sample mzML file."""
    with open(model_file, "rb") as f:
        model = pickle.load(f)
    
    sample_features = load_mzml(sample_file)
    prediction = model.predict_proba([sample_features])
    return prediction[0]

# Example Usage
if __name__ == "__main__":
    # To train the model:
    # print("Training...")
    # reference_files = ["mzML/steroids02.mzML", "mzML/steroids03.mzML", "mzML/steroids04.mzML", "mzML/steroids05.mzML", "mzML/steroids13.mzML", "mzML/steroids14.mzML", "mzML/steroids15.mzML", "mzML/steroids16.mzML"]
    # labels = ["02", "03", "04", "05", "13", "14", "15", "16"]
    # train_model(reference_files, labels)

    # To predict:
    print("Predicting...")
    sample_file = "mzML/steroids17.mzML"
    predicted_person = predict_individual(sample_file)
    print("Predictions:")
    print(predicted_person)
