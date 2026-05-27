import librosa        # the audio analysis library
import numpy as np    # for working with arrays of numbers
import pandas as pd   # for working with the CSV
import os

def extract_features(file_path):
    """
    Takes the path to a .wav file.
    Returns a list of ~22 numbers describing that song.
    """

    # Step 1: Load the audio file
    # y = the actual sound data (a long array of numbers)
    # sr = sample rate (how many samples per second, usually 22050)
    y, sr = librosa.load(file_path, duration=30)  # only use first 30 seconds

    # Step 2: Extract MFCCs
    # This gives us a 2D array: 20 rows (one per coefficient) x ~1300 columns (one per time frame)
    # We take the MEAN of each row to get a single number per coefficient
    # Result: 20 numbers
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    mfcc_means = np.mean(mfccs, axis=1)   # axis=1 means "average across time"

    # Step 3: Extract Tempo
    # Returns the BPM as a single number
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    # tempo comes back as an array in newer librosa, so we grab the first element
    tempo_value = float(np.atleast_1d(tempo)[0])

    # Step 4: Extract Energy (RMS)
    # rms gives a 2D array, we take the mean to get 1 number
    rms = librosa.feature.rms(y=y)
    energy = float(np.mean(rms))

    # Step 5: Extract Spectral Centroid
    # Same pattern — 2D array, take the mean
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    centroid_mean = float(np.mean(centroid))

    # Combine everything into one flat list of numbers
    # mfcc_means is already an array of 20 numbers
    # we add tempo, energy, centroid as individual numbers
    features = list(mfcc_means) + [tempo_value, energy, centroid_mean]
    # Total: 23 numbers

    return features


# --- Now run this on every song in our dataset ---

if __name__ == "__main__":
    # --- Now run this on every song in our dataset ---

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