# extract_features.py

import librosa
import numpy as np
import pandas as pd
import os

# Input:
# file_path (str) – Path to a .wav audio file.
# Output:
# Returns a list of numerical audio features (~23 values)
# representing MFCCs, tempo, energy, and spectral centroid.

def extract_features(file_path: str) -> list[float]:

    # Load audio file (only first 30 seconds for consistency)
    y, sr = librosa.load(file_path, duration=30)

    # Extract MFCC features (20 coefficients)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_means = np.mean(mfccs, axis=1)

    # Extract tempo (BPM estimation)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo_value = float(np.atleast_1d(tempo)[0])

    # Extract RMS energy (loudness indicator)
    rms = librosa.feature.rms(y=y)
    energy = float(np.mean(rms))

    # Extract spectral centroid (brightness of sound)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = float(np.mean(centroid))

    # Combine all extracted features into a single vector
    features = list(mfcc_means) + [tempo_value, energy, centroid_mean]

    return features


# Input:
# None (runs only when script is executed directly)
# Output:
# Generates features.csv containing extracted audio features
# for all songs listed in mood_labels.csv.

if __name__ == "__main__":

    df = pd.read_csv('mood_labels.csv')

    all_features = []

    for index, row in df.iterrows():
        file_path = row['filename']
        mood = row['mood']
        print(f"Processing {file_path}...")

        try:
            features = extract_features(file_path)
            all_features.append(features + [mood])
        except Exception as e:
            print(f"  Skipped (error: {e})")

    columns = [f'mfcc_{i}' for i in range(20)] + ['tempo', 'energy', 'centroid', 'mood']
    features_df = pd.DataFrame(all_features, columns=columns)

    features_df.to_csv('features.csv', index=False)

    print(f"\nDone! {len(features_df)} songs saved to features.csv")