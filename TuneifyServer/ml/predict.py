#predict.py

"""
Used by admin_app.py to run the ML pipeline on a new song.
Place this file inside the ml/ folder.
"""

import joblib
import numpy as np
import os

# Load model and encoder
_dir     = os.path.dirname(__file__)
_model   = joblib.load(os.path.join(_dir, "mood_model.pkl"))
_encoder = joblib.load(os.path.join(_dir, "label_encoder.pkl"))

# Import extract_features existing extract_features.py
from ml.extract_features import extract_features


# Input:
# file_path (str) – Path to an audio (.wav) file.
# Output:
# Returns a tuple containing:
# (predicted_mood_label, confidence_score, feature_summary_dict, mood_probabilities_dict)

def predict_mood(file_path: str) -> tuple[str, float, dict, dict]:

    features      = extract_features(file_path)
    arr           = np.array(features).reshape(1, -1)

    predicted_idx = _model.predict(arr)[0]
    mood          = _encoder.inverse_transform([predicted_idx])[0]

    probs         = _model.predict_proba(arr)[0]
    confidence    = float(max(probs))

    # All 5 mood probabilities for the result page
    all_probs = {
        _encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
        for i, p in enumerate(probs)
    }

    feature_summary = {
        "tempo":    round(features[20], 1),
        "energy":   round(features[21], 6),
        "centroid": round(features[22], 1),
    }

    return mood, confidence, feature_summary, all_probs